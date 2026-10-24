import numpy as np

from site5g.propagation import fspl_1m_db, path_loss_db, wall_loss_db


def test_fspl_at_one_metre_matches_the_textbook_formula():
    # FSPL(dB) = 32.44 + 20 log10(f_MHz) + 20 log10(d_km); d = 1 m = 0.001 km
    expected = 32.44 + 20 * np.log10(3500) + 20 * np.log10(0.001)
    assert abs(fspl_1m_db(3.5e9) - expected) < 0.05


def test_higher_frequency_means_more_loss_6_db_per_doubling():
    assert abs(fspl_1m_db(7e9) - fspl_1m_db(3.5e9) - 6.0206) < 1e-3


def test_doubling_distance_adds_3n_db():
    for n in (2.0, 3.0):
        d1 = path_loss_db(10.0, 3.5e9, n)
        d2 = path_loss_db(20.0, 3.5e9, n)
        assert abs((d2 - d1) - 10 * n * np.log10(2)) < 1e-9


def test_distances_below_one_metre_are_clamped():
    assert path_loss_db(0.2, 3.5e9, 3.0) == path_loss_db(1.0, 3.5e9, 3.0)


def test_wall_loss_is_added_to_path_loss():
    assert abs(path_loss_db(10.0, 3.5e9, 2.0, 12.0) - path_loss_db(10.0, 3.5e9, 2.0) - 12.0) < 1e-9


AP = np.array([0.0, 0.0])
WALL_P0, WALL_P1 = np.array([[5.0, -2.0]]), np.array([[5.0, 2.0]])      # vertical wall at x = 5


def test_ray_crossing_a_wall_counts_once():
    cells = np.array([[10.0, 0.0]])
    assert wall_loss_db(AP, cells, WALL_P0, WALL_P1, np.array([7.0]))[0] == 7.0


def test_ray_that_stops_before_the_wall_is_not_attenuated():
    cells = np.array([[4.0, 0.0]])
    assert wall_loss_db(AP, cells, WALL_P0, WALL_P1, np.array([7.0]))[0] == 0.0


def test_ray_that_passes_beside_the_wall_is_not_attenuated():
    cells = np.array([[10.0, 8.0]])          # crosses x=5 at y=4, beyond the wall's end (y<=2)
    assert wall_loss_db(AP, cells, WALL_P0, WALL_P1, np.array([7.0]))[0] == 0.0


def test_parallel_ray_is_not_attenuated():
    cells = np.array([[0.0, 3.0]])           # straight up, parallel to the wall
    assert wall_loss_db(AP, cells, WALL_P0, WALL_P1, np.array([7.0]))[0] == 0.0


def test_two_walls_add_up_and_cells_are_independent():
    p0 = np.array([[5.0, -2.0], [8.0, -2.0]])
    p1 = np.array([[5.0, 2.0], [8.0, 2.0]])
    cells = np.array([[10.0, 0.0], [6.0, 0.0], [4.0, 0.0]])
    out = wall_loss_db(AP, cells, p0, p1, np.array([3.0, 12.0]))
    assert list(out) == [15.0, 3.0, 0.0]


def test_no_walls_means_no_loss():
    out = wall_loss_db(AP, np.array([[1.0, 1.0]]), np.zeros((0, 2)), np.zeros((0, 2)), np.zeros(0))
    assert out[0] == 0.0
