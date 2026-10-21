"""Tests for the Fibonacci-lattice sphere formation."""

from __future__ import annotations

import numpy as np
import pytest

from swarmlab.formations.sphere import sphere


@pytest.mark.parametrize("n", [1, 2, 10, 64, 1000])
def test_sphere_shape_and_finiteness(n: int) -> None:
    points = sphere(n)
    assert points.shape == (n, 3)
    assert np.isfinite(points).all()


@pytest.mark.parametrize("n", [1, 10, 100, 1000])
def test_sphere_points_lie_on_the_unit_sphere(n: int) -> None:
    norms = np.linalg.norm(sphere(n), axis=1)
    np.testing.assert_allclose(norms, 1.0, atol=1e-12)


def test_sphere_is_deterministic() -> None:
    np.testing.assert_array_equal(sphere(100), sphere(100))


def test_sphere_has_no_duplicate_points() -> None:
    points = sphere(200)
    assert np.unique(points, axis=0).shape[0] == points.shape[0]


def test_sphere_rejects_invalid_sizes() -> None:
    with pytest.raises(ValueError, match="positive"):
        sphere(0)
