"""Döner OS Lite: Konsolenprogramm zum Bewerten und Vergleichen von Dönerläden.

Start:  python main.py

Diese Datei ist nur für Menü, Eingaben und Ausgaben zuständig.
Gerechnet wird in doener/logik.py, gespeichert in doener/speicher.py.
"""

from pathlib import Path

from doener import logik, speicher
from doener.modelle import KRITERIEN, MAX_NOTE, MIN_NOTE, Bewertung, Laden

AUSGABE_ORDNER = Path(__file__).resolve().parent / "ausgabe"


# ---------------------------------------------------------------- Eingabe-Hilfen

def frage_zahl(text, minimum, maximum):
    """Fragt so lange nach, bis eine ganze Zahl im erlaubten Bereich eingegeben wurde."""
    while True:
        eingabe = input(text)
        try:
            zahl = int(eingabe)
        except ValueError:
            print("Bitte eine ganze Zahl eingeben.")
            continue
        if minimum <= zahl <= maximum:
            return zahl
        print(f"Die Zahl muss zwischen {minimum} und {maximum} liegen.")


def frage_preis(text):
    """Fragt einen Preis in Euro ab. Eine leere Eingabe bedeutet: Preis unbekannt (None)."""
    while True:
        eingabe = input(text).strip()
        if eingabe == "":
            return None
        try:
            # Deutsche Schreibweise erlauben: 6,50 wird zu 6.50
            preis = float(eingabe.replace(",", "."))
        except ValueError:
            print("Bitte eine Zahl eingeben, zum Beispiel 6,50.")
            continue
        if preis > 0:
            return preis
        print("Der Preis muss größer als 0 sein.")


def laden_waehlen(laeden):
    """Zeigt alle Läden nummeriert an und gibt den gewählten Laden zurück (oder None)."""
    if len(laeden) == 0:
        print("Noch keine Läden vorhanden. Bitte zuerst einen Laden hinzufügen.")
        return None
    for nummer, laden in enumerate(laeden, start=1):
        print(f"  {nummer}. {laden.name} ({laden.stadt})")
    auswahl = frage_zahl("Nummer des Ladens: ", 1, len(laeden))
    return laeden[auswahl - 1]


def text_note(note):
    """Formatiert eine Note für die Anzeige. Ohne Wert steht dort 'keine Bewertung'."""
    return "keine Bewertung" if note is None else f"{note:.1f}"


# ---------------------------------------------------------------- Menüpunkte

def laeden_anzeigen(laeden):
    """Alle Läden mit Preis, Anzahl der Bewertungen und Gesamtnote auflisten."""
    if len(laeden) == 0:
        print("Noch keine Läden vorhanden.")
        return
    for laden in laeden:
        preis = "Preis unbekannt" if laden.preis is None else f"{laden.preis:.2f} Euro"
        print(
            f"- {laden.name} ({laden.stadt}), {preis}, "
            f"{len(laden.bewertungen)} Bewertung(en), Note: {text_note(laden.gesamtnote())}"
        )


def laden_hinzufuegen(laeden):
    """Neuen Laden anlegen."""
    name = input("Name des Ladens: ")
    stadt = input("Stadt: ")
    preis = frage_preis("Preis eines Döners in Euro (Enter, wenn unbekannt): ")
    if logik.laden_finden(laeden, name) is not None:
        print("Diesen Laden gibt es schon.")
        return
    try:
        laeden.append(Laden(name, stadt, preis))
    except ValueError as fehler:
        print(fehler)
        return
    print(f"{name.strip()} wurde hinzugefügt.")


def laden_bewerten(laeden):
    """Eine Bewertung mit drei Noten und optionalem Kommentar abgeben."""
    laden = laden_waehlen(laeden)
    if laden is None:
        return
    noten = {}
    for kriterium in KRITERIEN:
        noten[kriterium] = frage_zahl(
            f"{kriterium} ({MIN_NOTE} bis {MAX_NOTE}): ", MIN_NOTE, MAX_NOTE
        )
    kommentar = input("Kommentar (optional): ")
    laden.bewertung_hinzufuegen(Bewertung(noten, kommentar))
    print("Danke für deine Bewertung!")


def ranking_waehlen(laeden):
    """Fragt Stadt und Sortierung ab und gibt (liste, titel) zurück."""
    vorhandene_staedte = logik.staedte(laeden)
    if len(vorhandene_staedte) > 0:
        print("Städte: " + ", ".join(vorhandene_staedte))
    stadt = input("Nur eine Stadt anzeigen? (Enter für alle): ").strip()
    stadt_filter = stadt if stadt != "" else None

    print("Sortieren nach:")
    print("  0: Gesamtnote")
    for nummer, kriterium in enumerate(KRITERIEN, start=1):
        print(f"  {nummer}: {kriterium}")
    nummer_preis_leistung = len(KRITERIEN) + 1
    print(f"  {nummer_preis_leistung}: Preis-Leistung (Notenpunkte pro Euro)")
    auswahl = frage_zahl("Auswahl: ", 0, nummer_preis_leistung)

    if auswahl == 0:
        liste = logik.ranking(laeden, stadt=stadt_filter)
        titel = "Ranking nach Gesamtnote"
    elif auswahl == nummer_preis_leistung:
        liste = logik.ranking(laeden, stadt=stadt_filter, nach_preis_leistung=True)
        titel = "Ranking nach Preis-Leistung"
    else:
        kriterium = KRITERIEN[auswahl - 1]
        liste = logik.ranking(laeden, stadt=stadt_filter, kriterium=kriterium)
        titel = f"Ranking nach {kriterium}"

    if stadt_filter is not None:
        titel += f" ({stadt_filter})"
    return liste, titel


def ranking_anzeigen(laeden):
    """Rangliste als Tabelle ausgeben."""
    liste, titel = ranking_waehlen(laeden)
    if len(liste) == 0:
        print("Keine passenden Läden mit Bewertung gefunden.")
        return
    print()
    print(titel)
    print("-" * len(titel))
    for platz, (laden, wert) in enumerate(liste, start=1):
        # :<26 bedeutet linksbündig auf 26 Zeichen, :>6.2f rechtsbündig mit 2 Nachkommastellen
        print(f"{platz:>2}. {laden.name:<26} {laden.stadt:<14} {wert:>6.2f}")


def laden_details(laeden):
    """Läden suchen und alle Einzelheiten samt Kommentaren anzeigen."""
    suchtext = input("Suchbegriff (Name oder Stadt, Enter für alle): ")
    treffer = logik.laeden_suchen(laeden, suchtext)
    if len(treffer) == 0:
        print("Keine Treffer.")
        return
    laden = laden_waehlen(treffer)
    print()
    print(f"{laden.name} ({laden.stadt})")
    print(f"Gesamtnote: {text_note(laden.gesamtnote())}")
    for kriterium in KRITERIEN:
        print(f"  {kriterium}: {text_note(laden.kriterium_note(kriterium))}")
    preis_leistung = laden.preis_leistung()
    if preis_leistung is not None:
        print(f"Preis-Leistung: {preis_leistung:.2f} Notenpunkte pro Euro")
    kommentare = [b for b in laden.bewertungen if b.kommentar != ""]
    if len(kommentare) > 0:
        print("Kommentare:")
        for bewertung in kommentare:
            print(f"  {bewertung.datum}: {bewertung.kommentar}")


def statistik_anzeigen(laeden):
    """Wichtige Kennzahlen auf einen Blick."""
    werte = logik.statistik(laeden)
    print(f"Läden: {werte['anzahl_laeden']}, Bewertungen: {werte['anzahl_bewertungen']}")
    if werte["durchschnittspreis"] is not None:
        print(f"Durchschnittspreis: {werte['durchschnittspreis']:.2f} Euro")
    print("Bester Laden je Kriterium:")
    for kriterium, eintrag in werte["beste_pro_kriterium"].items():
        if eintrag is None:
            print(f"  {kriterium}: noch keine Bewertungen")
        else:
            laden, note = eintrag
            print(f"  {kriterium}: {laden.name} ({note:.1f})")
    if werte["beste_preis_leistung"] is not None:
        laden, wert = werte["beste_preis_leistung"]
        print(f"Bestes Preis-Leistungs-Verhältnis: {laden.name} ({wert:.2f} Punkte pro Euro)")


def ranking_exportieren(laeden):
    """Ranking als CSV-Datei speichern (öffnet sich in Excel)."""
    liste, titel = ranking_waehlen(laeden)
    if len(liste) == 0:
        print("Nichts zu exportieren.")
        return
    pfad = AUSGABE_ORDNER / "ranking.csv"
    speicher.ranking_als_csv(liste, pfad)
    print(f"Gespeichert unter {pfad}")


def diagramm_erstellen(laeden):
    """Ranking als Balkendiagramm (PNG) speichern."""
    liste, titel = ranking_waehlen(laeden)
    if len(liste) == 0:
        print("Nichts darzustellen.")
        return
    try:
        from doener import diagramm
        pfad = AUSGABE_ORDNER / "ranking.png"
        diagramm.ranking_diagramm(liste, pfad, titel)
    except ImportError:
        print("Für das Diagramm wird matplotlib gebraucht: pip install matplotlib")
        return
    print(f"Diagramm gespeichert unter {pfad}")


def laden_loeschen(laeden):
    """Einen Laden nach Rückfrage löschen."""
    laden = laden_waehlen(laeden)
    if laden is None:
        return
    sicher = input(f"{laden.name} wirklich löschen? (j/n): ").strip().lower()
    if sicher == "j":
        logik.laden_loeschen(laeden, laden)
        print("Gelöscht.")
    else:
        print("Abgebrochen.")


# ---------------------------------------------------------------- Hauptmenü

# Ein Dictionary ordnet jeder Menünummer Beschriftung und Funktion zu.
# Funktionen sind in Python Werte wie alle anderen und lassen sich so speichern.
MENUE = {
    1: ("Läden anzeigen", laeden_anzeigen),
    2: ("Laden hinzufügen", laden_hinzufuegen),
    3: ("Laden bewerten", laden_bewerten),
    4: ("Ranking anzeigen", ranking_anzeigen),
    5: ("Laden suchen und Details ansehen", laden_details),
    6: ("Statistik", statistik_anzeigen),
    7: ("Ranking als CSV exportieren", ranking_exportieren),
    8: ("Ranking als Diagramm speichern", diagramm_erstellen),
    9: ("Laden löschen", laden_loeschen),
}


def menue():
    """Hauptschleife: zeigt das Menü, führt die gewählte Funktion aus und speichert danach."""
    try:
        laeden = speicher.laeden_laden()
    except ValueError as fehler:
        print(fehler)
        return

    print("Willkommen bei Döner OS Lite!")
    while True:
        print()
        for nummer, (beschriftung, _funktion) in MENUE.items():
            print(f"{nummer}: {beschriftung}")
        print("0: Beenden")
        auswahl = frage_zahl("Auswahl: ", 0, len(MENUE))

        if auswahl == 0:
            print("Bis zum nächsten Döner!")
            break

        _beschriftung, funktion = MENUE[auswahl]
        print()
        funktion(laeden)
        speicher.laeden_speichern(laeden)  # Nach jeder Aktion speichern, es geht nichts verloren


if __name__ == "__main__":
    menue()
