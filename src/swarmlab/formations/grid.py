"""Rectangular lattice formation.

The grid is a regular lattice that fills the cube ``[-1, 1]^3``: each axis is
sampled with ``linspace(-1, 1, count)``, so every axis spans the full cube
regardless of how many samples it carries. The spatial density is therefore
``N / 8`` points per unit volume for any ``N``, which keeps a grid comparable
with the other formations.

Axis counts are chosen so that the lattice looks cubic:

1. If ``N`` can be written as ``a * b * c`` with ``2 <= a <= b <= c``, the
   factorization with the smallest aspect ratio ``c / a`` is used. The lattice
   is then exactly filled, with no leftover points.
2. Otherwise a box with ``a * b * c >= N`` is chosen by the same rule, and the
   first ``N`` points in ``z``-major order are kept. The formation then fills
   the box except for a partial final slab.

Both rules are deterministic and documented so that a grid can be reproduced
from ``N`` alone.
"""

from __future__ import annotations

import numpy as np

from swarmlab.models import FloatArray

__all__ = ["grid"]


def _axis(count: int) -> np.ndarray:
    """Return ``count`` evenly spaced values spanning ``[-1, 1]``."""
    if count == 1:
        return np.zeros(1, dtype=np.float64)
    return np.linspace(-1.0, 1.0, count, dtype=np.float64)


def _lattice(a: int, b: int, c: int) -> FloatArray:
    """Build the full ``a * b * c`` lattice, ordered with ``x`` varying fastest.

    The order is ``x`` fastest, then ``y``, then ``z`` slowest. Keeping the
    first ``N`` points of an oversized lattice therefore keeps complete slabs
    along ``z`` and only the last slab is partial.
    """
    x = _axis(a)
    y = _axis(b)
    z = _axis(c)
    points = np.empty((a * b * c, 3), dtype=np.float64)
    points[:, 0] = np.tile(x, b * c)
    points[:, 1] = np.tile(np.repeat(y, a), c)
    points[:, 2] = np.repeat(z, a * b)
    return points


def _exact_factors(n: int) -> tuple[int, int, int] | None:
    """Return the most cubic exact factorization of ``n``, or ``None``.

    With ``a <= b <= c`` and ``a * b * c == n`` we always have
    ``a <= n ** (1 / 3)`` and ``b <= sqrt(n / a)``, which bounds the search.

    All three sides must be at least two, otherwise the result is a flat grid
    or a line rather than a 3D formation.
    """
    best: tuple[tuple[float, int, int, int], tuple[int, int, int]] | None = None
    a_limit = int(n ** (1 / 3)) + 1
    for a in range(2, a_limit + 1):
        if n % a != 0:
            continue
        remaining = n // a
        b_limit = int(remaining**0.5) + 1
        for b in range(a, b_limit + 1):
            if remaining % b != 0:
                continue
            c = remaining // b
            if c < b:
                continue
            key = (c / a, a, b, c)
            if best is None or key < best[0]:
                best = (key, (a, b, c))
    return None if best is None else best[1]


def _near_cubic_box(n: int) -> tuple[int, int, int]:
    """Return the most cubic box ``(a, b, c)`` with ``a * b * c >= n``."""
    limit = int(np.ceil(n ** (1 / 3))) + 2
    best: tuple[tuple[float, int, int, int], tuple[int, int, int]] | None = None
    for a in range(1, limit + 1):
        for b in range(a, limit + 1):
            c = -(-n // (a * b))
            if c < b:
                continue
            key = (c / a, a * b * c - n, a, b, c)
            if best is None or key < best[0]:
                best = (key, (a, b, c))
    return best[1]


def grid(n: int) -> FloatArray:
    """Return ``n`` points of a regular lattice filling the cube ``[-1, 1]^3``.

    Args:
        n: Number of points. Must be a positive integer.

    Returns:
        An ``(n, 3)`` array of finite coordinates.

    Raises:
        ValueError: If ``n`` is not a positive integer.
    """
    if not isinstance(n, int) or isinstance(n, bool):
        raise TypeError(f"n must be an int, got {type(n).__name__}")
    if n < 1:
        raise ValueError(f"n must be positive, got {n}")

    dims = _exact_factors(n)
    if dims is not None:
        return _lattice(*dims)

    a, b, c = _near_cubic_box(n)
    return _lattice(a, b, c)[:n]
