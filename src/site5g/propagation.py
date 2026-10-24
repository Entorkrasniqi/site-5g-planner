"""Radio propagation maths: how much signal survives the trip from antenna to phone.

    received power (dBm) = transmit power (dBm) + antenna gain (dBi) - path loss (dB)

PATH LOSS MODEL (simple, explainable, wall-aware)
    PL(d) = FSPL(1 m) + 10 * n * log10(d / 1 m) + sum of wall attenuations on the way

  * FSPL(1 m) is the free-space loss at 1 metre reference distance:
        FSPL(1 m) = 20*log10(4*pi*f/c)         (about 43.3 dB at 3.5 GHz)
  * n is the path-loss exponent. n = 2 is free space; indoors 2-3 is typical,
    higher if the rooms are full of furniture, machines or people.
  * Every wall the straight line from antenna to receiver crosses adds its
    attenuation (see materials.py).

WHAT THIS MODEL IGNORES (on purpose, to stay readable)
    reflections / diffraction / waveguiding in corridors, doors vs wall differences
    beyond what the geometry gives, floors/ceilings (single storey only), antenna
    patterns, shadow fading, interference between access points, people and furniture.
"""
from __future__ import annotations

import numpy as np

C = 299_792_458.0  # speed of light, m/s


def fspl_1m_db(freq_hz: float) -> float:
    """Free-space path loss at the 1 m reference distance."""
    return float(20.0 * np.log10(4.0 * np.pi * freq_hz / C))


def path_loss_db(distance_m: np.ndarray, freq_hz: float, exponent: float, wall_loss_db: np.ndarray | float = 0.0):
    """Path loss in dB. Distances below 1 m are clamped to 1 m (reference distance)."""
    d = np.maximum(np.asarray(distance_m, dtype=float), 1.0)
    return fspl_1m_db(freq_hz) + 10.0 * exponent * np.log10(d) + wall_loss_db


def wall_loss_db(ap_xy: np.ndarray, cells_xy: np.ndarray, wall_p0: np.ndarray, wall_p1: np.ndarray,
                 wall_att_db: np.ndarray) -> np.ndarray:
    """Total wall attenuation between one access point and many receiver points.

    For each receiver cell we draw the straight segment AP -> cell and test it against
    every wall centre-line. Each wall crossed adds that wall's attenuation.

    Segment intersection (vectorised): with s = cell - ap, r = wall_end - wall_start,
        t = cross(q - a, r) / cross(s, r)     position along the AP->cell segment
        u = cross(q - a, s) / cross(s, r)     position along the wall
    they intersect iff 0 <= t <= 1 and 0 <= u <= 1 (and the lines are not parallel).

    Shapes: ap_xy (2,), cells_xy (N, 2), wall_p0/p1 (W, 2), wall_att_db (W,)  ->  (N,)
    """
    if len(wall_att_db) == 0:
        return np.zeros(len(cells_xy))
    s = cells_xy - ap_xy                                   # (N, 2)
    r = wall_p1 - wall_p0                                  # (W, 2)
    qa = wall_p0 - ap_xy                                   # (W, 2)
    denom = s[:, None, 0] * r[None, :, 1] - s[:, None, 1] * r[None, :, 0]          # (N, W) cross(s, r)
    num_t = qa[None, :, 0] * r[None, :, 1] - qa[None, :, 1] * r[None, :, 0]        # (1, W) cross(q-a, r)
    num_u = qa[None, :, 0] * s[:, None, 1] - qa[None, :, 1] * s[:, None, 0]        # (N, W) cross(q-a, s)
    with np.errstate(divide="ignore", invalid="ignore"):
        t = num_t / denom
        u = num_u / denom
    hit = (np.abs(denom) > 1e-12) & (t >= 0.0) & (t <= 1.0) & (u >= 0.0) & (u <= 1.0)
    return hit @ wall_att_db
