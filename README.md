# Döner OS Lite 🥙

Ein Konsolenprogramm in Python, mit dem man Dönerläden nach **Fleisch, Soße und Gemüse** bewerten, vergleichen und ranken kann, auch nach **Preis-Leistung**. Alle Daten bleiben in einer Datei gespeichert.

Das ist die Lite-Version der Idee "Döner OS" (eine Bewertungsplattform für Dönerläden) und entstand als Prüfungsleistung im Modul Python.

## Das Problem

Wo es den besten Döner gibt, ist Geschmackssache und meist nur ein Gesamteindruck ("4,5 Sterne"). Döner OS Lite bewertet getrennt nach Fleisch, Soße und Gemüse, berücksichtigt den Preis und macht daraus Ranglisten, auch pro Stadt und pro Kriterium.

## Funktionen

- Läden anlegen (mit Stadt und optionalem Preis) und löschen
- Bewerten mit drei Noten (1 bis 10) und optionalem Kommentar
- Ranking nach Gesamtnote, einzelnem Kriterium oder Preis-Leistung, optional für eine Stadt
- Laden suchen und Details samt Kommentaren ansehen
- Statistik: Durchschnittspreis, bester Laden je Kriterium, bestes Preis-Leistungs-Verhältnis
- Export des Rankings als CSV (für Excel) und als Balkendiagramm (PNG)
- Automatisches Speichern nach jeder Aktion, Schutz vor beschädigten Dateien

## Starten

```bash
python main.py
```

Das Programm selbst braucht keine zusätzlichen Pakete (Python 3.10 oder neuer). Nur das Diagramm braucht `matplotlib`:

```bash
pip install -r requirements.txt
```

Beim ersten Start sind vier Beispiel-Läden geladen.

## Web-Version

Dieselbe Logik gibt es auch als Web-App im Browser (`app.py`, gebaut mit Streamlit):

```bash
pip install -r requirements.txt
streamlit run app.py
```

Danach öffnet sich die App unter http://localhost:8501.

Online läuft sie auf Render. Die Einstellungen dafür stehen in `render.yaml`, eingerichtet wird sie mit einem Klick:

[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy?repo=https://github.com/moritz2404/Doeneros-lite)

Hinweise zur Online-Version: Im kostenlosen Tarif schläft die App nach 15 Minuten ohne Besucher ein, der erste Aufruf danach dauert etwa eine Minute. Neue Bewertungen bleiben nur bis zum nächsten Neustart erhalten, weil Render keine dauerhafte Festplatte im Gratistarif bietet. Löschen ist online absichtlich nicht möglich, da jeder mit dem Link die App benutzen kann.

## Tests

```bash
pytest -q
```

## Projektaufbau

```
main.py              Konsolenversion: Menü, Eingaben und Ausgaben
app.py               Web-Version mit Streamlit (nutzt dieselben Module)
render.yaml          Einstellungen für das Hosting auf Render
doener/
  modelle.py         Klassen Bewertung und Laden mit Notenberechnung
  logik.py           Ranking, Suche, Statistik
  speicher.py        Speichern und Laden (JSON), Export als CSV
  diagramm.py        Balkendiagramm mit matplotlib
data/
  laeden.json        Gespeicherte Läden und Bewertungen
tests/
  test_doener.py     21 automatische Tests
```

Die Trennung ist Absicht: `logik.py` und `modelle.py` kennen keine Ein- und Ausgaben. Dadurch sind sie einfach zu testen und lassen sich ohne Änderung in eine Website übernehmen. Genau das zeigt `app.py`: Die Web-Version nutzt dieselben Module wie die Konsolenversion. Das ist der Weg von "Lite" zum echten Döner OS.

## Welche Python-Konzepte wo vorkommen

| Konzept | Wo im Code |
|---|---|
| Variablen, Konstanten, Datentypen | `KRITERIEN`, `MIN_NOTE`, `MAX_NOTE` in `modelle.py` |
| Listen und Mengen (`set`) | Liste der Läden, Liste der Bewertungen, `staedte()` in `logik.py` |
| Dictionaries | Noten einer Bewertung, Menü in `main.py`, Statistik in `logik.py` |
| Schleifen (`for`, `while`) | Durchschnittsberechnung, Menüschleife, Eingabewiederholung |
| Bedingungen (`if`, `elif`, `else`) | Menüauswahl, Filter nach Stadt, Notenprüfung |
| Funktionen mit Parametern und Rückgabe | `logik.py`, Hilfsfunktionen in `main.py` |
| Klassen, Objekte, Methoden | `Bewertung` und `Laden` in `modelle.py` |
| Fehlerbehandlung (`try`, `except`, `raise`) | `frage_zahl`, `frage_preis`, `laeden_laden` |
| Dateien (JSON, CSV) | `speicher.py` |
| Sortieren mit `sorted` und `lambda` | `ranking()` in `logik.py` |
| Funktionen als Werte | `MENUE`-Dictionary in `main.py` |
| Module, Importe, optionale Pakete | `from doener import logik`, `matplotlib` nur bei Bedarf |
| f-Strings und Formatierung | Tabellenausgabe in `ranking_anzeigen` |
| Automatische Tests | `tests/test_doener.py` mit `pytest` |

## Wie Gesamtnote und Preis-Leistung berechnet werden

- **Bewertung:** Durchschnitt ihrer drei Noten
- **Gesamtnote eines Ladens:** Durchschnitt aller seiner Bewertungen
- **Preis-Leistung:** Gesamtnote geteilt durch den Preis, also Notenpunkte pro Euro. Ein 7er-Döner für 5 Euro (1,40) schlägt damit einen 9er-Döner für 10 Euro (0,90).

Läden ohne Bewertung (oder bei Preis-Leistung ohne Preis) tauchen im Ranking nicht auf.

## Erklärhilfe für die Präsentation

1. **Idee:** Welches Problem löst das Programm, und warum Döner? (Abschnitt "Das Problem")
2. **Daten:** Ein Laden ist ein Objekt mit Bewertungen, jede Bewertung hat drei Noten (`modelle.py`).
3. **Rechnen:** Durchschnitte per Schleife, Ranking mit `sorted` (`logik.py`).
4. **Speichern:** Warum JSON, und was passiert bei einer kaputten Datei (`speicher.py`).
5. **Menü:** Das Dictionary mit Funktionen und die Eingabeprüfung (`main.py`).
6. **Qualität:** Live `pytest` ausführen.

## Datenschutz

Das Programm speichert nur Ladennamen, Städte, Preise, Noten und Kommentare, keine personenbezogenen Daten, und alles bleibt lokal in `data/laeden.json`. Die Web-Version wird bei Render in Frankfurt gehostet. Weil dort jeder Kommentare eintragen kann, sollte man keine Namen oder andere personenbezogenen Daten in Kommentare schreiben. Bei einer echten Online-Version mit Nutzerkonten wären zusätzlich Datenschutzerklärung, Impressum und ein Auftragsverarbeitungsvertrag mit dem Hoster nötig (DSGVO).

## Mögliche Erweiterungen

- Nutzerkonten mit Bewertungen einzelner Personen
- Daten aus einer Datenbank statt aus einer JSON-Datei
