"""Döner OS Lite: Konsolenprogramm zum Bewerten und Vergleichen von Dönerläden.

Start:  python main.py
"""

from doener import logik, speicher


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


def laden_waehlen(laeden):
    """Zeigt alle Läden nummeriert an und gibt den gewählten Laden zurück (oder None)."""
    if len(laeden) == 0:
        print("Noch keine Läden vorhanden. Bitte zuerst einen Laden hinzufügen.")
        return None
    for nummer, laden in enumerate(laeden, start=1):
        print(f"  {nummer}. {laden['name']} ({laden['stadt']})")
    auswahl = frage_zahl("Nummer des Ladens: ", 1, len(laeden))
    return laeden[auswahl - 1]


def laeden_anzeigen(laeden):
    """Menüpunkt 1: Alle Läden mit Anzahl der Bewertungen auflisten."""
    if len(laeden) == 0:
        print("Noch keine Läden vorhanden.")
    for laden in laeden:
        anzahl = len(laden["bewertungen"])
        print(f"- {laden['name']} ({laden['stadt']}), {anzahl} Bewertung(en)")


def laden_hinzufuegen(laeden):
    """Menüpunkt 2: Neuen Laden anlegen."""
    name = input("Name des Ladens: ").strip()
    stadt = input("Stadt: ").strip()
    if name == "" or stadt == "":
        print("Name und Stadt dürfen nicht leer sein.")
        return
    if logik.laden_finden(laeden, name) is not None:
        print("Diesen Laden gibt es schon.")
        return
    laeden.append(logik.neuer_laden(name, stadt))
    print(f"{name} wurde hinzugefügt.")


def laden_bewerten(laeden):
    """Menüpunkt 3: Eine Bewertung für einen Laden abgeben."""
    laden = laden_waehlen(laeden)
    if laden is None:
        return
    noten = {}
    for kriterium in logik.KRITERIEN:
        noten[kriterium] = frage_zahl(
            f"{kriterium} ({logik.MIN_NOTE} bis {logik.MAX_NOTE}): ",
            logik.MIN_NOTE,
            logik.MAX_NOTE,
        )
    logik.bewertung_hinzufuegen(laden, noten)
    print("Danke für deine Bewertung!")


def ranking_anzeigen(laeden):
    """Menüpunkt 4: Rangliste, optional nach Stadt und Kriterium gefiltert."""
    stadt = input("Nur eine Stadt anzeigen? (Enter für alle): ").strip()
    print("Nach welchem Kriterium sortieren?")
    print("  0. Gesamtnote")
    for nummer, kriterium in enumerate(logik.KRITERIEN, start=1):
        print(f"  {nummer}. {kriterium}")
    auswahl = frage_zahl("Auswahl: ", 0, len(logik.KRITERIEN))

    kriterium = None if auswahl == 0 else logik.KRITERIEN[auswahl - 1]
    stadt_filter = stadt if stadt != "" else None

    liste = logik.ranking(laeden, stadt=stadt_filter, kriterium=kriterium)
    if len(liste) == 0:
        print("Keine bewerteten Läden für diese Auswahl.")
        return
    print()
    for platz, (laden, note) in enumerate(liste, start=1):
        print(f"{platz}. {laden['name']} ({laden['stadt']}): {note:.1f} von {logik.MAX_NOTE}")


def menue():
    """Hauptschleife: zeigt das Menü, bis der Nutzer beendet."""
    laeden = speicher.laeden_laden()
    print("Willkommen bei Döner OS Lite!")

    while True:
        print()
        print("1: Läden anzeigen")
        print("2: Laden hinzufügen")
        print("3: Laden bewerten")
        print("4: Ranking anzeigen")
        print("5: Speichern und beenden")
        auswahl = frage_zahl("Auswahl: ", 1, 5)

        if auswahl == 1:
            laeden_anzeigen(laeden)
        elif auswahl == 2:
            laden_hinzufuegen(laeden)
        elif auswahl == 3:
            laden_bewerten(laeden)
        elif auswahl == 4:
            ranking_anzeigen(laeden)
        else:
            speicher.laeden_speichern(laeden)
            print("Gespeichert. Bis zum nächsten Döner!")
            break


if __name__ == "__main__":
    menue()
