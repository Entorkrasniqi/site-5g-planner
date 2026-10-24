import numpy as np

from site5g.ifc_loader import _fit_segment, load_ifc
from site5g.materials import wall_attenuation


def test_fit_segment_recovers_a_rotated_thick_wall():
    # 10 m long, 0.2 m thick wall rotated 30 degrees, centre-line starting at (1, 2)
    th = np.deg2rad(30)
    axis, normal = np.array([np.cos(th), np.sin(th)]), np.array([-np.sin(th), np.cos(th)])
    pts = [np.array([1.0, 2.0]) + axis * a + normal * b for a in (0, 10) for b in (-0.1, 0.1)]
    p0, p1, t = _fit_segment(np.array(pts))
    ends = sorted([tuple(np.round(p0, 6)), tuple(np.round(p1, 6))])
    expected = sorted([tuple(np.round([1.0, 2.0], 6)), tuple(np.round(np.array([1.0, 2.0]) + 10 * axis, 6))])
    assert np.allclose(ends, expected, atol=1e-6)
    assert abs(t - 0.2) < 1e-9


def test_loader_finds_one_storey_with_all_walls_and_rooms(storey):
    assert storey.name == "Level 1"
    assert len(storey.walls) == 28
    assert len(storey.spaces) == 10


def test_exterior_walls_are_recovered_with_right_geometry_and_material(storey):
    ext = {w.name: w for w in storey.walls if w.name.startswith("Ext")}
    assert set(ext) == {"Ext S", "Ext E", "Ext N", "Ext W"}
    for w in ext.values():
        assert abs(w.thickness - 0.30) < 1e-6
        assert w.materials == ["Concrete"] and w.attenuation_db == 12.0
    south = ext["Ext S"]
    ends = sorted([tuple(np.round(south.p0, 3)), tuple(np.round(south.p1, 3))])
    assert np.allclose(ends, [(0, 0), (36, 0)], atol=1e-3)
    assert abs(ext["Ext E"].length - 20.0) < 1e-6


def test_partition_and_glass_attenuations(storey):
    by_name = {w.name: w for w in storey.walls}
    assert by_name["South partition x=7"].attenuation_db == 3.0
    assert abs(by_name["South partition x=7"].thickness - 0.10) < 1e-6
    glass = [w for w in storey.walls if w.materials == ["Glass"]]
    assert len(glass) == 4                          # two meeting rooms, two wall pieces each (doorway gap)
    assert all(abs(w.length - 4.0) < 1e-6 for w in glass)


def test_rooms_have_the_expected_area(storey):
    rooms = {s.name: s.polygon.area for s in storey.spaces}
    assert abs(rooms["Corridor"] - (36 - 0.3) * 2.9) < 1e-6
    assert abs(rooms["South 1"] - 7 * 8.3) < 1e-6


def test_material_lookup_rules():
    assert wall_attenuation(["Reinforced Concrete C30"]) == (12.0, ["concrete"])
    assert wall_attenuation(["Gypsum", "Concrete"])[0] == 15.0      # layers add up
    db, matched = wall_attenuation(["Mystery stuff"])
    assert db == 6.0 and matched == []                              # default + flagged as unmatched
    assert wall_attenuation(["Concrete"], {"concrete": 30.0})[0] == 30.0


def test_custom_material_table_changes_loaded_attenuation(sample_ifc):
    st = load_ifc(sample_ifc, {"concrete": 25.0, "gypsum": 1.0, "glass": 2.0})[0]
    assert {w.attenuation_db for w in st.walls} == {25.0, 1.0, 2.0}
