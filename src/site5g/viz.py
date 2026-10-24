"""Coverage heat-map figure: floor plan, signal strength, access points."""
from __future__ import annotations

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

from .ifc_loader import Storey  # noqa: E402
from .planner import PlanResult  # noqa: E402


def save_coverage_figure(path: str, storey: Storey, result: PlanResult, dpi: int = 100) -> None:
    cfg = result.config
    fig, ax = plt.subplots(figsize=(10, 6))

    # signal strength per receiver cell, drawn as a raster (cells lie on a regular grid)
    step = cfg.grid_m
    x0, y0 = result.cells_xy.min(axis=0) - step / 2
    ix = np.round((result.cells_xy[:, 0] - x0 - step / 2) / step).astype(int)
    iy = np.round((result.cells_xy[:, 1] - y0 - step / 2) / step).astype(int)
    raster = np.full((iy.max() + 1, ix.max() + 1), np.nan)
    raster[iy, ix] = result.best_dbm
    im = ax.imshow(raster, origin="lower", cmap="RdYlGn", vmin=cfg.threshold_dbm - 30, vmax=cfg.threshold_dbm + 25,
                   extent=(x0, x0 + raster.shape[1] * step, y0, y0 + raster.shape[0] * step), interpolation="nearest")
    cbar = fig.colorbar(im, ax=ax, fraction=0.03, pad=0.02)
    cbar.set_label("best received power (dBm)")
    cbar.ax.axhline(cfg.threshold_dbm, color="k", lw=1.5)

    # walls, darker/thicker = more attenuation
    max_att = max([w.attenuation_db for w in storey.walls] + [1.0])
    for w in storey.walls:
        ax.plot([w.p0[0], w.p1[0]], [w.p0[1], w.p1[1]], color="k",
                lw=0.8 + 2.4 * w.attenuation_db / max_att, solid_capstyle="butt")

    # rooms
    for sp in storey.spaces:
        c = sp.polygon.centroid
        cov = result.room_coverage.get(sp.name)
        label = sp.name if cov is None else f"{sp.name}\n{100 * cov:.0f}%"
        ax.text(c.x, c.y, label, ha="center", va="center", fontsize=6.5, color="#222",
                bbox=dict(boxstyle="round,pad=0.15", fc="white", ec="none", alpha=0.65))

    # access points
    for i, (x, y) in enumerate(result.aps_xy, start=1):
        ax.plot(x, y, marker="^", color="#0057b8", markeredgecolor="white", markersize=13, zorder=5)
        ax.text(x, y + 1.0, f"AP{i}", ha="center", fontsize=8, color="#0057b8", fontweight="bold", zorder=6,
                bbox=dict(boxstyle="round,pad=0.1", fc="white", ec="none", alpha=0.8))

    ax.set_aspect("equal")
    ax.set_xlabel("x (m)")
    ax.set_ylabel("y (m)")
    ax.set_title(f"{storey.name}: {len(result.aps_xy)} access point(s), {cfg.freq_ghz:g} GHz, "
                 f"coverage {100 * result.coverage:.1f} % of floor area at >= {cfg.threshold_dbm:g} dBm\n"
                 "(wall thickness in the drawing = attenuation; room labels show per-room coverage)", fontsize=9)
    fig.tight_layout()
    kwargs = {"dpi": dpi}
    if str(path).lower().endswith((".jpg", ".jpeg")):
        kwargs["pil_kwargs"] = {"quality": 88, "optimize": True}
    fig.savefig(path, **kwargs)
    plt.close(fig)
