import csv
import sys
from pathlib import Path

import pytest

# Damit "import doener" auch aus dem Ordner tests heraus funktioniert
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from doener import logik, speicher
from doener.modelle import Bewertung, Laden


def laden_mit(name, stadt, preis, *noten_liste):
    laden = Laden(name, stadt, preis)
    for fleisch, sosse, gemuese in noten_liste:
        laden.bewertung_hinzufuegen(
            Bewertung({"Fleisch": fleisch, "Soße": sosse, "Gemüse": gemuese})
        )
    return laden


# ---------------------------------------------------------------- Modelle

def test_bewertung_durchschnitt():
    assert Bewertung({"Fleisch": 8, "Soße": 6, "Gemüse": 4}).durchschnitt() == 6


def test_ungueltige_note_wird_abgelehnt():
    with pytest.raises(ValueError):
        Bewertung({"Fleisch": 11, "Soße": 5, "Gemüse": 5})
    with pytest.raises(ValueError):
        Bewertung({"Fleisch": 0, "Soße": 5, "Gemüse": 5})


def test_fehlendes_kriterium_wird_abgelehnt():
    with pytest.raises(ValueError):
        Bewertung({"Fleisch": 5, "Soße": 5})


def test_laden_ohne_name_oder_mit_falschem_preis():
    with pytest.raises(ValueError):
        Laden("", "Stuttgart")
    with pytest.raises(ValueError):
        Laden("A", "Stuttgart", preis=0)


def test_gesamtnote_und_kriteriumnote():
    laden = laden_mit("A", "Stuttgart", 6.0, (8, 6, 4), (10, 8, 6))
    assert laden.gesamtnote() == 7
    assert laden.kriterium_note("Fleisch") == 9


def test_laden_ohne_bewertung_hat_keine_note():
    laden = Laden("A", "Stuttgart", 6.0)
    assert laden.gesamtnote() is None
    assert laden.preis_leistung() is None


def test_preis_leistung():
    laden = laden_mit("A", "Stuttgart", 5.0, (8, 8, 8))
    assert laden.preis_leistung() == pytest.approx(1.6)


def test_preis_leistung_ohne_preis():
    laden = laden_mit("A", "Stuttgart", None, (8, 8, 8))
    assert laden.preis_leistung() is None


# ---------------------------------------------------------------- Logik

def test_ranking_sortiert_absteigend_und_ignoriert_unbewertete():
    schlecht = laden_mit("Schlecht", "Stuttgart", 6.0, (3, 3, 3))
    gut = laden_mit("Gut", "Stuttgart", 6.0, (9, 9, 9))
    ohne = Laden("Ohne", "Stuttgart")
    liste = logik.ranking([schlecht, ohne, gut])
    assert [laden.name for laden, wert in liste] == ["Gut", "Schlecht"]


def test_ranking_nach_stadt_und_kriterium():
    a = laden_mit("A", "Stuttgart", 6.0, (9, 1, 5))
    b = laden_mit("B", "Stuttgart", 6.0, (2, 9, 5))
    c = laden_mit("C", "Ludwigsburg", 6.0, (10, 10, 10))
    liste = logik.ranking([a, b, c], stadt="stuttgart", kriterium="Soße")
    assert [laden.name for laden, wert in liste] == ["B", "A"]


def test_ranking_nach_preis_leistung():
    teuer = laden_mit("Teuer", "Stuttgart", 10.0, (9, 9, 9))
    guenstig = laden_mit("Günstig", "Stuttgart", 5.0, (7, 7, 7))
    ohne_preis = laden_mit("OhnePreis", "Stuttgart", None, (10, 10, 10))
    liste = logik.ranking([teuer, guenstig, ohne_preis], nach_preis_leistung=True)
    assert [laden.name for laden, wert in liste] == ["Günstig", "Teuer"]


def test_laden_finden_und_suchen():
    laeden = [Laden("Beispiel Döner", "Stuttgart"), Laden("Kebap Haus", "Ludwigsburg")]
    assert logik.laden_finden(laeden, "beispiel döner") is laeden[0]
    assert logik.laden_finden(laeden, "gibt es nicht") is None
    assert logik.laeden_suchen(laeden, "ludwigs") == [laeden[1]]
    assert len(logik.laeden_suchen(laeden, "")) == 2


def test_staedte_ohne_doppelte():
    laeden = [Laden("A", "Stuttgart"), Laden("B", "Stuttgart"), Laden("C", "Aalen")]
    assert logik.staedte(laeden) == ["Aalen", "Stuttgart"]


def test_laden_loeschen():
    a, b = Laden("A", "Stuttgart"), Laden("B", "Stuttgart")
    laeden = [a, b]
    logik.laden_loeschen(laeden, a)
    assert laeden == [b]


def test_statistik():
    a = laden_mit("A", "Stuttgart", 6.0, (9, 5, 5))
    b = laden_mit("B", "Stuttgart", 8.0, (5, 9, 5), (5, 9, 5))
    werte = logik.statistik([a, b])
    assert werte["anzahl_laeden"] == 2
    assert werte["anzahl_bewertungen"] == 3
    assert werte["durchschnittspreis"] == 7.0
    assert werte["beste_pro_kriterium"]["Fleisch"][0] is a
    assert werte["beste_pro_kriterium"]["Soße"][0] is b


def test_statistik_ohne_daten():
    werte = logik.statistik([])
    assert werte["anzahl_laeden"] == 0
    assert werte["durchschnittspreis"] is None
    assert werte["beste_preis_leistung"] is None


# ---------------------------------------------------------------- Speichern

def test_speichern_und_laden(tmp_path):
    pfad = tmp_path / "test.json"
    laden = laden_mit("A", "Stuttgart", 6.5, (8, 7, 6))
    laden.bewertungen[0].kommentar = "Lecker"
    speicher.laeden_speichern([laden], pfad)

    geladen = speicher.laeden_laden(pfad)
    assert len(geladen) == 1
    assert geladen[0].name == "A"
    assert geladen[0].preis == 6.5
    assert geladen[0].bewertungen[0].kommentar == "Lecker"
    assert geladen[0].gesamtnote() == laden.gesamtnote()


def test_fehlende_datei_ergibt_leere_liste(tmp_path):
    assert speicher.laeden_laden(tmp_path / "gibt_es_nicht.json") == []


def test_beschaedigte_datei_loest_fehler_aus(tmp_path):
    pfad = tmp_path / "kaputt.json"
    pfad.write_text("das ist kein json", encoding="utf-8")
    with pytest.raises(ValueError):
        speicher.laeden_laden(pfad)
    assert pfad.read_text(encoding="utf-8") == "das ist kein json"  # nichts überschrieben


def test_mitgelieferte_beispieldaten_sind_gueltig():
    laeden = speicher.laeden_laden()
    assert len(laeden) >= 1


def test_csv_export(tmp_path):
    a = laden_mit("A", "Stuttgart", 6.0, (9, 9, 9))
    pfad = tmp_path / "ranking.csv"
    speicher.ranking_als_csv(logik.ranking([a]), pfad)
    with open(pfad, encoding="utf-8-sig", newline="") as datei:
        zeilen = list(csv.reader(datei, delimiter=";"))
    assert zeilen[0][:3] == ["Platz", "Name", "Stadt"]
    assert zeilen[1][:3] == ["1", "A", "Stuttgart"]
    assert zeilen[1][-2] == "9.0"


def test_diagramm_wird_erzeugt(tmp_path):
    pytest.importorskip("matplotlib")
    from doener import diagramm

    a = laden_mit("A", "Stuttgart", 6.0, (9, 9, 9))
    b = laden_mit("B", "Stuttgart", 6.0, (5, 5, 5))
    pfad = tmp_path / "ranking.png"
    diagramm.ranking_diagramm(logik.ranking([a, b]), pfad, "Test")
    assert pfad.exists() and pfad.stat().st_size > 0
