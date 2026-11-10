"""Speichern und Laden der Läden in einer JSON-Datei.

JSON ist ein Textformat, das Python direkt aus Listen und Dictionaries
erzeugen kann. So bleiben die Bewertungen nach dem Beenden erhalten.
"""

import json
from pathlib import Path

# Standardpfad: Ordner "data" neben der Datei main.py
STANDARD_PFAD = Path(__file__).resolve().parent.parent / "data" / "laeden.json"


def laeden_laden(pfad=STANDARD_PFAD):
    """Liest die Läden aus der Datei. Gibt es die Datei noch nicht, startet die Liste leer."""
    pfad = Path(pfad)
    if not pfad.exists():
        return []
    with open(pfad, "r", encoding="utf-8") as datei:
        return json.load(datei)


def laeden_speichern(laeden, pfad=STANDARD_PFAD):
    """Schreibt alle Läden in die Datei (der Ordner wird bei Bedarf angelegt)."""
    pfad = Path(pfad)
    pfad.parent.mkdir(parents=True, exist_ok=True)
    with open(pfad, "w", encoding="utf-8") as datei:
        json.dump(laeden, datei, ensure_ascii=False, indent=2)
