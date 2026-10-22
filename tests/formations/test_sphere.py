"""Tests for the Fibonacci-lattice sphere formation."""

from __future__ import annotations

import numpy as np
import pytest

from swarmlab.formations.sphere import sphere

#: Golden fixture: the four points of ``sphere(4)``, pinned exactly. This locks
#: the angular step to the golden angle; a different step still produces points
#: on the sphere, so the norm checks alone cannot catch it.
GOLDEN_SPHERE_4 = np.array(
    [
        [-0.23968846013182918, 0.6164815018146389, 0.75],
        [0.8683062340463996, -0.42842068567724306, 0.25],
        [-0.9296560086630493, -0.27062835320174505, -0.25],
        [0.34340440932514366, 0.5653082448152063, -0.75],
    ]
)


@pytest.mark.parametrize("n", [1, 2, 10, 64, 1000])
def test_sphere_shape_and_finiteness(n: int) -> None:
    points = sphere(n)
    assert points.shape == (n, 3)
    assert np.isfinite(points).all()


@pytest.mark.parametrize("n", [1, 10, 100, 1000])
def test_sphere_points_lie_on_the_unit_sphere(n: int) -> None:
    norms = np.linalg.norm(sphere(n), axis=1)
    np.testing.assert_allclose(norms, 1.0, atol=1e-12)


def test_sphere_matches_the_golden_fixture() -> None:
    np.testing.assert_allclose(sphere(4), GOLDEN_SPHERE_4, atol=1e-12)


@pytest.mark.parametrize("n", [100, 200, 500])
def test_sphere_lattice_is_evenly_spread(n: int) -> None:
    """Nearest-neighbour distances must be close to uniform.

    A golden-angle lattice gives a coefficient of variation near 0.02. A wrong
    angular step still yields points on the sphere but lines them up along a
    spiral, which pushes the coefficient above 0.08. The thresholds are
    empirical, chosen with roughly a factor of two of margin on both sides.
    """
    points = sphere(n)
    distances = np.linalg.norm(points[:, None, :] - points[None, :, :], axis=2)
    np.fill_diagonal(distances, np.inf)
    nearest = distances.min(axis=1)

    assert nearest.std() / nearest.mean() < 0.05
    assert nearest.max() / nearest.min() < 1.25


def test_sphere_is_deterministic() -> None:
    np.testing.assert_array_equal(sphere(100), sphere(100))


def test_sphere_has_no_duplicate_points() -> None:
    points = sphere(200)
    assert np.unique(points, axis=0).shape[0] == points.shape[0]


def test_sphere_rejects_invalid_sizes() -> None:
    with pytest.raises(ValueError, match="positive"):
        sphere(0)
