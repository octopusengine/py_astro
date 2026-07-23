"""Datové sady těles zobrazovaných na hvězdné mapě."""

import ephem


PLANETS = (
    {
        "name": "Sun",
        "factory": ephem.Sun,
        "color": "orange",
        "size_multiplier": 20,
        "marker_label": None,
    },
    {
        "name": "Moon",
        "factory": ephem.Moon,
        "color": "blue",
        "size_multiplier": 12,
        "marker_label": None,
    },
    {
        "name": "Mars",
        "factory": ephem.Mars,
        "color": "red",
        "size_multiplier": 5,
        "marker_label": "M",
    },
    {
        "name": "Venus",
        "factory": ephem.Venus,
        "color": "yellow",
        "size_multiplier": 5,
        "marker_label": "V",
    },
    {
        "name": "Jupiter",
        "factory": ephem.Jupiter,
        "color": "green",
        "size_multiplier": 5,
        "marker_label": "J",
    },
    {
        "name": "Saturn",
        "factory": ephem.Saturn,
        "color": "black",
        "size_multiplier": 3,
        "marker_label": "S",
    },
)


BRIGHT_STARS = (
    "Sirius",
    "Canopus",
    "Alpha Centauri",
    "Arcturus",
    "Vega",
    "Capella",
    "Rigel",
    "Altair",
    "Betelgeuse",
)


CONSTELLATIONS = {
    "Ursa Major (Big Dipper)": ("Dubhe", "Merak", "Phecda", "Megrez", "Alioth", "Mizar", "Alkaid"),
    "Orion": ("Betelgeuse", "Bellatrix", "Mintaka", "Alnitak", "Saiph", "Rigel"),
    "Cassiopeia": ("Caph", "Schedar"),
    "Southern Cross (Crux)": ("Acrux", "Mimosa", "Gacrux"),
    "Leo": ("Regulus", "Algieba", "Denebola"),
    "Taurus": ("Aldebaran", "Elnath", "Alcyone"),
}
