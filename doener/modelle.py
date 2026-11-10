"""Die Datenmodelle von Döner OS Lite: Bewertung und Laden als Klassen.

Eine Klasse ist ein Bauplan für Objekte. Jedes Objekt bündelt Daten
(zum Beispiel Name und Stadt) und die Funktionen, die dazugehören
(zum Beispiel "berechne meine Gesamtnote"). Funktionen innerhalb einer
Klasse heißen Methoden.
"""

from datetime import date

# Konstanten: Werte, die sich im Programm nie ändern.
KRITERIEN = ["Fleisch", "Soße", "Gemüse"]
MIN_NOTE = 1
MAX_NOTE = 10


def durchschnitt(zahlen):
    """Mittelwert einer Liste. Bei einer leeren Liste gibt es keinen Wert (None)."""
    if len(zahlen) == 0:
        return None
    return sum(zahlen) / len(zahlen)


class Bewertung:
    """Eine einzelne Bewertung: je eine Note pro Kriterium, ein Kommentar und das Datum."""

    def __init__(self, noten, kommentar="", datum=None):
        # noten ist ein Dictionary wie {"Fleisch": 8, "Soße": 7, "Gemüse": 6}
        for kriterium in KRITERIEN:
            if kriterium not in noten:
                raise ValueError(f"Kriterium fehlt: {kriterium}")
            if not MIN_NOTE <= noten[kriterium] <= MAX_NOTE:
                raise ValueError(
                    f"Die Note für {kriterium} muss zwischen {MIN_NOTE} und {MAX_NOTE} liegen."
                )
        self.noten = noten
        self.kommentar = kommentar.strip()
        # Ohne Angabe wird das heutige Datum als Text gespeichert, z. B. "2026-11-10"
        self.datum = datum if datum is not None else date.today().isoformat()

    def durchschnitt(self):
        """Durchschnitt der drei Noten dieser einen Bewertung."""
        return durchschnitt([self.noten[kriterium] for kriterium in KRITERIEN])

    def zu_dict(self):
        """Wandelt die Bewertung in ein Dictionary um (für das Speichern als JSON)."""
        return {"noten": self.noten, "kommentar": self.kommentar, "datum": self.datum}


class Laden:
    """Ein Dönerladen mit Name, Stadt, optionalem Preis und allen Bewertungen."""

    def __init__(self, name, stadt, preis=None, bewertungen=None):
        if name.strip() == "" or stadt.strip() == "":
            raise ValueError("Name und Stadt dürfen nicht leer sein.")
        if preis is not None and preis <= 0:
            raise ValueError("Der Preis muss größer als 0 sein.")
        self.name = name.strip()
        self.stadt = stadt.strip()
        self.preis = preis  # Preis eines Döners in Euro oder None, wenn unbekannt
        self.bewertungen = bewertungen if bewertungen is not None else []

    def bewertung_hinzufuegen(self, bewertung):
        self.bewertungen.append(bewertung)

    def kriterium_note(self, kriterium):
        """Durchschnittsnote für ein einzelnes Kriterium (z. B. nur die Soße)."""
        einzelnoten = []
        for bewertung in self.bewertungen:
            einzelnoten.append(bewertung.noten[kriterium])
        return durchschnitt(einzelnoten)

    def gesamtnote(self):
        """Durchschnitt aller Bewertungen. Ohne Bewertung gibt es keine Note (None)."""
        einzelwerte = []
        for bewertung in self.bewertungen:
            einzelwerte.append(bewertung.durchschnitt())
        return durchschnitt(einzelwerte)

    def preis_leistung(self):
        """Gesamtnote geteilt durch den Preis: wie viele Notenpunkte man pro Euro bekommt.

        Ohne Note oder ohne Preis lässt sich der Wert nicht berechnen (None).
        """
        note = self.gesamtnote()
        if note is None or self.preis is None:
            return None
        return note / self.preis

    def zu_dict(self):
        """Wandelt den Laden samt Bewertungen in ein Dictionary um (für JSON)."""
        bewertungen_als_dict = []
        for bewertung in self.bewertungen:
            bewertungen_als_dict.append(bewertung.zu_dict())
        return {
            "name": self.name,
            "stadt": self.stadt,
            "preis": self.preis,
            "bewertungen": bewertungen_als_dict,
        }
