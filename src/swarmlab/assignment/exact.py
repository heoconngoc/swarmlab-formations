"""Exact assignment solvers.

Two implementations, both of which return a provably optimal bijection for the
given cost matrix:

``brute_force_assignment``
    Enumerate all ``N!`` permutations and keep the cheapest. Unbeatable as an
    oracle because it shares no logic with the Hungarian implementation, and
    useless beyond ``N = 8`` (40320 permutations).

``hungarian_assignment``
    The Kuhn-Munkres algorithm in the short potential-based form, ``O(N**3)``.
    This is the educational implementation for Phase 2. It is written for
    clarity, not for speed: every inner loop is a NumPy expression on a vector
    of length ``N``, so the constant factor is far worse than SciPy's compiled
    solver. Use :func:`~swarmlab.assignment.reference.scipy_assignment` for
    large instances and keep this one as the cross-check.

Tie handling differs. Brute force enumerates permutations in lexicographic
order and therefore returns the lexicographically first optimum. The Hungarian
result among tied optima depends on its column scan order: it is deterministic
for a given matrix, but it is not the lexicographic minimum. Different optimal
permutations with the same objective value are not an error, so tests compare
costs, never permutations.
"""

from __future__ import annotations

from itertools import permutations

import numpy as np

from swarmlab.assignment.costs import as_square_cost_matrix
from swarmlab.models import Assignment, FloatArray

__all__ = ["brute_force_assignment", "hungarian_assignment"]

BRUTE_FORCE_LIMIT = 8
"""Largest ``N`` accepted by :func:`brute_force_assignment`."""


def brute_force_assignment(costs: FloatArray, *, max_n: int = BRUTE_FORCE_LIMIT) -> Assignment:
    """Return the cheapest of all ``N!`` permutations.

    Args:
        costs: ``(N, N)`` matrix of pair costs.
        max_n: Refuse to enumerate more than this many agents.

    Returns:
        The lexicographically first permutation that attains the minimum cost.

    Raises:
        ValueError: If ``costs`` is not a finite square matrix, or if ``N``
            exceeds ``max_n``.

    Complexity:
        ``O(N! * N)`` time and ``O(N! * N)`` memory for the permutation table.
    """
    matrix = as_square_cost_matrix(costs)
    n = matrix.shape[0]
    if n > max_n:
        raise ValueError(
            f"brute force is limited to N <= {max_n}, got {n}; "
            f"use the Hungarian solver or SciPy instead"
        )

    candidates = np.array(list(permutations(range(n))), dtype=np.int64).reshape(-1, n)
    rows = np.arange(n)[None, :]
    totals = matrix[rows, candidates].sum(axis=1)
    best = int(np.argmin(totals))
    return Assignment(target_index=candidates[best])


def hungarian_assignment(costs: FloatArray) -> Assignment:
    """Solve the assignment problem with the Kuhn-Munkres algorithm.

    The implementation follows the classic potential formulation. Column ``0``
    is a sentinel that starts every augmenting path; real columns are ``1..N``.
    For each new row the algorithm grows an alternating tree over columns until
    it reaches an unmatched one, then flips the path. Row potentials ``u`` and
    column potentials ``v`` keep the reduced costs ``costs[i, j] - u[i] - v[j]``
    non-negative, which is what makes the greedy column choice safe.

    Args:
        costs: ``(N, N)`` matrix of pair costs. Costs need not be non-negative.

    Returns:
        A :class:`~swarmlab.models.Assignment` covering every agent.

    Raises:
        ValueError: If ``costs`` is not a finite square matrix.

    Complexity:
        ``O(N**3)`` time: ``N`` augmentations, each scanning up to ``N``
        columns. Extra memory is ``O(N)``.

    Notes:
        Costs are compared as floating-point numbers. Two permutations that are
        optimal in exact arithmetic can therefore be separated by rounding; the
        returned *cost* is stable to within a few ulps, the returned
        *permutation* need not match another optimal solver.
    """
    matrix = as_square_cost_matrix(costs)
    n = matrix.shape[0]

    u = np.zeros(n + 1, dtype=np.float64)
    v = np.zeros(n + 1, dtype=np.float64)
    matched_row = np.zeros(n + 1, dtype=np.int64)
    predecessor = np.zeros(n + 1, dtype=np.int64)

    for row in range(1, n + 1):
        matched_row[0] = row
        min_reduced = np.full(n + 1, np.inf)
        used = np.zeros(n + 1, dtype=bool)
        column = 0

        while True:
            used[column] = True
            current_row = int(matched_row[column])
            free = ~used[1:]
            reduced = matrix[current_row - 1] - u[current_row] - v[1:]

            improved = free & (reduced < min_reduced[1:])
            min_reduced[1:][improved] = reduced[improved]
            predecessor[1:][improved] = column

            candidates = np.where(free, min_reduced[1:], np.inf)
            delta = float(candidates.min())
            next_column = int(np.argmin(candidates)) + 1

            # Dual update: subtract the tightest slack from every free column,
            # and compensate on the potentials of the tree.
            u[matched_row[used]] += delta
            v[used] -= delta
            min_reduced[1:][free] -= delta

            column = next_column
            if matched_row[column] == 0:
                break

        # Flip the augmenting path: every column on it changes owner.
        while column != 0:
            previous = int(predecessor[column])
            matched_row[column] = matched_row[previous]
            column = previous

    target_index = np.empty(n, dtype=np.int64)
    for column in range(1, n + 1):
        target_index[int(matched_row[column]) - 1] = column - 1
    return Assignment(target_index=target_index)
