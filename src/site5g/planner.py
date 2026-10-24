"""Coverage map + greedy access-point (AP) placement.

PROBLEM
    Given the walls and rooms of one floor, where should the radio access points go so
    that (almost) every room has a usable signal, using as few APs as possible?

APPROACH (deliberately simple, so you can follow every line)
    1. Lay a grid of RECEIVER CELLS (default every 0.5 m) over the rooms.
    2. Lay a coarser grid of CANDIDATE AP POSITIONS (default every 2 m) inside the rooms.
    3. For every candidate, compute the received power at every cell (propagation.py).
    4. GREEDY SELECTION: repeatedly pick the candidate that newly covers the most cells
       (coverage = best-server power >= threshold), until BOTH goals are met - overall
       coverage >= target_coverage and every room >= min_room_coverage - or the AP budget
       is used up.

    Greedy "maximum coverage" is not guaranteed optimal - the problem is NP-hard - but it
    is a classic, has a known approximation guarantee (about 63 % of optimal for pure
    set-cover coverage), and works well in practice. Roadmap item P3 compares it with
    an exact solver on small cases.
"""
from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np
from shapely import contains_xy
from shapely.ops import unary_union

from .ifc_loader import Storey
from .propagation import path_loss_db, wall_loss_db


@dataclass
class PlanConfig:
    freq_ghz: float = 3.5
    tx_power_dbm: float = 23.0          # power at the antenna port + gain (EIRP-like), dBm
    path_loss_exponent: float = 3.0     # 2 = free space; ~3 stands in for a furnished office
    threshold_dbm: float = -70.0        # required received power. NOT literally 3GPP RSRP.
    target_coverage: float = 0.95       # fraction of ALL room area that must be covered ...
    min_room_coverage: float = 0.90     # ... AND each single room must reach at least this
    grid_m: float = 0.5                 # receiver cell size
    candidate_spacing_m: float = 2.0    # spacing of candidate AP positions
    max_aps: int = 10
    # rooms whose NAME contains one of these words are never used as AP positions
    # (you cannot mount an access point inside a lift shaft) but are still covered.
    exclude_ap_rooms: tuple[str, ...] = ("core", "shaft", "stair", "lift", "elevator")


@dataclass
class PlanResult:
    config: PlanConfig
    storey: str
    cells_xy: np.ndarray                # (N, 2) receiver cell centres
    best_dbm: np.ndarray                # (N,) best-server received power with the chosen APs
    aps_xy: list[tuple[float, float]]
    coverage_after_each_ap: list[float]
    room_coverage: dict[str, float] = field(default_factory=dict)

    @property
    def coverage(self) -> float:
        return float((self.best_dbm >= self.config.threshold_dbm).mean()) if len(self.best_dbm) else 0.0


def _grid_inside(polygon, step: float) -> np.ndarray:
    minx, miny, maxx, maxy = polygon.bounds
    xs = np.arange(minx + step / 2, maxx, step)
    ys = np.arange(miny + step / 2, maxy, step)
    gx, gy = np.meshgrid(xs, ys)
    pts = np.column_stack([gx.ravel(), gy.ravel()])
    inside = contains_xy(polygon, pts[:, 0], pts[:, 1])
    return pts[inside]


def coverage_area(storey: Storey):
    """The area where coverage is required: union of rooms, or the walls' convex hull."""
    if storey.spaces:
        return unary_union([s.polygon for s in storey.spaces])
    from shapely.geometry import MultiPoint
    pts = [tuple(p) for w in storey.walls for p in (w.p0, w.p1)]
    return MultiPoint(pts).convex_hull


def received_power_dbm(ap_xy, cells_xy, storey: Storey, cfg: PlanConfig) -> np.ndarray:
    """Received power at every cell from ONE access point at ap_xy."""
    ap = np.asarray(ap_xy, dtype=float)
    p0 = np.array([w.p0 for w in storey.walls]).reshape(-1, 2)
    p1 = np.array([w.p1 for w in storey.walls]).reshape(-1, 2)
    att = np.array([w.attenuation_db for w in storey.walls])
    d = np.linalg.norm(cells_xy - ap, axis=1)
    walls = wall_loss_db(ap, cells_xy, p0, p1, att)
    return cfg.tx_power_dbm - path_loss_db(d, cfg.freq_ghz * 1e9, cfg.path_loss_exponent, walls)


def plan_storey(storey: Storey, cfg: PlanConfig | None = None) -> PlanResult:
    cfg = cfg or PlanConfig()
    area = coverage_area(storey)
    cells = _grid_inside(area, cfg.grid_m)
    mountable = [sp.polygon for sp in storey.spaces
                 if not any(word in sp.name.lower() for word in cfg.exclude_ap_rooms)]
    candidates = _grid_inside(unary_union(mountable) if mountable else area, cfg.candidate_spacing_m)
    if len(cells) == 0 or len(candidates) == 0:
        raise ValueError("no area to cover: the storey has no rooms or walls")

    # Power matrix: one row per candidate AP, one column per cell.
    power = np.vstack([received_power_dbm(c, cells, storey, cfg) for c in candidates])

    best = np.full(len(cells), -np.inf)
    chosen: list[int] = []
    curve: list[float] = []
    floor_dbm = cfg.threshold_dbm - 20.0            # for the tie-break utility below
    room_masks = [contains_xy(sp.polygon, cells[:, 0], cells[:, 1]) for sp in storey.spaces]
    room_masks = [m for m in room_masks if m.any()]

    def goals_met(level) -> bool:
        ok = (level >= cfg.threshold_dbm).mean() >= cfg.target_coverage
        # an overall average can hide one badly served room, so check every room too
        return bool(ok and all((level[m] >= cfg.threshold_dbm).mean() >= cfg.min_room_coverage
                               for m in room_masks))

    def utility(level):                             # smooth score: 0 at floor, 20 at threshold, capped
        return np.clip(level - floor_dbm, 0.0, 20.0)

    while len(chosen) < cfg.max_aps:
        covered_now = best >= cfg.threshold_dbm
        new_best = np.maximum(best[None, :], power)                    # (A, N)
        gain = ((new_best >= cfg.threshold_dbm) & ~covered_now[None, :]).sum(axis=1)
        if gain.max() == 0:
            # No candidate covers a new cell. Fall back to the smooth utility so that
            # APs still move weak spots towards the threshold; stop if even that is flat.
            gain_u = (utility(new_best) - utility(best)[None, :]).sum(axis=1)
            if gain_u.max() <= 1e-9:
                break
            pick = int(np.argmax(gain_u))
        else:
            pick = int(np.argmax(gain))
        chosen.append(pick)
        best = new_best[pick]
        curve.append(float((best >= cfg.threshold_dbm).mean()))
        if goals_met(best):
            break

    result = PlanResult(cfg, storey.name, cells, best, [tuple(map(float, candidates[i])) for i in chosen], curve)
    for sp in storey.spaces:
        inside = contains_xy(sp.polygon, cells[:, 0], cells[:, 1])
        if inside.any():
            result.room_coverage[sp.name] = float((best[inside] >= cfg.threshold_dbm).mean())
    return result
