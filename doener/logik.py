"""Die Rechenlogik von Döner OS Lite.

Alle Funktionen in dieser Datei arbeiten nur mit Python-Grundtypen:
Ein Laden ist ein Dictionary, alle Läden zusammen sind eine Liste.

Beispiel für einen Laden:
    {
        "name": "Beispiel Döner Mitte",
        "stadt": "Stuttgart",
        "bewertungen": [
            {"Fleisch": 8, "Soße": 7, "Gemüse": 6},
            {"Fleisch": 9, "Soße": 8, "Gemüse": 7},
        ],
    }
"""

# Konstanten: Werte, die sich im Programm nie ändern.
KRITERIEN = ["Fleisch", "Soße", "Gemüse"]
MIN_NOTE = 1
MAX_NOTE = 10


def neuer_laden(name, stadt):
    """Erzeugt einen neuen Laden ohne Bewertungen."""
    return {"name": name.strip(), "stadt": stadt.strip(), "bewertungen": []}


def bewertung_hinzufuegen(laden, noten):
    """Fügt eine Bewertung hinzu, wenn alle Noten gültig sind.

    noten ist ein Dictionary wie {"Fleisch": 8, "Soße": 7, "Gemüse": 6}.
    Bei ungültigen Noten wird ein ValueError ausgelöst.
    """
    for kriterium in KRITERIEN:
        if kriterium not in noten:
            raise ValueError(f"Kriterium fehlt: {kriterium}")
        if not MIN_NOTE <= noten[kriterium] <= MAX_NOTE:
            raise ValueError(
                f"Die Note für {kriterium} muss zwischen {MIN_NOTE} und {MAX_NOTE} liegen."
            )
    laden["bewertungen"].append(noten)


def durchschnitt(zahlen):
    """Mittelwert einer Liste. Bei einer leeren Liste gibt es keinen Wert (None)."""
    if len(zahlen) == 0:
        return None
    return sum(zahlen) / len(zahlen)


def kriterium_note(laden, kriterium):
    """Durchschnittsnote eines Ladens für ein einzelnes Kriterium (z. B. nur Fleisch)."""
    einzelnoten = []
    for bewertung in laden["bewertungen"]:
        einzelnoten.append(bewertung[kriterium])
    return durchschnitt(einzelnoten)


def gesamtnote(laden):
    """Gesamtnote eines Ladens: Durchschnitt über alle Kriterien und alle Bewertungen."""
    alle_noten = []
    for bewertung in laden["bewertungen"]:
        for kriterium in KRITERIEN:
            alle_noten.append(bewertung[kriterium])
    return durchschnitt(alle_noten)


def ranking(laeden, stadt=None, kriterium=None):
    """Erstellt die Rangliste, beste Läden zuerst.

    stadt:     Wenn angegeben, werden nur Läden dieser Stadt berücksichtigt.
    kriterium: Wenn angegeben, zählt nur dieses Kriterium (z. B. "Soße"),
               sonst die Gesamtnote.

    Rückgabe: Liste aus Paaren (laden, note). Läden ohne Bewertung fehlen.
    """
    ergebnis = []
    for laden in laeden:
        if stadt is not None and laden["stadt"].lower() != stadt.lower():
            continue  # Laden aus einer anderen Stadt überspringen

        if kriterium is None:
            note = gesamtnote(laden)
        else:
            note = kriterium_note(laden, kriterium)

        if note is not None:
            ergebnis.append((laden, note))

    # sorted mit key: sortiert nach der Note (zweites Element des Paares), absteigend
    return sorted(ergebnis, key=lambda paar: paar[1], reverse=True)


def laden_finden(laeden, name):
    """Sucht einen Laden nach Namen (Groß und Kleinschreibung egal). Sonst None."""
    for laden in laeden:
        if laden["name"].lower() == name.strip().lower():
            return laden
    return None
