"""Command-line interface:  site5g sample | inspect | plan"""
from __future__ import annotations

import argparse
import json
import os
import sys

from . import __version__
from .ifc_loader import load_ifc
from .materials import load_table
from .planner import PlanConfig, plan_storey


def cmd_sample(args) -> int:
    from .sample_ifc import build_sample
    os.makedirs(os.path.dirname(os.path.abspath(args.output)), exist_ok=True)
    build_sample(args.output)
    print(f"wrote {args.output}")
    return 0


def cmd_inspect(args) -> int:
    """Show what the loader understood - ALWAYS do this first on a new model."""
    storeys = load_ifc(args.ifc, load_table(args.materials))
    for st in storeys:
        print(f"\n== {st.name} (elevation {st.elevation:g} m): {len(st.walls)} walls, {len(st.spaces)} spaces")
        for w in st.walls:
            mats = ", ".join(w.materials) or "(no material!)"
            flag = "" if w.matched_keywords else "   <-- no keyword matched, default attenuation used"
            print(f"  {w.name:<28} {w.length:6.2f} m  t={w.thickness:4.2f} m  {w.attenuation_db:5.1f} dB  [{mats}]{flag}")
        for sp in st.spaces:
            print(f"  room {sp.name:<22} area {sp.polygon.area:7.1f} m2")
    return 0


def cmd_plan(args) -> int:
    from .viz import save_coverage_figure
    storeys = load_ifc(args.ifc, load_table(args.materials))
    if not storeys:
        print("error: the IFC file contains no building storeys with walls", file=sys.stderr)
        return 1
    cfg = PlanConfig(freq_ghz=args.freq, tx_power_dbm=args.tx_power, path_loss_exponent=args.exponent,
                     threshold_dbm=args.threshold, target_coverage=args.target,
                     min_room_coverage=args.min_room, grid_m=args.grid, candidate_spacing_m=args.candidate_spacing,
                     max_aps=args.max_aps)
    os.makedirs(args.out, exist_ok=True)
    summary = []
    for st in storeys:
        if args.storey and st.name != args.storey:
            continue
        if not st.walls:
            continue
        res = plan_storey(st, cfg)
        save_coverage_figure(os.path.join(args.out, f"coverage_{st.name.replace(' ', '_')}.{args.format}"), st, res)
        summary.append({
            "storey": st.name,
            "access_points": [{"x_m": round(x, 2), "y_m": round(y, 2)} for x, y in res.aps_xy],
            "coverage": round(res.coverage, 4),
            "coverage_after_each_ap": [round(c, 4) for c in res.coverage_after_each_ap],
            "room_coverage": {k: round(v, 3) for k, v in res.room_coverage.items()},
            "goals_met": res.coverage >= cfg.target_coverage and all(v >= cfg.min_room_coverage for v in res.room_coverage.values()),
        })
    with open(os.path.join(args.out, "plan.json"), "w") as f:
        json.dump({"config": vars(args) | {"fn": None}, "storeys": summary}, f, indent=2, default=str)
    for s in summary:
        status = "goals met" if s["goals_met"] else "GOALS NOT MET (raise --max-aps or lower the targets)"
        print(f"{s['storey']}: {len(s['access_points'])} AP(s), coverage {100 * s['coverage']:.1f} %, "
              f"worst room {100 * min(s['room_coverage'].values()):.0f} % - {status}")
    print(f"results in {args.out}/")
    return 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="site5g", description="Indoor 5G coverage planning from an IFC model")
    p.add_argument("--version", action="version", version=__version__)
    sub = p.add_subparsers(dest="command", required=True)

    s = sub.add_parser("sample", help="write a synthetic office-floor IFC to play with")
    s.add_argument("output", nargs="?", default="examples/sample_office.ifc")
    s.set_defaults(fn=cmd_sample)

    i = sub.add_parser("inspect", help="list walls, materials and rooms found in an IFC file")
    i.add_argument("ifc")
    i.add_argument("--materials", help="JSON file with extra/overriding {keyword: dB} entries")
    i.set_defaults(fn=cmd_inspect)

    c = sub.add_parser("plan", help="place access points and write a coverage map")
    c.add_argument("ifc")
    c.add_argument("--out", default="out")
    c.add_argument("--materials", help="JSON file with extra/overriding {keyword: dB} entries")
    c.add_argument("--freq", type=float, default=3.5, help="carrier frequency in GHz")
    c.add_argument("--tx-power", type=float, default=23.0, help="AP power incl. antenna gain, dBm")
    c.add_argument("--exponent", type=float, default=3.0, help="path-loss exponent (2 = free space)")
    c.add_argument("--threshold", type=float, default=-70.0, help="required received power, dBm")
    c.add_argument("--target", type=float, default=0.95, help="required overall coverage fraction")
    c.add_argument("--min-room", type=float, default=0.90, help="required coverage fraction in EVERY room")
    c.add_argument("--grid", type=float, default=0.5, help="receiver grid spacing, m")
    c.add_argument("--candidate-spacing", type=float, default=2.0, help="candidate AP grid spacing, m")
    c.add_argument("--max-aps", type=int, default=10)
    c.add_argument("--storey", help="only plan the storey with this name")
    c.add_argument("--format", choices=["png", "jpg", "svg"], default="png")
    c.set_defaults(fn=cmd_plan)
    return p


def main(argv=None) -> int:
    args = build_parser().parse_args(argv)
    try:
        return args.fn(args)
    except (OSError, ValueError, RuntimeError) as e:
        print(f"error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
