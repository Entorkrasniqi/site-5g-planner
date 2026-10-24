"""Radio attenuation of building materials.

A radio wave loses energy every time it passes through a wall. How much depends on the
material, its thickness, the frequency, and even on what is inside the wall (steel
reinforcement, metal studs, low-emissivity glass coatings).

!!! THE NUMBERS BELOW ARE ILLUSTRATIVE PLACEHOLDERS !!!
They are plausible orders of magnitude for roughly 3.5 GHz (a common 5G mid-band
frequency), chosen so the model behaves sensibly - NOT measured values. A real
project must replace them with measurements or values from a published survey for the
actual building and frequency. Pass your own table with `--materials my_table.json`.
"""
from __future__ import annotations

import json

# keyword (lower-case, matched as a substring of the IFC material name) -> dB per wall crossing
DEFAULT_ATTENUATION_DB: dict[str, float] = {
    "concrete": 12.0,
    "brick": 8.0,
    "gypsum": 3.0,
    "plasterboard": 3.0,
    "drywall": 3.0,
    "glass": 3.0,
    "wood": 3.0,
    "timber": 3.0,
    "steel": 20.0,
    "metal": 20.0,
}
UNKNOWN_DB = 6.0   # used when no keyword matches


def load_table(path: str | None) -> dict[str, float]:
    """Defaults, optionally overridden/extended by a JSON file {"keyword": dB, ...}."""
    table = dict(DEFAULT_ATTENUATION_DB)
    if path:
        with open(path) as f:
            table.update({k.lower(): float(v) for k, v in json.load(f).items()})
    return table


def wall_attenuation(material_names: list[str], table: dict[str, float] | None = None) -> tuple[float, list[str]]:
    """Total attenuation (dB) for ONE crossing of a wall made of the named materials.

    A layered wall lists several materials (e.g. "Gypsum" + "Concrete"). We add the
    attenuation of each *distinct* matched keyword. If nothing matches, UNKNOWN_DB is used.
    Returns (dB, matched_keywords).
    """
    table = table or DEFAULT_ATTENUATION_DB
    text = " ".join(material_names).lower()
    matched = [k for k in table if k in text]
    if not matched:
        return UNKNOWN_DB, []
    return float(sum(table[k] for k in matched)), matched
