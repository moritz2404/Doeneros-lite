"""Speichern und Laden (JSON) sowie der Export des Rankings als CSV.

JSON ist ein Textformat, das Python direkt aus Listen und Dictionaries
erzeugen kann. So bleiben die Bewertungen nach dem Beenden erhalten.
"""

import csv
import json
from pathlib import Path

from .modelle import KRITERIEN, Bewertung, Laden

# Standardpfad: Ordner "data" neben der Datei main.py
STANDARD_PFAD = Path(__file__).resolve().parent.parent / "data" / "laeden.json"


def laden_aus_dict(daten):
    """Baut aus einem Dictionary (wie es in der JSON-Datei steht) wieder ein Laden-Objekt."""
    bewertungen = []
    for eintrag in daten["bewertungen"]:
        bewertungen.append(
            Bewertung(
                noten=eintrag["noten"],
                kommentar=eintrag.get("kommentar", ""),
                datum=eintrag.get("datum"),
            )
        )
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
        with open(pfad, "r", encoding="utf-8") as datei:
            rohdaten = json.load(datei)
        return [laden_aus_dict(eintrag) for eintrag in rohdaten]
    except (json.JSONDecodeError, KeyError, TypeError) as fehler:
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
        json.dump(rohdaten, datei, ensure_ascii=False, indent=2)


def _runden(wert, stellen=2):
    """Rundet einen Wert, lässt aber None (kein Wert vorhanden) unverändert."""
    return None if wert is None else round(wert, stellen)


def ranking_als_csv(liste, pfad):
    """Exportiert ein Ranking (Liste aus Paaren (laden, wert)) als CSV für Excel.

    Als Trennzeichen dient das Semikolon und als Kodierung utf-8-sig,
    damit Excel in Deutschland Umlaute und Spalten richtig anzeigt.
    """
    pfad = Path(pfad)
    pfad.parent.mkdir(parents=True, exist_ok=True)
    kopfzeile = ["Platz", "Name", "Stadt", "Preis in Euro", "Bewertungen"]
    kopfzeile += KRITERIEN
    kopfzeile += ["Gesamtnote", "Preis-Leistung"]

    with open(pfad, "w", encoding="utf-8-sig", newline="") as datei:
        schreiber = csv.writer(datei, delimiter=";")
        schreiber.writerow(kopfzeile)
        for platz, (laden, _wert) in enumerate(liste, start=1):
            zeile = [platz, laden.name, laden.stadt, laden.preis, len(laden.bewertungen)]
            for kriterium in KRITERIEN:
                zeile.append(_runden(laden.kriterium_note(kriterium)))
            zeile.append(_runden(laden.gesamtnote()))
            zeile.append(_runden(laden.preis_leistung()))
            schreiber.writerow(zeile)
