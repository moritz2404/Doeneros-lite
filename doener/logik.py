"""Die Rechenlogik von Döner OS Lite: Ranking, Suche und Statistik.

Diese Datei kennt keine Eingaben und Ausgaben (kein input, kein print).
Dadurch lässt sie sich einfach testen und später auch in einer App wiederverwenden.
"""

from .modelle import KRITERIEN, durchschnitt


def ranking(laeden, stadt=None, kriterium=None, nach_preis_leistung=False):
    """Erstellt die Rangliste, beste Läden zuerst.

    stadt:               Wenn angegeben, zählen nur Läden dieser Stadt.
    kriterium:           Wenn angegeben, zählt nur dieses Kriterium (z. B. "Soße").
    nach_preis_leistung: Wenn True, wird nach Notenpunkten pro Euro sortiert.
    Ohne Angaben zählt die Gesamtnote.

    Rückgabe: Liste aus Paaren (laden, wert). Läden ohne Wert fehlen in der Liste.
    """
    ergebnis = []
    for laden in laeden:
        # Groß und Kleinschreibung ignorieren, damit "stuttgart" auch "Stuttgart" findet
        if stadt is not None and laden.stadt.lower() != stadt.lower():
            continue  # Laden aus einer anderen Stadt überspringen

        # Je nach Wunsch einen anderen Wert für die Sortierung berechnen
        if nach_preis_leistung:
            wert = laden.preis_leistung()
        elif kriterium is not None:
            wert = laden.kriterium_note(kriterium)
        else:
            wert = laden.gesamtnote()

        if wert is not None:  # Läden ohne Bewertung oder ohne Preis weglassen
            ergebnis.append((laden, wert))

    # sorted mit key: sortiert nach dem Wert (zweites Element des Paares), absteigend
    return sorted(ergebnis, key=lambda paar: paar[1], reverse=True)


def laden_finden(laeden, name):
    """Sucht einen Laden nach exaktem Namen (Groß und Kleinschreibung egal). Sonst None."""
    gesucht = name.strip().lower()  # nur einmal umwandeln statt in jedem Durchlauf
    for laden in laeden:
        if laden.name.lower() == gesucht:
            return laden  # Treffer: Funktion sofort beenden
    return None


def laeden_suchen(laeden, suchtext):
    """Alle Läden, in deren Name oder Stadt der Suchtext vorkommt.

    Ein leerer Suchtext kommt in jedem Text vor, liefert also alle Läden.
    """
    suchtext = suchtext.strip().lower()
    return [
        laden for laden in laeden
        if suchtext in laden.name.lower() or suchtext in laden.stadt.lower()
    ]


def staedte(laeden):
    """Alphabetische Liste aller vorkommenden Städte, jede nur einmal."""
    # Die geschweiften Klammern erzeugen eine Menge (set): jeder Wert höchstens einmal
    return sorted({laden.stadt for laden in laeden})


def _erster_oder_none(liste):
    """Gibt den ersten Eintrag einer Liste zurück oder None, wenn sie leer ist."""
    return liste[0] if liste else None


def statistik(laeden):
    """Fasst die wichtigsten Kennzahlen in einem Dictionary zusammen.

    Enthalten sind Anzahl Läden und Bewertungen, Durchschnittspreis,
    bester Laden je Kriterium und bestes Preis-Leistungs-Verhältnis.
    """
    # sum() zählt die Bewertungen aller Läden zusammen
    anzahl_bewertungen = sum(len(laden.bewertungen) for laden in laeden)
    # Nur Läden mit bekanntem Preis zählen für den Durchschnittspreis
    preise = [laden.preis for laden in laeden if laden.preis is not None]

    # Bester Laden je Kriterium: erster Eintrag der jeweiligen Rangliste
    beste_pro_kriterium = {
        kriterium: _erster_oder_none(ranking(laeden, kriterium=kriterium))
        for kriterium in KRITERIEN
    }

    return {
        "anzahl_laeden": len(laeden),
        "anzahl_bewertungen": anzahl_bewertungen,
        "durchschnittspreis": durchschnitt(preise),
        "beste_pro_kriterium": beste_pro_kriterium,
        "beste_preis_leistung": _erster_oder_none(ranking(laeden, nach_preis_leistung=True)),
    }
