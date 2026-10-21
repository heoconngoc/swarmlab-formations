"""Fibonacci-lattice sphere formation.

The points are the classic Fibonacci (golden-angle) lattice: latitudes are
evenly spaced, longitudes advance by the golden angle, and the result is close
to an area-uniform distribution on the unit sphere.

The lattice is fully deterministic and uses no random numbers, so the same
``n`` always yields the same points.
"""

from __future__ import annotations

import numpy as np

from swarmlab.models import FloatArray

__all__ = ["sphere"]

_GOLDEN_ANGLE = np.pi * (1.0 + np.sqrt(5.0))


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
    theta = 2.0 * np.pi * index / _GOLDEN_ANGLE
    return np.stack([radius * np.cos(theta), radius * np.sin(theta), z], axis=1)
