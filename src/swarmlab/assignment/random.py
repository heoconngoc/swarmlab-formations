"""Seeded random assignment.

The assignment is a uniformly drawn permutation of ``range(N)``. The seed
makes the result reproducible, so an experiment record can be replayed exactly.

This is deliberately *not* an optimizer. A random permutation ignores the
geometry entirely and therefore produces long, crossing paths. That makes it a
useful lower bound for the assignment solvers of Phase 2.
"""

from __future__ import annotations

import numpy as np

from swarmlab.models import Assignment

__all__ = ["random_assignment"]


def random_assignment(n: int, seed: int) -> Assignment:
    """Return a random bijection from ``N`` agents to ``N`` targets.

    Args:
        n: Number of agents. Must be a positive integer.
        seed: Seed of the random generator. The same ``(n, seed)`` pair always
            yields exactly the same permutation.

    Returns:
        An :class:`~swarmlab.models.Assignment` holding a permutation of
        ``range(n)``.

    Raises:
        ValueError: If ``n`` is not a positive integer.
    """
    if not isinstance(n, int) or isinstance(n, bool):
        raise TypeError(f"n must be an int, got {type(n).__name__}")
    if n < 1:
        raise ValueError(f"n must be positive, got {n}")

    rng = np.random.default_rng(seed)
    return Assignment(target_index=rng.permutation(n))
