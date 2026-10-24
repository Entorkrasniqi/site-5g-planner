"""Read walls and rooms out of an IFC (Industry Foundation Classes) building model.

IFC is the open file format of BIM (Building Information Modelling): architects and
engineers export their 3-D building models as .ifc files. An IFC file is a database of
objects - IfcWall, IfcSlab, IfcDoor, IfcSpace (a room), IfcBuildingStorey (a floor) ...
each with geometry, a material, and a place in the building hierarchy.

For radio planning we only need, per floor:
  * every WALL as a 2-D line segment, plus its thickness and MATERIAL
  * every SPACE (room) as a 2-D polygon, so we know where coverage is actually needed

HOW WALL GEOMETRY IS RECOVERED
  IFC stores geometry in many different ways (extrusions, boolean cuts, meshes...).
  Instead of parsing each, we ask ifcopenshell to triangulate every wall in WORLD
  coordinates, then fit a line segment to the points seen from above:
    1. take the (x, y) of all mesh vertices
    2. principal axis (PCA) = the wall's direction
    3. centre-line = from the smallest to the largest position along that axis,
       thickness  = spread across the axis.
  This works for straight walls (the vast majority). Curved or L-shaped walls are
  approximated by one straight segment - a documented limitation.
"""
from __future__ import annotations

from dataclasses import dataclass, field

import ifcopenshell
import ifcopenshell.geom
import ifcopenshell.util.element as ifc_element
import numpy as np
from shapely.geometry import Polygon
from shapely.ops import unary_union

from .materials import wall_attenuation


@dataclass
class Wall:
    guid: str
    name: str
    storey: str
    p0: np.ndarray               # (x, y) metres, centre-line start
    p1: np.ndarray               # (x, y) metres, centre-line end
    thickness: float             # metres
    materials: list[str]
    attenuation_db: float
    matched_keywords: list[str] = field(default_factory=list)

    @property
    def length(self) -> float:
        return float(np.linalg.norm(self.p1 - self.p0))


@dataclass
class Space:
    guid: str
    name: str
    storey: str
    polygon: Polygon


@dataclass
class Storey:
    name: str
    elevation: float
    walls: list[Wall]
    spaces: list[Space]


def _world_vertices(settings, element) -> np.ndarray:
    shape = ifcopenshell.geom.create_shape(settings, element)
    return np.array(shape.geometry.verts, dtype=float).reshape(-1, 3)


def _fit_segment(xy: np.ndarray) -> tuple[np.ndarray, np.ndarray, float]:
    """Fit a thick line segment to 2-D points: returns (p0, p1, thickness)."""
    centre = xy.mean(axis=0)
    # principal axis via the covariance matrix
    cov = np.cov((xy - centre).T)
    eigvals, eigvecs = np.linalg.eigh(cov)
    axis = eigvecs[:, int(np.argmax(eigvals))]
    normal = np.array([-axis[1], axis[0]])
    along = (xy - centre) @ axis
    across = (xy - centre) @ normal
    mid_across = 0.5 * (across.max() + across.min())
    p0 = centre + axis * along.min() + normal * mid_across
    p1 = centre + axis * along.max() + normal * mid_across
    return p0, p1, float(across.max() - across.min())


def _footprint(xy_tris: np.ndarray) -> Polygon:
    """Union of the mesh triangles seen from above = the room's floor polygon."""
    polys = []
    for tri in xy_tris:
        p = Polygon(tri)
        if p.is_valid and p.area > 1e-9:
            polys.append(p)
    merged = unary_union(polys)
    if merged.geom_type == "MultiPolygon":
        merged = max(merged.geoms, key=lambda g: g.area)
    return merged.simplify(0.01)


def load_ifc(path: str, materials_table: dict[str, float] | None = None) -> list[Storey]:
    """Load every building storey with its walls and rooms.

    Lengths are returned in metres. Elements that cannot be triangulated are skipped.
    """
    model = ifcopenshell.open(path)
    settings = ifcopenshell.geom.settings()
    settings.set("use-world-coords", True)

    storeys: dict[str, Storey] = {}

    def storey_of(element) -> Storey | None:
        container = ifc_element.get_container(element)
        # spaces are aggregated (not "contained") by their storey
        if container is None and getattr(element, "Decomposes", None):
            for rel in element.Decomposes:
                container = rel.RelatingObject
        while container is not None and not container.is_a("IfcBuildingStorey"):
            container = ifc_element.get_container(container)
        if container is None:
            return None
        key = container.GlobalId
        if key not in storeys:
            storeys[key] = Storey(container.Name or "Storey", float(container.Elevation or 0.0), [], [])
        return storeys[key]

    for wall in model.by_type("IfcWall"):
        st = storey_of(wall)
        if st is None:
            continue
        try:
            xyz = _world_vertices(settings, wall)
        except Exception:  # element without usable geometry
            continue
        p0, p1, thickness = _fit_segment(xyz[:, :2])
        names = [m.Name for m in ifc_element.get_materials(wall) if getattr(m, "Name", None)]
        att, matched = wall_attenuation(names, materials_table)
        st.walls.append(Wall(wall.GlobalId, wall.Name or "Wall", st.name, p0, p1, thickness, names, att, matched))

    for space in model.by_type("IfcSpace"):
        st = storey_of(space)
        if st is None:
            continue
        try:
            shape = ifcopenshell.geom.create_shape(settings, space)
        except Exception:
            continue
        verts = np.array(shape.geometry.verts, dtype=float).reshape(-1, 3)
        faces = np.array(shape.geometry.faces, dtype=int).reshape(-1, 3)
        tris = verts[faces][:, :, :2]
        st.spaces.append(Space(space.GlobalId, space.Name or "Space", st.name, _footprint(tris)))

    return sorted(storeys.values(), key=lambda s: s.elevation)
