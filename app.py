"""Döner OS Lite als Web-App im Browser (mit Streamlit).

Start lokal:  streamlit run app.py
Online:       wird auf Render gehostet (siehe render.yaml)

Wichtig: Diese Datei rechnet nichts selbst. Sie nutzt genau dieselben Module
wie die Konsolenversion main.py (logik, speicher, modelle). Nur die Oberfläche
ist anders: Statt input und print gibt es Karten, Balken, Formulare und Diagramme.

Das Aussehen (Farben, Schatten, Rundungen) steht in assets/style.css,
das Farbschema in .streamlit/config.toml. So bleibt diese Datei übersichtlich.

So funktioniert Streamlit: Bei jedem Klick läuft diese Datei einmal komplett
von oben nach unten durch und baut die Seite neu auf.
"""

import html
import tempfile
from pathlib import Path

import altair as alt
import pandas as pd
import streamlit as st

from doener import logik, speicher
from doener.modelle import KRITERIEN, MAX_NOTE, MIN_NOTE, Bewertung, Laden

ICONS = {"Fleisch": "🥩", "Soße": "🌶️", "Gemüse": "🥬"}
SEITEN = ["🏆 Ranking", "⭐ Bewerten", "➕ Neuer Laden", "🔍 Details", "📊 Statistik"]
MEDAILLEN = ["🥇", "🥈", "🥉"]

st.set_page_config(
    page_title="Döner OS Lite", page_icon="🥙", layout="centered", initial_sidebar_state="collapsed"
)

# Das Stylesheet einlesen und in die Seite einbauen
css = (Path(__file__).parent / "assets" / "style.css").read_text(encoding="utf-8")
st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)

# Bei jedem Durchlauf frisch aus der JSON-Datei lesen, so sieht jeder den aktuellen Stand
laeden = speicher.laeden_laden()


# ---------------------------------------------------------------- Hilfsfunktionen

def speichern(meldung):
    """Speichert alle Läden, merkt sich eine Erfolgsmeldung und baut die Seite neu auf."""
    speicher.laeden_speichern(laeden)
    # session_state überlebt das Neuladen, so erscheint die Meldung nach dem Neuaufbau
    st.session_state["meldung"] = meldung
    st.rerun()


def sicher(text):
    """Macht Text ungefährlich für HTML. Besucher können Namen und Kommentare eintippen,
    daher darf nie ungeprüfter Text in HTML landen (Schutz vor eingeschleustem Code)."""
    return html.escape(str(text))


def zahl(wert, stellen=1):
    """Zahl mit deutschem Komma, ohne Wert steht dort ein Strich."""
    return "-" if wert is None else f"{wert:.{stellen}f}".replace(".", ",")


def farbe(anteil):
    """Balkenfarbe nach Güte: grün ab 80 Prozent, orange ab 60, sonst rot."""
    if anteil >= 0.8:
        return "#2E9E5B"
    if anteil >= 0.6:
        return "#F2A33A"
    return "#D9534F"


def balken(wert, maximum):
    """Ein Fortschrittsbalken als HTML. Die Breite ist wert geteilt durch maximum."""
    anteil = 0 if wert is None else min(wert / maximum, 1)
    return (
        f'<div class="spur"><div class="fuell" '
        f'style="width:{anteil * 100:.0f}%;background:{farbe(anteil)}"></div></div>'
    )


def preis_text(laden):
    """Preis für die Anzeige, zum Beispiel '6,50 €'."""
    return "Preis unbekannt" if laden.preis is None else f"{zahl(laden.preis, 2)} €"


def titel(text, untertitel=""):
    """Zwischenüberschrift mit optionaler Unterzeile."""
    st.markdown(f'<div class="titel">{text}</div>', unsafe_allow_html=True)
    if untertitel:
        st.markdown(f'<div class="untertitel">{untertitel}</div>', unsafe_allow_html=True)


def kennzahl(symbol, wert, text):
    """Eine Kennzahl-Karte (zum Beispiel '14 Läden')."""
    return (
        f'<div class="kpi"><div class="symbol">{symbol}</div>'
        f'<div class="zahl">{wert}</div><div class="text">{text}</div></div>'
    )


# ---------------------------------------------------------------- Kopfbereich

werte = logik.statistik(laeden)
chips = (
    f'<span class="chip">🏪 {werte["anzahl_laeden"]} Läden</span>'
    f'<span class="chip">⭐ {werte["anzahl_bewertungen"]} Bewertungen</span>'
)
if werte["durchschnittspreis"] is not None:
    chips += f'<span class="chip">💶 Ø {zahl(werte["durchschnittspreis"], 2)} €</span>'
st.markdown(
    '<div class="hero"><div class="logo">Bewertungsplattform</div><h1>Döner OS Lite</h1>'
    "<p>Welcher Döner ist wirklich der beste? Bewertet nach Fleisch, Soße und Gemüse, "
    f'mit Ranking und Preis-Leistung.</p><div class="chips">{chips}</div></div>',
    unsafe_allow_html=True,
)

if "meldung" in st.session_state:
    st.toast(st.session_state.pop("meldung"), icon="✅")  # pop: Meldung nur einmal anzeigen

# Navigation als Reiter oben. Wird das Feld abgewählt, kommt None zurück, dann Ranking.
seite = st.segmented_control(
    "Menü", SEITEN, default=SEITEN[0], selection_mode="single", label_visibility="collapsed"
) or SEITEN[0]


# ---------------------------------------------------------------- Ranking

if seite == SEITEN[0]:
    spalte1, spalte2 = st.columns(2)
    stadt = spalte1.selectbox("📍 Stadt", ["Alle Städte"] + logik.staedte(laeden))
    sortierung = spalte2.selectbox("🔀 Sortieren nach", ["Gesamtnote", *KRITERIEN, "Preis-Leistung"])

    # Die Auswahl in die Parameter von logik.ranking übersetzen
    stadt_filter = None if stadt == "Alle Städte" else stadt
    nach_pl = sortierung == "Preis-Leistung"
    if nach_pl:
        liste = logik.ranking(laeden, stadt=stadt_filter, nach_preis_leistung=True)
    elif sortierung in KRITERIEN:
        liste = logik.ranking(laeden, stadt=stadt_filter, kriterium=sortierung)
    else:
        liste = logik.ranking(laeden, stadt=stadt_filter)

    if not liste:
        st.info("Keine passenden Läden mit Bewertung gefunden.")
    else:
        # Bei Noten ist 10 das Maximum. Preis-Leistung hat keine feste Obergrenze,
        # dort ist der beste Laden der volle Balken.
        maximum = liste[0][1] if nach_pl else MAX_NOTE
        einheit = "Punkte pro Euro" if nach_pl else "von 10"
        titel(f"Rangliste nach {sortierung}", f"{len(liste)} bewertete Läden, beste zuerst")

        # Die ersten drei als Podium: Spalten nebeneinander
        podium = st.columns(3)
        for spalte, (laden, wert), medaille, klasse in zip(podium, liste[:3], MEDAILLEN, ["p1", "p2", "p3"]):
            spalte.markdown(
                f'<div class="podium {klasse}"><div class="medaille">{medaille}</div>'
                f'<div class="name">{sicher(laden.name)}</div>'
                f'<div class="meta">📍 {sicher(laden.stadt)} · {preis_text(laden)}</div>'
                f'<div class="zahl">{zahl(wert, 2 if nach_pl else 1)}</div>'
                f'<div class="einheit">{einheit}</div>{balken(wert, maximum)}</div>',
                unsafe_allow_html=True,
            )

        # Alle weiteren als Zeilen. start=4, weil Platz 1 bis 3 schon oben stehen.
        if len(liste) > 3:
            st.markdown('<div style="height:18px"></div>', unsafe_allow_html=True)
        for platz, (laden, wert) in enumerate(liste[3:], start=4):
            st.markdown(
                f'<div class="zeile"><div class="platz">{platz}</div>'
                f'<div class="info"><div class="name">{sicher(laden.name)}</div>'
                f'<div class="meta">📍 {sicher(laden.stadt)} · {preis_text(laden)} · '
                f'{len(laden.bewertungen)} Bewertungen</div></div>'
                f'<div class="wert"><div class="zahl">{zahl(wert, 2 if nach_pl else 1)}</div>'
                f"{balken(wert, maximum)}</div></div>",
                unsafe_allow_html=True,
            )

        # Diagramm und Export sind eingeklappt, damit die Seite übersichtlich bleibt
        tabelle = pd.DataFrame(
            [{"Laden": l.name, sortierung: round(w, 2)} for l, w in liste]
        )
        with st.expander("📈 Als Diagramm anzeigen"):
            diagramm = (
                alt.Chart(tabelle)
                .mark_bar(color="#C0392B", cornerRadiusEnd=8)
                .encode(x=alt.X(sortierung, title=sortierung), y=alt.Y("Laden", sort="-x", title=None))
            )
            st.altair_chart(diagramm, width="stretch")

        # CSV-Export: dieselbe Funktion wie in der Konsolenversion, nur als Download-Knopf
        with tempfile.TemporaryDirectory() as ordner:
            pfad = Path(ordner) / "ranking.csv"
            speicher.ranking_als_csv(liste, pfad)
            st.download_button("⬇️ Ranking als CSV (für Excel)", pfad.read_bytes(), "ranking.csv")


# ---------------------------------------------------------------- Bewerten

elif seite == SEITEN[1]:
    titel("Laden bewerten", "Drei Noten von 1 (schlecht) bis 10 (perfekt) und ein optionaler Kommentar.")
    if not laeden:
        st.info("Noch keine Läden vorhanden. Bitte zuerst einen Laden hinzufügen.")
    else:
        # Ein Formular schickt alle Eingaben erst beim Klick auf den Knopf ab
        with st.form("bewerten"):
            namen = [f"{laden.name} ({laden.stadt})" for laden in laeden]
            nummer = st.selectbox("Laden", range(len(laeden)), format_func=lambda i: namen[i])
            # Für jedes Kriterium ein Schieberegler von 1 bis 10
            noten = {k: st.slider(f"{ICONS[k]} {k}", MIN_NOTE, MAX_NOTE, 5) for k in KRITERIEN}
            kommentar = st.text_input("💬 Kommentar (optional)")
            if st.form_submit_button("Bewertung abgeben", type="primary"):
                laeden[nummer].bewertung_hinzufuegen(Bewertung(noten, kommentar))
                speichern("Danke für deine Bewertung!")


# ---------------------------------------------------------------- Hinzufügen

elif seite == SEITEN[2]:
    titel("Neuen Laden anlegen", "Fehlt dein Lieblingsladen? Trag ihn hier ein.")
    with st.form("hinzufuegen", clear_on_submit=True):
        name = st.text_input("🏪 Name des Ladens")
        stadt = st.text_input("📍 Stadt")
        preis = st.number_input(
            "💶 Preis eines Döners in Euro (leer lassen, wenn unbekannt)",
            min_value=0.5, max_value=50.0, value=None, step=0.5, format="%.2f",
        )
        if st.form_submit_button("Laden hinzufügen", type="primary"):
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

elif seite == SEITEN[3]:
    titel("Laden im Detail", "Such nach Name oder Stadt.")
    suchtext = st.text_input("🔍 Suchbegriff", label_visibility="collapsed", placeholder="Name oder Stadt")
    treffer = logik.laeden_suchen(laeden, suchtext)
    if not treffer:
        st.info("Keine Treffer.")
    else:
        laden = st.selectbox("Laden", treffer, format_func=lambda l: f"{l.name} ({l.stadt})")
        gesamt = laden.gesamtnote()
        anteil = 0 if gesamt is None else gesamt / MAX_NOTE

        # Kopfkarte mit Ring für die Gesamtnote und einem Balken pro Kriterium
        zeilen = ""
        for kriterium in KRITERIEN:
            note = laden.kriterium_note(kriterium)
            zeilen += (
                f'<div class="kriterium-zeile"><div class="bez">{ICONS[kriterium]} {kriterium}</div>'
                f'{balken(note, MAX_NOTE)}<div class="zahl">{zahl(note)}</div></div>'
            )
        preis_leistung = laden.preis_leistung()
        zusatz = "" if preis_leistung is None else f" · ⚖️ {zahl(preis_leistung, 2)} Punkte pro Euro"
        st.markdown(
            f'<div class="detail"><div class="kopf"><div><h2>{sicher(laden.name)}</h2>'
            f'<div class="meta">📍 {sicher(laden.stadt)} · {preis_text(laden)}{zusatz} · '
            f'{len(laden.bewertungen)} Bewertungen</div></div>'
            f'<div class="ring" style="--anteil:{anteil * 100:.0f};--farbe:{farbe(anteil)}">'
            f"<span>{zahl(gesamt)}</span></div></div>{zeilen}</div>",
            unsafe_allow_html=True,
        )

        kommentare = [b for b in laden.bewertungen if b.kommentar]
        if kommentare:
            titel("💬 Kommentare")
            for bewertung in kommentare:
                st.markdown(
                    f'<div class="blase"><div class="datum">{sicher(bewertung.datum)}</div>'
                    f'<div class="text">{sicher(bewertung.kommentar)}</div></div>',
                    unsafe_allow_html=True,
                )


# ---------------------------------------------------------------- Statistik

elif seite == SEITEN[4]:
    titel("Statistik auf einen Blick")
    karten = st.columns(3)
    karten[0].markdown(kennzahl("🏪", werte["anzahl_laeden"], "Läden"), unsafe_allow_html=True)
    karten[1].markdown(kennzahl("⭐", werte["anzahl_bewertungen"], "Bewertungen"), unsafe_allow_html=True)
    if werte["durchschnittspreis"] is not None:
        karten[2].markdown(
            kennzahl("💶", f"{zahl(werte['durchschnittspreis'], 2)} €", "Durchschnittspreis"),
            unsafe_allow_html=True,
        )

    titel("Die Besten", "Bester Laden je Kriterium und beim Preis-Leistungs-Verhältnis")
    sieger = st.columns(4)
    for spalte, (kriterium, eintrag) in zip(sieger, werte["beste_pro_kriterium"].items()):
        if eintrag is None:
            inhalt = '<div class="name">noch keine Bewertungen</div>'
        else:
            laden, note = eintrag  # Das Paar (laden, note) in zwei Variablen aufteilen
            inhalt = (
                f'<div class="name">{sicher(laden.name)}</div>'
                f'<div class="note">{zahl(note)} von 10</div>'
            )
        spalte.markdown(
            f'<div class="sieger"><div class="kriterium">{ICONS[kriterium]} {kriterium}</div>{inhalt}</div>',
            unsafe_allow_html=True,
        )
    if werte["beste_preis_leistung"] is None:
        inhalt = '<div class="name">noch keine Daten</div>'
    else:
        laden, wert = werte["beste_preis_leistung"]
        inhalt = (
            f'<div class="name">{sicher(laden.name)}</div>'
            f'<div class="note">{zahl(wert, 2)} Punkte pro Euro</div>'
        )
    sieger[3].markdown(
        f'<div class="sieger"><div class="kriterium">⚖️ Preis-Leistung</div>{inhalt}</div>',
        unsafe_allow_html=True,
    )

# Löschen gibt es in der Web-Version absichtlich nicht: Der Link ist öffentlich,
# sonst könnte jeder Besucher Läden entfernen. Löschen geht in der Konsolenversion.

st.markdown(
    '<div class="fuss">Gebaut mit Python und Streamlit · Alle Läden und Bewertungen sind Testdaten</div>',
    unsafe_allow_html=True,
)
