import numpy as np
from shapely.geometry import box

from site5g.ifc_loader import Space, Storey, Wall
from site5g.planner import PlanConfig, plan_storey


def _room(w=10.0, h=10.0, walls=()):
    return Storey("Test", 0.0, list(walls), [Space("s", "Room", "Test", box(0, 0, w, h))])


def _wall(x0, y0, x1, y1, att):
    return Wall("g", "w", "Test", np.array([x0, y0], float), np.array([x1, y1], float), 0.1, [], att)


def test_a_small_open_room_needs_exactly_one_ap():
    res = plan_storey(_room(10, 10), PlanConfig())
    assert len(res.aps_xy) == 1 and res.coverage > 0.99


def test_sample_floor_reaches_its_goals(storey):
    cfg = PlanConfig()
    res = plan_storey(storey, cfg)
    assert res.coverage >= cfg.target_coverage
    assert min(res.room_coverage.values()) >= cfg.min_room_coverage
    assert len(res.aps_xy) <= cfg.max_aps


def test_coverage_never_decreases_when_an_ap_is_added(storey):
    res = plan_storey(storey, PlanConfig(freq_ghz=28.0, max_aps=20))
    c = res.coverage_after_each_ap
    assert all(b >= a - 1e-12 for a, b in zip(c, c[1:]))


def test_ap_budget_is_respected_and_unmet_goals_are_visible(storey):
    res = plan_storey(storey, PlanConfig(freq_ghz=28.0, max_aps=2))
    assert len(res.aps_xy) == 2
    assert res.coverage < PlanConfig().target_coverage


def test_access_points_are_never_placed_in_excluded_rooms(storey):
    core = next(s for s in storey.spaces if s.name == "Core").polygon
    res = plan_storey(storey, PlanConfig(freq_ghz=28.0, max_aps=20))
    for x, y in res.aps_xy:
        assert not core.contains(__import__("shapely.geometry", fromlist=["Point"]).Point(x, y))


def test_higher_frequency_needs_more_access_points(storey):
    n = {f: len(plan_storey(storey, PlanConfig(freq_ghz=f, max_aps=25)).aps_xy) for f in (3.5, 28.0)}
    assert n[28.0] > n[3.5]


def test_a_wall_splits_the_coverage_problem():
    # A heavily attenuating wall (60 dB) divides a long room in two: one AP cannot serve both halves.
    wall = _wall(10, -1, 10, 11, 60.0)
    st = Storey("Test", 0.0, [wall], [Space("s", "Hall", "Test", box(0, 0, 20, 10))])
    res = plan_storey(st, PlanConfig(threshold_dbm=-60, min_room_coverage=0.9))
    assert len(res.aps_xy) == 2
    xs = sorted(x for x, _ in res.aps_xy)
    assert xs[0] < 10 < xs[1]


def test_storey_without_area_is_rejected():
    import pytest
    with pytest.raises(ValueError):
        plan_storey(Storey("Empty", 0.0, [], []))
