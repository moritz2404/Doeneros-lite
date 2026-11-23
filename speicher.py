"""Speichern und Laden (JSON) sowie der Export des Rankings als CSV.

JSON ist ein Textformat, das Python direkt aus Listen und Dictionaries
erzeugen kann. So bleiben die Bewertungen nach dem Beenden erhalten.
"""

import csv
import json
from pathlib import Path

from .modelle import KRITERIEN, Bewertung, Laden

# Standardpfad: Ordner "data" neben der Datei main.py
# __file__ ist der Pfad dieser Datei, .parent.parent geht zwei Ordner nach oben
STANDARD_PFAD = Path(__file__).resolve().parent.parent / "data" / "laeden.json"


def laden_aus_dict(daten):
    """Baut aus einem Dictionary (wie es in der JSON-Datei steht) wieder ein Laden-Objekt.

    Das ist das Gegenstück zu Laden.zu_dict(). Mit .get() bekommen ältere Einträge
    ohne Kommentar, Datum oder Preis einfach einen Standardwert statt eines Fehlers.
    """
    bewertungen = [
        Bewertung(eintrag["noten"], eintrag.get("kommentar", ""), eintrag.get("datum"))
        for eintrag in daten["bewertungen"]
    ]
    return Laden(daten["name"], daten["stadt"], daten.get("preis"), bewertungen)


def laeden_laden(pfad=STANDARD_PFAD):
    """Liest alle Läden aus der Datei. Gibt es die Datei noch nicht, startet die Liste leer.

    Ist die Datei beschädigt, wird ein ValueError ausgelöst. Das Programm bricht dann lieber
    ab, als die Datei beim nächsten Speichern mit einer leeren Liste zu überschreiben.
    """
    pfad = Path(pfad)
    if not pfad.exists():
        return []
    try:
        # "with" schließt die Datei automatisch wieder, auch wenn ein Fehler passiert
        with open(pfad, "r", encoding="utf-8") as datei:
            rohdaten = json.load(datei)
        return [laden_aus_dict(eintrag) for eintrag in rohdaten]
    except (json.JSONDecodeError, KeyError, TypeError) as fehler:
        # Alle drei Fehlerarten bedeuten: Inhalt passt nicht zum erwarteten Aufbau
        raise ValueError(
            f"Die Datei {pfad.name} ist beschädigt ({fehler}). "
            "Bitte reparieren oder löschen, damit keine Daten überschrieben werden."
        ) from fehler


def laeden_speichern(laeden, pfad=STANDARD_PFAD):
    """Schreibt alle Läden in die Datei (der Ordner wird bei Bedarf angelegt)."""
    pfad = Path(pfad)
    pfad.parent.mkdir(parents=True, exist_ok=True)
    rohdaten = [laden.zu_dict() for laden in laeden]
    with open(pfad, "w", encoding="utf-8") as datei:
        # ensure_ascii=False lässt Umlaute lesbar, indent=2 rückt die Datei schön ein
        json.dump(rohdaten, datei, ensure_ascii=False, indent=2)


def _runden(wert, stellen=2):
    """Rundet einen Wert, lässt aber None (kein Wert vorhanden) unverändert.

    Der Unterstrich am Anfang zeigt: Diese Funktion ist nur für diese Datei gedacht.
    """
    return None if wert is None else round(wert, stellen)


def ranking_als_csv(liste, pfad):
    """Exportiert ein Ranking (Liste aus Paaren (laden, wert)) als CSV für Excel.

    Als Trennzeichen dient das Semikolon und als Kodierung utf-8-sig,
    damit Excel in Deutschland Umlaute und Spalten richtig anzeigt.
    """
    pfad = Path(pfad)
    pfad.parent.mkdir(parents=True, exist_ok=True)
    kopfzeile = ["Platz", "Name", "Stadt", "Preis in Euro", "Bewertungen", *KRITERIEN,
                 "Gesamtnote", "Preis-Leistung"]

    with open(pfad, "w", encoding="utf-8-sig", newline="") as datei:
        schreiber = csv.writer(datei, delimiter=";")
        schreiber.writerow(kopfzeile)
        # enumerate zählt mit, start=1 damit der beste Laden Platz 1 bekommt
        for platz, (laden, _wert) in enumerate(liste, start=1):
            zeile = [platz, laden.name, laden.stadt, laden.preis, len(laden.bewertungen)]
            zeile += [_runden(laden.kriterium_note(kriterium)) for kriterium in KRITERIEN]
            zeile += [_runden(laden.gesamtnote()), _runden(laden.preis_leistung())]
            schreiber.writerow(zeile)
