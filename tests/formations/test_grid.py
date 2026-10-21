"""Tests for the rectangular lattice formation."""

from __future__ import annotations

import numpy as np
import pytest

from swarmlab.formations.grid import grid

#: Golden fixture: eight agents on the vertices of a 2 x 2 x 2 lattice,
#: ordered with ``z`` varying slowest and ``x`` varying fastest.
GOLDEN_GRID_8 = np.array(
    [
        [-1.0, -1.0, -1.0],
        [1.0, -1.0, -1.0],
        [-1.0, 1.0, -1.0],
        [1.0, 1.0, -1.0],
        [-1.0, -1.0, 1.0],
        [1.0, -1.0, 1.0],
        [-1.0, 1.0, 1.0],
        [1.0, 1.0, 1.0],
    ]
)


@pytest.mark.parametrize("n", [1, 2, 7, 8, 50, 64, 97, 100, 500, 1000])
def test_grid_shape_and_finiteness(n: int) -> None:
    points = grid(n)
    assert points.shape == (n, 3)
    assert np.isfinite(points).all()


@pytest.mark.parametrize("n", [1, 8, 97, 100, 1000])
def test_grid_stays_inside_the_cube(n: int) -> None:
    points = grid(n)
    assert np.all(points >= -1.0)
    assert np.all(points <= 1.0)


def test_grid_matches_the_golden_fixture() -> None:
    np.testing.assert_allclose(grid(8), GOLDEN_GRID_8, atol=1e-12)


def test_grid_is_deterministic() -> None:
    np.testing.assert_array_equal(grid(100), grid(100))


def test_grid_has_no_duplicate_points() -> None:
    points = grid(97)
    assert np.unique(points, axis=0).shape[0] == points.shape[0]


def test_grid_uses_an_exact_factorization_when_available() -> None:
    # 100 = 4 * 5 * 5, the most cubic exact factorization.
    points = grid(100)
    assert np.unique(points[:, 0]).size == 4
    assert np.unique(points[:, 1]).size == 5
    assert np.unique(points[:, 2]).size == 5


def test_grid_falls_back_to_a_near_cubic_box() -> None:
    # 97 is prime, so no exact 3-factorization exists.
    points = grid(97)
    assert points.shape == (97, 3)
    assert np.unique(points[:, 0]).size == 4
    assert np.unique(points[:, 1]).size == 5


def test_grid_rejects_invalid_sizes() -> None:
    with pytest.raises(ValueError, match="positive"):
        grid(0)
    with pytest.raises(TypeError):
        grid(3.5)  # type: ignore[arg-type]
