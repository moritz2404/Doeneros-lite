"""Erzeugt aus einem Ranking ein Balkendiagramm als PNG-Datei.

matplotlib ist ein zusätzliches Paket (pip install matplotlib). Es wird erst in der
Funktion importiert, damit der Rest des Programms auch ohne matplotlib läuft.
"""

from pathlib import Path


def ranking_diagramm(liste, pfad, titel="Döner Ranking"):
    """Speichert ein waagerechtes Balkendiagramm als PNG.

    liste besteht aus Paaren (laden, wert), der beste Laden steht vorne.
    """
    import matplotlib

    matplotlib.use("Agg")  # Nur in eine Datei zeichnen, kein Fenster öffnen
    import matplotlib.pyplot as plt

    # matplotlib zeichnet waagerechte Balken von unten nach oben. Mit reversed()
    # drehen wir die Liste um, damit der beste Laden im Diagramm oben steht.
    namen = [laden.name for laden, _wert in reversed(liste)]
    werte = [wert for _laden, wert in reversed(liste)]

    pfad = Path(pfad)
    pfad.parent.mkdir(parents=True, exist_ok=True)

    # Die Höhe wächst mit der Anzahl der Läden, damit nichts gequetscht wird
    figur, achse = plt.subplots(figsize=(8, 2 + 0.5 * len(namen)))
    balken = achse.barh(namen, werte, color="#c0392b")
    achse.bar_label(balken, fmt="%.2f", padding=3)  # Wert direkt neben jeden Balken
    achse.set_title(titel)
    achse.set_xlim(0, max(werte) * 1.15)  # Etwas Platz rechts für die Beschriftung
    figur.tight_layout()
    figur.savefig(pfad, dpi=150)
    plt.close(figur)  # Speicher wieder freigeben
