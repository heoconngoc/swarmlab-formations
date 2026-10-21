"""Cube-surface formation.

The points are obtained by projecting a Fibonacci lattice sphere onto the cube
surface: dividing each point by its largest absolute coordinate maps the unit
sphere onto the boundary of ``[-1, 1]^3``.

Reusing the sphere generator keeps the cube surface evenly covered and avoids a
second, separately tuned sampling rule.
"""

from __future__ import annotations

import numpy as np

from swarmlab.formations.sphere import sphere
from swarmlab.models import FloatArray

__all__ = ["cube_surface"]


def cube_surface(n: int) -> FloatArray:
    """Return ``n`` points on the surface of the cube ``[-1, 1]^3``.

    Args:
        n: Number of points. Must be a positive integer.

    Returns:
        An ``(n, 3)`` array where every row satisfies
        ``max(|x|, |y|, |z|) == 1``.

    Raises:
        ValueError: If ``n`` is not a positive integer.
    """
    if not isinstance(n, int) or isinstance(n, bool):
        raise TypeError(f"n must be an int, got {type(n).__name__}")
    if n < 1:
        raise ValueError(f"n must be positive, got {n}")

    points = sphere(n)
    scale = np.max(np.abs(points), axis=1)
    return points / scale[:, None]
