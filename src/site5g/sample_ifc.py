"""Generate a small, fully synthetic office floor as an IFC file.

Purpose: let anyone try the planner without owning a BIM model. The layout is invented
(36 m x 20 m, one corridor, offices, a concrete core, two glass-fronted meeting rooms).

     y=20 +-----------+-----------+-----------+-----------+
          |  Meeting  |  North 2  |  North 3  |  Meeting  |   north row
          |  North 1  |           |           |  North 4  |
     y=11.5 ===g==========g=========g==========g==========g====   corridor wall (doorway gaps)
          |                  Corridor (y 8.5 - 11.5)       |
     y=8.5 ====g=========g==========##########===g=========g==
          | South 1 | South 2 |  CORE   | South 3 | South 4 |   south row
     y=0  +---------+---------+---------+---------+---------+
          x=0       7        14        22        29        36

Walls: exterior = concrete 0.30 m, core = concrete 0.25 m, partitions = gypsum 0.10 m,
glass fronts of the two meeting rooms = glass 0.02 m. Doorways are 1 m gaps (no door objects).
"""
from __future__ import annotations

import numpy as np

import ifcopenshell
import ifcopenshell.api.aggregate
import ifcopenshell.api.context
import ifcopenshell.api.geometry
import ifcopenshell.api.material
import ifcopenshell.api.project
import ifcopenshell.api.root
import ifcopenshell.api.spatial
import ifcopenshell.api.unit

HEIGHT = 3.0


def _add_wall(f, ctx, storey, mats, name, p0, p1, thickness, material):
    p0, p1 = np.asarray(p0, float), np.asarray(p1, float)
    length = float(np.linalg.norm(p1 - p0))
    theta = np.arctan2(p1[1] - p0[1], p1[0] - p0[0])
    c, s = np.cos(theta), np.sin(theta)
    # wall geometry occupies local y in [0, thickness]; shift so the centre-line is at p0->p1
    origin = p0 - (thickness / 2.0) * np.array([-s, c])
    matrix = np.array([[c, -s, 0, origin[0]], [s, c, 0, origin[1]], [0, 0, 1, 0], [0, 0, 0, 1]])
    wall = ifcopenshell.api.root.create_entity(f, ifc_class="IfcWall", name=name)
    rep = ifcopenshell.api.geometry.add_wall_representation(f, context=ctx, length=length, height=HEIGHT,
                                                            thickness=thickness)
    ifcopenshell.api.geometry.assign_representation(f, product=wall, representation=rep)
    ifcopenshell.api.geometry.edit_object_placement(f, product=wall, matrix=matrix)
    ifcopenshell.api.spatial.assign_container(f, products=[wall], relating_structure=storey)
    if material not in mats:
        mats[material] = ifcopenshell.api.material.add_material(f, name=material)
    ifcopenshell.api.material.assign_material(f, products=[wall], material=mats[material])


def _add_space(f, ctx, storey, name, x0, y0, x1, y1):
    space = ifcopenshell.api.root.create_entity(f, ifc_class="IfcSpace", name=name)
    rep = ifcopenshell.api.geometry.add_slab_representation(
        f, context=ctx, depth=HEIGHT, polyline=[(x0, y0), (x1, y0), (x1, y1), (x0, y1), (x0, y0)])
    ifcopenshell.api.geometry.assign_representation(f, product=space, representation=rep)
    ifcopenshell.api.aggregate.assign_object(f, products=[space], relating_object=storey)


def _wall_with_doorway(f, ctx, storey, mats, name, y, xa, xb, thickness, material, doorway=True):
    """Horizontal wall from xa to xb at height y, with a 1 m doorway in the middle."""
    if not doorway:
        _add_wall(f, ctx, storey, mats, name, (xa, y), (xb, y), thickness, material)
        return
    mid = 0.5 * (xa + xb)
    _add_wall(f, ctx, storey, mats, name + " (a)", (xa, y), (mid - 0.5, y), thickness, material)
    _add_wall(f, ctx, storey, mats, name + " (b)", (mid + 0.5, y), (xb, y), thickness, material)


def build_sample(path: str) -> None:
    f = ifcopenshell.api.project.create_file(version="IFC4")
    project = ifcopenshell.api.root.create_entity(f, ifc_class="IfcProject", name="Sample office")
    ifcopenshell.api.unit.assign_unit(f)
    model_ctx = ifcopenshell.api.context.add_context(f, context_type="Model")
    body = ifcopenshell.api.context.add_context(f, context_type="Model", context_identifier="Body",
                                                target_view="MODEL_VIEW", parent=model_ctx)
    site = ifcopenshell.api.root.create_entity(f, ifc_class="IfcSite", name="Site")
    building = ifcopenshell.api.root.create_entity(f, ifc_class="IfcBuilding", name="Sample office building")
    storey = ifcopenshell.api.root.create_entity(f, ifc_class="IfcBuildingStorey", name="Level 1")
    ifcopenshell.api.aggregate.assign_object(f, products=[site], relating_object=project)
    ifcopenshell.api.aggregate.assign_object(f, products=[building], relating_object=site)
    ifcopenshell.api.aggregate.assign_object(f, products=[storey], relating_object=building)
    mats: dict = {}
    W, H = 36.0, 20.0

    # exterior
    for name, a, b in [("Ext S", (0, 0), (W, 0)), ("Ext E", (W, 0), (W, H)),
                       ("Ext N", (W, H), (0, H)), ("Ext W", (0, H), (0, 0))]:
        _add_wall(f, body, storey, mats, name, a, b, 0.30, "Concrete")

    # south row: rooms [0,7] [7,14], core [14,22], rooms [22,29] [29,36]; y from 0 to 8.5
    for x in (7.0, 29.0):
        _add_wall(f, body, storey, mats, f"South partition x={x:g}", (x, 0), (x, 8.5), 0.10, "Gypsum board")
    for x in (14.0, 22.0):
        _add_wall(f, body, storey, mats, f"Core wall x={x:g}", (x, 0), (x, 8.5), 0.25, "Concrete")
    _add_wall(f, body, storey, mats, "Core wall y=8.5", (14, 8.5), (22, 8.5), 0.25, "Concrete")
    for i, (xa, xb) in enumerate([(0, 7), (7, 14), (22, 29), (29, 36)], start=1):
        _wall_with_doorway(f, body, storey, mats, f"South {i} corridor wall", 8.5, xa, xb, 0.10, "Gypsum board")

    # north row: rooms [0,9] [9,18] [18,27] [27,36]; y from 11.5 to 20
    for x in (9.0, 18.0, 27.0):
        _add_wall(f, body, storey, mats, f"North partition x={x:g}", (x, 11.5), (x, H), 0.10, "Gypsum board")
    for i, (xa, xb) in enumerate([(0, 9), (9, 18), (18, 27), (27, 36)], start=1):
        meeting = i in (1, 4)
        _wall_with_doorway(f, body, storey, mats, f"North {i} corridor wall", 11.5, xa, xb,
                           0.02 if meeting else 0.10, "Glass" if meeting else "Gypsum board")

    # rooms (IfcSpace)
    for i, (xa, xb) in enumerate([(0, 7), (7, 14)], start=1):
        _add_space(f, body, storey, f"South {i}", xa, 0.15, xb, 8.45)
    _add_space(f, body, storey, "Core", 14.15, 0.15, 21.85, 8.35)
    for i, (xa, xb) in enumerate([(22, 29), (29, 36)], start=3):
        _add_space(f, body, storey, f"South {i}", xa, 0.15, xb, 8.45)
    for i, (xa, xb) in enumerate([(0, 9), (9, 18), (18, 27), (27, 36)], start=1):
        _add_space(f, body, storey, "Meeting North 1" if i == 1 else "Meeting North 4" if i == 4 else f"North {i}",
                   xa, 11.55, xb, H - 0.15)
    _add_space(f, body, storey, "Corridor", 0.15, 8.55, W - 0.15, 11.45)

    f.write(path)


if __name__ == "__main__":
    import sys
    out = sys.argv[1] if len(sys.argv) > 1 else "sample_office.ifc"
    build_sample(out)
    print(f"wrote {out}")
