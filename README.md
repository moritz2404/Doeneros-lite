# Döner OS Lite 🥙

Ein Konsolenprogramm in reinem Python, mit dem man Dönerläden nach **Fleisch, Soße und Gemüse** bewerten und ein **Ranking** erstellen kann. Die Bewertungen bleiben in einer Datei gespeichert.

Das ist die Lite-Version der Idee "Döner OS" (eine Bewertungsplattform für Dönerläden) und entstand als Prüfungsleistung im Modul Python.

## Das Problem

Wo es den besten Döner gibt, ist Geschmackssache und meist nur ein Gesamteindruck ("4,5 Sterne"). Döner OS Lite bewertet getrennt nach Fleisch, Soße und Gemüse und macht daraus Ranglisten, auch pro Stadt und pro Kriterium.

## Starten

```bash
python main.py
```

Es werden keine zusätzlichen Pakete gebraucht (Python 3.10 oder neuer). Beim ersten Start sind drei Beispiel-Läden geladen.

## Tests

```bash
pip install -r requirements.txt
pytest -q
```

## Projektaufbau

```
main.py              Menü und Eingaben (alles, was mit dem Nutzer zu tun hat)
doener/
  logik.py           Rechenlogik: Bewerten, Durchschnitt, Ranking, Suche
  speicher.py        Speichern und Laden als JSON
data/
  laeden.json        Gespeicherte Läden und Bewertungen
tests/
  test_logik.py      Automatische Tests
```

Die Trennung ist Absicht: `logik.py` kennt keine Eingaben und Ausgaben, deshalb lässt sie sich einfach testen und später in eine App oder Website übernehmen.

## Welche Python-Basics wo vorkommen

| Konzept | Wo im Code |
|---|---|
| Variablen, Konstanten, Datentypen | `KRITERIEN`, `MIN_NOTE`, `MAX_NOTE` in `logik.py` |
| Listen | Liste aller Läden, Liste der Bewertungen pro Laden |
| Dictionaries | Ein Laden und eine Bewertung sind je ein Dictionary |
| Schleifen (`for`, `while`) | Durchschnitt über Bewertungen, Menüschleife in `main.py` |
| Bedingungen (`if`, `elif`, `else`) | Menüauswahl, Filter nach Stadt, Notenprüfung |
| Funktionen mit Parametern und Rückgabe | alle Funktionen in `logik.py` |
| Fehlerbehandlung (`try`, `except`, `raise`) | `frage_zahl` in `main.py`, `bewertung_hinzufuegen` in `logik.py` |
| Dateien lesen und schreiben (JSON) | `speicher.py` |
| Sortieren mit `sorted` und `lambda` | `ranking` in `logik.py` |
| Module und Importe | `from doener import logik, speicher` |
| f-Strings und Formatierung | Ausgaben in `main.py` |
| Tests | `tests/test_logik.py` |

## Wie die Gesamtnote berechnet wird

Alle Noten (1 bis 10) aller Bewertungen und aller drei Kriterien werden zusammen gemittelt. Läden ohne Bewertung tauchen im Ranking nicht auf. Im Ranking kann man auch nur nach einem Kriterium sortieren, etwa "Wer hat die beste Soße?".

## Datenschutz

Das Programm speichert nur Ladennamen, Städte und Noten, keine personenbezogenen Daten, und alles bleibt lokal in `data/laeden.json`. Bei einer echten Online-Version mit Nutzerkonten wäre die DSGVO zu beachten.

## Mögliche Erweiterungen

- Preis pro Döner erfassen und ein Preis-Leistungs-Ranking berechnen
- Kommentare zu Bewertungen
- Eine Klasse `Laden` statt Dictionaries
- Eine Weboberfläche (zum Beispiel mit Streamlit oder Flask)
