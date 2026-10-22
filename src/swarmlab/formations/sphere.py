"""Fibonacci-lattice sphere formation.

The points are the classic Fibonacci (golden-angle) lattice: latitudes are
evenly spaced, longitudes advance by the golden angle, and the result is close
to an area-uniform distribution on the unit sphere.

The angular step matters. Advancing the azimuth by ``2*pi/phi`` radians per
point (the golden angle, equivalently ``-2.39996`` radians modulo ``2*pi``)
spreads the longitudes quasi-uniformly. Using a smaller step, such as
``1/phi`` radians, still produces points on the sphere, but they line up along
a visible spiral and cluster: the nearest-neighbour distance then varies by a
factor of two instead of a few percent. ``tests/formations/test_sphere.py``
pins both the exact coordinates and that spread.

The lattice is fully deterministic and uses no random numbers, so the same
``n`` always yields the same points.
"""

from __future__ import annotations

import numpy as np

from swarmlab.models import FloatArray

__all__ = ["sphere"]

_GOLDEN_RATIO = (1.0 + np.sqrt(5.0)) / 2.0


def sphere(n: int) -> FloatArray:
    """Return ``n`` points on the unit sphere.

    Args:
        n: Number of points. Must be a positive integer.

    Returns:
        An ``(n, 3)`` array whose rows have unit Euclidean norm.

    Raises:
        ValueError: If ``n`` is not a positive integer.
    """
    if not isinstance(n, int) or isinstance(n, bool):
        raise TypeError(f"n must be an int, got {type(n).__name__}")
    if n < 1:
        raise ValueError(f"n must be positive, got {n}")

    index = np.arange(n, dtype=np.float64) + 0.5
    z = 1.0 - 2.0 * index / n
    radius = np.sqrt(np.maximum(0.0, 1.0 - z * z))
    # Golden angle in radians: 2*pi/phi ~= 3.8832, i.e. -2.39996 mod 2*pi.
    theta = 2.0 * np.pi * index / _GOLDEN_RATIO
    return np.stack([radius * np.cos(theta), radius * np.sin(theta), z], axis=1)
