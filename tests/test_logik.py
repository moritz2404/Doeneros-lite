import sys
from pathlib import Path

import pytest

# Damit "import doener" auch aus dem Ordner tests heraus funktioniert
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from doener import logik, speicher


def laden_mit(name, stadt, *noten_liste):
    laden = logik.neuer_laden(name, stadt)
    for fleisch, sosse, gemuese in noten_liste:
        logik.bewertung_hinzufuegen(
            laden, {"Fleisch": fleisch, "Soße": sosse, "Gemüse": gemuese}
        )
    return laden


def test_durchschnitt():
    assert logik.durchschnitt([2, 4, 6]) == 4
    assert logik.durchschnitt([]) is None


def test_gesamtnote():
    laden = laden_mit("A", "Stuttgart", (8, 6, 4))
    assert logik.gesamtnote(laden) == 6


def test_laden_ohne_bewertung_hat_keine_note():
    laden = logik.neuer_laden("A", "Stuttgart")
    assert logik.gesamtnote(laden) is None


def test_ungueltige_note_wird_abgelehnt():
    laden = logik.neuer_laden("A", "Stuttgart")
    with pytest.raises(ValueError):
        logik.bewertung_hinzufuegen(laden, {"Fleisch": 11, "Soße": 5, "Gemüse": 5})


def test_ranking_sortiert_absteigend():
    schlecht = laden_mit("Schlecht", "Stuttgart", (3, 3, 3))
    gut = laden_mit("Gut", "Stuttgart", (9, 9, 9))
    ohne = logik.neuer_laden("Ohne", "Stuttgart")
    liste = logik.ranking([schlecht, ohne, gut])
    assert [laden["name"] for laden, note in liste] == ["Gut", "Schlecht"]


def test_ranking_nach_stadt_und_kriterium():
    a = laden_mit("A", "Stuttgart", (9, 1, 5))
    b = laden_mit("B", "Stuttgart", (2, 9, 5))
    c = laden_mit("C", "Ludwigsburg", (10, 10, 10))
    liste = logik.ranking([a, b, c], stadt="stuttgart", kriterium="Soße")
    assert [laden["name"] for laden, note in liste] == ["B", "A"]


def test_laden_finden_ignoriert_gross_und_kleinschreibung():
    laeden = [logik.neuer_laden("Beispiel Döner", "Stuttgart")]
    assert logik.laden_finden(laeden, "beispiel döner") is laeden[0]
    assert logik.laden_finden(laeden, "gibt es nicht") is None


def test_speichern_und_laden(tmp_path):
    pfad = tmp_path / "test.json"
    laeden = [laden_mit("A", "Stuttgart", (8, 7, 6))]
    speicher.laeden_speichern(laeden, pfad)
    assert speicher.laeden_laden(pfad) == laeden


def test_fehlende_datei_ergibt_leere_liste(tmp_path):
    assert speicher.laeden_laden(tmp_path / "gibt_es_nicht.json") == []
