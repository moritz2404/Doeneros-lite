"""Die Datenmodelle von Döner OS Lite: Bewertung und Laden als Klassen.

Eine Klasse ist ein Bauplan für Objekte. Jedes Objekt bündelt Daten
(zum Beispiel Name und Stadt) und die Funktionen, die dazugehören
(zum Beispiel "berechne meine Gesamtnote"). Funktionen innerhalb einer
Klasse heißen Methoden.
"""

from datetime import date

# Konstanten: Werte, die sich im Programm nie ändern.
# Schreibt man sie groß, erkennt jeder sofort, dass man sie nicht verändern soll.
KRITERIEN = ["Fleisch", "Soße", "Gemüse"]
MIN_NOTE = 1
MAX_NOTE = 10


def durchschnitt(zahlen):
    """Berechnet den Mittelwert einer Liste von Zahlen.

    Bei einer leeren Liste gibt es keinen Mittelwert, dann kommt None zurück.
    So vermeiden wir eine Division durch 0.
    """
    # "not zahlen" ist True, wenn die Liste leer ist
    if not zahlen:
        return None
    return sum(zahlen) / len(zahlen)


class Bewertung:
    """Eine einzelne Bewertung: je eine Note pro Kriterium, ein Kommentar und das Datum."""

    def __init__(self, noten, kommentar="", datum=None):
        """Legt eine Bewertung an und prüft vorher, ob die Noten gültig sind.

        noten ist ein Dictionary wie {"Fleisch": 8, "Soße": 7, "Gemüse": 6}.
        Fehlt ein Kriterium oder liegt eine Note außerhalb von 1 bis 10,
        wird ein ValueError ausgelöst und die Bewertung gar nicht erst angelegt.
        """
        for kriterium in KRITERIEN:
            if kriterium not in noten:
                raise ValueError(f"Kriterium fehlt: {kriterium}")
            if not MIN_NOTE <= noten[kriterium] <= MAX_NOTE:
                raise ValueError(
                    f"Die Note für {kriterium} muss zwischen {MIN_NOTE} und {MAX_NOTE} liegen."
                )
        self.noten = noten
        self.kommentar = kommentar.strip()  # Leerzeichen am Anfang und Ende entfernen
        # Ohne Angabe wird das heutige Datum als Text gespeichert, z. B. "2026-11-10"
        self.datum = datum or date.today().isoformat()

    def durchschnitt(self):
        """Durchschnitt der drei Noten dieser einen Bewertung."""
        return durchschnitt([self.noten[kriterium] for kriterium in KRITERIEN])

    def zu_dict(self):
        """Wandelt die Bewertung in ein Dictionary um (für das Speichern als JSON)."""
        return {"noten": self.noten, "kommentar": self.kommentar, "datum": self.datum}


class Laden:
    """Ein Dönerladen mit Name, Stadt, optionalem Preis und allen Bewertungen."""

    def __init__(self, name, stadt, preis=None, bewertungen=None):
        """Legt einen Laden an und prüft Name, Stadt und Preis.

        Leerer Name, leere Stadt oder ein Preis von 0 oder weniger lösen einen ValueError aus.
        """
        if name.strip() == "" or stadt.strip() == "":
            raise ValueError("Name und Stadt dürfen nicht leer sein.")
        if preis is not None and preis <= 0:
            raise ValueError("Der Preis muss größer als 0 sein.")
        self.name = name.strip()
        self.stadt = stadt.strip()
        self.preis = preis  # Preis eines Döners in Euro oder None, wenn unbekannt
        # Wichtig: nicht "bewertungen=[]" als Standardwert schreiben, sonst würden sich
        # alle Läden dieselbe Liste teilen. Deshalb None und hier eine neue Liste.
        self.bewertungen = bewertungen if bewertungen is not None else []

    def bewertung_hinzufuegen(self, bewertung):
        """Hängt eine neue Bewertung an die Liste dieses Ladens an."""
        self.bewertungen.append(bewertung)

    def kriterium_note(self, kriterium):
        """Durchschnittsnote für ein einzelnes Kriterium (z. B. nur die Soße)."""
        # List Comprehension: sammelt aus jeder Bewertung die Note für dieses Kriterium
        return durchschnitt([bewertung.noten[kriterium] for bewertung in self.bewertungen])

    def gesamtnote(self):
        """Durchschnitt aller Bewertungen. Ohne Bewertung gibt es keine Note (None)."""
        return durchschnitt([bewertung.durchschnitt() for bewertung in self.bewertungen])

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
        return {
            "name": self.name,
            "stadt": self.stadt,
            "preis": self.preis,
            "bewertungen": [bewertung.zu_dict() for bewertung in self.bewertungen],
        }
