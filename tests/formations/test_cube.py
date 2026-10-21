"""Tests for the cube-surface formation."""

from __future__ import annotations

import numpy as np
import pytest

from swarmlab.formations.cube import cube_surface


@pytest.mark.parametrize("n", [1, 8, 64, 1000])
def test_cube_shape_and_finiteness(n: int) -> None:
    points = cube_surface(n)
    assert points.shape == (n, 3)
    assert np.isfinite(points).all()


@pytest.mark.parametrize("n", [1, 10, 100, 1000])
def test_cube_points_lie_on_the_cube_surface(n: int) -> None:
    max_norm = np.max(np.abs(cube_surface(n)), axis=1)
    np.testing.assert_allclose(max_norm, 1.0, atol=1e-12)


def test_cube_is_deterministic() -> None:
    np.testing.assert_array_equal(cube_surface(100), cube_surface(100))


def test_cube_rejects_invalid_sizes() -> None:
    with pytest.raises(ValueError, match="positive"):
        cube_surface(0)
