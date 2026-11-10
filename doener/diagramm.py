"""Erzeugt aus einem Ranking ein Balkendiagramm als PNG-Datei.

matplotlib ist ein zusätzliches Paket (pip install matplotlib). Es wird erst in der
Funktion importiert, damit der Rest des Programms auch ohne matplotlib läuft.
"""

from pathlib import Path


def ranking_diagramm(liste, pfad, titel="Döner Ranking"):
    """Speichert ein waagerechtes Balkendiagramm. liste besteht aus Paaren (laden, wert)."""
    import matplotlib

    matplotlib.use("Agg")  # Nur in eine Datei zeichnen, kein Fenster öffnen
    import matplotlib.pyplot as plt

    namen = []
    werte = []
    for laden, wert in liste:
        namen.append(laden.name)
        werte.append(wert)

    # Listen umdrehen, damit der beste Laden im Diagramm oben steht
    namen.reverse()
    werte.reverse()

    pfad = Path(pfad)
    pfad.parent.mkdir(parents=True, exist_ok=True)

    figur, achse = plt.subplots(figsize=(8, 2 + 0.5 * len(namen)))
    balken = achse.barh(namen, werte, color="#c0392b")
    achse.bar_label(balken, fmt="%.2f", padding=3)
    achse.set_title(titel)
    achse.set_xlim(0, max(werte) * 1.15)
    figur.tight_layout()
    figur.savefig(pfad, dpi=150)
    plt.close(figur)
