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
        if stadt is not None and laden.stadt.lower() != stadt.lower():
            continue  # Laden aus einer anderen Stadt überspringen

        if nach_preis_leistung:
            wert = laden.preis_leistung()
        elif kriterium is not None:
            wert = laden.kriterium_note(kriterium)
        else:
            wert = laden.gesamtnote()

        if wert is not None:
            ergebnis.append((laden, wert))

    # sorted mit key: sortiert nach dem Wert (zweites Element des Paares), absteigend
    return sorted(ergebnis, key=lambda paar: paar[1], reverse=True)


def laden_finden(laeden, name):
    """Sucht einen Laden nach exaktem Namen (Groß und Kleinschreibung egal). Sonst None."""
    for laden in laeden:
        if laden.name.lower() == name.strip().lower():
            return laden
    return None


def laeden_suchen(laeden, suchtext):
    """Alle Läden, in deren Name oder Stadt der Suchtext vorkommt."""
    suchtext = suchtext.strip().lower()
    treffer = []
    for laden in laeden:
        if suchtext in laden.name.lower() or suchtext in laden.stadt.lower():
            treffer.append(laden)
    return treffer


def staedte(laeden):
    """Alphabetische Liste aller vorkommenden Städte, jede nur einmal."""
    alle = set()  # Eine Menge (set) enthält jeden Wert höchstens einmal
    for laden in laeden:
        alle.add(laden.stadt)
    return sorted(alle)


def laden_loeschen(laeden, laden):
    """Entfernt einen Laden aus der Liste."""
    laeden.remove(laden)


def statistik(laeden):
    """Fasst die wichtigsten Kennzahlen in einem Dictionary zusammen."""
    anzahl_bewertungen = 0
    preise = []
    for laden in laeden:
        anzahl_bewertungen += len(laden.bewertungen)
        if laden.preis is not None:
            preise.append(laden.preis)

    # Bester Laden je Kriterium: erster Eintrag der jeweiligen Rangliste
    beste_pro_kriterium = {}
    for kriterium in KRITERIEN:
        liste = ranking(laeden, kriterium=kriterium)
        beste_pro_kriterium[kriterium] = liste[0] if len(liste) > 0 else None

    preis_leistung_liste = ranking(laeden, nach_preis_leistung=True)

    return {
        "anzahl_laeden": len(laeden),
        "anzahl_bewertungen": anzahl_bewertungen,
        "durchschnittspreis": durchschnitt(preise),
        "beste_pro_kriterium": beste_pro_kriterium,
        "beste_preis_leistung": preis_leistung_liste[0] if len(preis_leistung_liste) > 0 else None,
    }
