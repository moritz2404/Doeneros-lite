"""Döner OS Lite als Web-App im Browser (mit Streamlit).

Start lokal:  streamlit run app.py
Online:       wird auf Render gehostet (siehe render.yaml)

Wichtig: Diese Datei rechnet nichts selbst. Sie nutzt genau dieselben Module
wie die Konsolenversion main.py (logik, speicher, modelle). Nur die Oberfläche
ist anders: Statt input und print gibt es Formulare, Tabellen und Diagramme.

So funktioniert Streamlit: Bei jedem Klick läuft diese Datei einmal komplett
von oben nach unten durch und baut die Seite neu auf.
"""

import tempfile
from pathlib import Path

import altair as alt
import pandas as pd
import streamlit as st

from doener import logik, speicher
from doener.modelle import KRITERIEN, MAX_NOTE, MIN_NOTE, Bewertung, Laden

st.set_page_config(page_title="Döner OS Lite", page_icon="🥙")

# Bei jedem Durchlauf frisch aus der JSON-Datei lesen, so sieht jeder den aktuellen Stand
laeden = speicher.laeden_laden()


def speichern(meldung):
    """Speichert alle Läden, merkt sich eine Erfolgsmeldung und baut die Seite neu auf."""
    speicher.laeden_speichern(laeden)
    # session_state überlebt das Neuladen, so erscheint die Meldung nach dem Neuaufbau
    st.session_state["meldung"] = meldung
    st.rerun()


def note_als_text(note):
    """Wie text_note in main.py: Note mit einer Nachkommastelle oder "keine"."""
    return "keine" if note is None else f"{note:.1f}"


# ---------------------------------------------------------------- Kopf und Menü

st.title("🥙 Döner OS Lite")
st.caption("Dönerläden nach Fleisch, Soße und Gemüse bewerten und vergleichen.")

if "meldung" in st.session_state:
    st.success(st.session_state.pop("meldung"))  # pop: Meldung nur einmal anzeigen

seite = st.sidebar.radio(
    "Menü", ["Ranking", "Laden bewerten", "Laden hinzufügen", "Details", "Statistik"]
)


# ---------------------------------------------------------------- Ranking

if seite == "Ranking":
    spalte1, spalte2 = st.columns(2)
    stadt = spalte1.selectbox("Stadt", ["Alle Städte"] + logik.staedte(laeden))
    sortierung = spalte2.selectbox("Sortieren nach", ["Gesamtnote", *KRITERIEN, "Preis-Leistung"])

    # Die Auswahl in die Parameter von logik.ranking übersetzen
    stadt_filter = None if stadt == "Alle Städte" else stadt
    if sortierung == "Preis-Leistung":
        liste = logik.ranking(laeden, stadt=stadt_filter, nach_preis_leistung=True)
    elif sortierung in KRITERIEN:
        liste = logik.ranking(laeden, stadt=stadt_filter, kriterium=sortierung)
    else:
        liste = logik.ranking(laeden, stadt=stadt_filter)

    if not liste:
        st.info("Keine passenden Läden mit Bewertung gefunden.")
    else:
        # Aus den Paaren (laden, wert) eine Tabelle machen
        tabelle = pd.DataFrame(
            [
                {"Platz": platz, "Laden": laden.name, "Stadt": laden.stadt, sortierung: round(wert, 2)}
                for platz, (laden, wert) in enumerate(liste, start=1)
            ]
        )
        st.dataframe(tabelle, hide_index=True, width="stretch")

        # Balkendiagramm: sort="-x" stellt den besten Laden nach oben
        diagramm = (
            alt.Chart(tabelle)
            .mark_bar(color="#c0392b")
            .encode(x=alt.X(sortierung, title=sortierung), y=alt.Y("Laden", sort="-x", title=None))
        )
        st.altair_chart(diagramm, width="stretch")

        # CSV-Export: dieselbe Funktion wie in der Konsolenversion, nur als Download-Knopf
        with tempfile.TemporaryDirectory() as ordner:
            pfad = Path(ordner) / "ranking.csv"
            speicher.ranking_als_csv(liste, pfad)
            st.download_button("Ranking als CSV herunterladen", pfad.read_bytes(), "ranking.csv")


# ---------------------------------------------------------------- Bewerten

elif seite == "Laden bewerten":
    if not laeden:
        st.info("Noch keine Läden vorhanden. Bitte zuerst einen Laden hinzufügen.")
    else:
        # Ein Formular schickt alle Eingaben erst beim Klick auf den Knopf ab
        with st.form("bewerten"):
            namen = [f"{laden.name} ({laden.stadt})" for laden in laeden]
            nummer = st.selectbox("Laden", range(len(laeden)), format_func=lambda i: namen[i])
            # Für jedes Kriterium ein Schieberegler von 1 bis 10
            noten = {k: st.slider(k, MIN_NOTE, MAX_NOTE, 5) for k in KRITERIEN}
            kommentar = st.text_input("Kommentar (optional)")
            if st.form_submit_button("Bewertung abgeben"):
                laeden[nummer].bewertung_hinzufuegen(Bewertung(noten, kommentar))
                speichern("Danke für deine Bewertung!")


# ---------------------------------------------------------------- Hinzufügen

elif seite == "Laden hinzufügen":
    with st.form("hinzufuegen", clear_on_submit=True):
        name = st.text_input("Name des Ladens")
        stadt = st.text_input("Stadt")
        preis = st.number_input(
            "Preis eines Döners in Euro (leer lassen, wenn unbekannt)",
            min_value=0.5, max_value=50.0, value=None, step=0.5, format="%.2f",
        )
        if st.form_submit_button("Laden hinzufügen"):
            if logik.laden_finden(laeden, name) is not None:
                st.error("Diesen Laden gibt es schon.")
            else:
                try:
                    neuer_laden = Laden(name, stadt, preis)  # prüft Name, Stadt und Preis
                except ValueError as fehler:
                    st.error(str(fehler))
                else:  # else nach try: läuft nur, wenn kein Fehler aufgetreten ist
                    laeden.append(neuer_laden)
                    speichern(f"{neuer_laden.name} wurde hinzugefügt.")


# ---------------------------------------------------------------- Details

elif seite == "Details":
    suchtext = st.text_input("Suchbegriff (Name oder Stadt)")
    treffer = logik.laeden_suchen(laeden, suchtext)
    if not treffer:
        st.info("Keine Treffer.")
    else:
        laden = st.selectbox("Laden", treffer, format_func=lambda l: f"{l.name} ({l.stadt})")
        st.subheader(laden.name)
        spalten = st.columns(len(KRITERIEN) + 1)
        spalten[0].metric("Gesamtnote", note_als_text(laden.gesamtnote()))
        for spalte, kriterium in zip(spalten[1:], KRITERIEN):
            spalte.metric(kriterium, note_als_text(laden.kriterium_note(kriterium)))
        if laden.preis is not None:
            st.write(f"Preis: {laden.preis:.2f} Euro")
        if laden.preis_leistung() is not None:
            st.write(f"Preis-Leistung: {laden.preis_leistung():.2f} Notenpunkte pro Euro")
        kommentare = [b for b in laden.bewertungen if b.kommentar]
        if kommentare:
            st.write("**Kommentare**")
            for bewertung in kommentare:
                st.write(f"{bewertung.datum}: {bewertung.kommentar}")


# ---------------------------------------------------------------- Statistik

elif seite == "Statistik":
    werte = logik.statistik(laeden)
    spalte1, spalte2, spalte3 = st.columns(3)
    spalte1.metric("Läden", werte["anzahl_laeden"])
    spalte2.metric("Bewertungen", werte["anzahl_bewertungen"])
    if werte["durchschnittspreis"] is not None:
        spalte3.metric("Durchschnittspreis", f"{werte['durchschnittspreis']:.2f} €")

    st.write("**Bester Laden je Kriterium**")
    for kriterium, eintrag in werte["beste_pro_kriterium"].items():
        if eintrag is None:
            st.write(f"{kriterium}: noch keine Bewertungen")
        else:
            laden, note = eintrag
            st.write(f"{kriterium}: {laden.name} ({note:.1f})")
    if werte["beste_preis_leistung"] is not None:
        laden, wert = werte["beste_preis_leistung"]
        st.write(f"**Bestes Preis-Leistungs-Verhältnis:** {laden.name} ({wert:.2f} Punkte pro Euro)")

# Löschen gibt es in der Web-Version absichtlich nicht: Der Link ist öffentlich,
# sonst könnte jeder Besucher Läden entfernen. Löschen geht in der Konsolenversion.
