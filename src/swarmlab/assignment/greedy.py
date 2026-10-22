"""Greedy assignment heuristics.

Greedy is the cheapest non-trivial baseline: it never looks ahead, so a locally
attractive pair can force an expensive leg later. Two variants are provided
because they fail in different ways.

``greedy_assignment``
    Walk the agents in index order. Each agent takes the nearest target that is
    still free. The outcome depends on that agent order, so agent ``0`` gets the
    first pick even if another agent had a much cheaper claim.

``greedy_pair_assignment``
    Sort all ``N**2`` pairs by cost and accept a pair when both endpoints are
    still free. No agent is privileged, but a cheap edge can still block two
    slightly more expensive edges that would have covered more agents.

Ties are broken deterministically: the first variant keeps the lowest target
index, the second keeps lexicographic ``(cost, agent, target)`` order. Neither
variant is an optimizer; ``experiments/phase2.py`` measures the optimality gap
on real instances.
"""

from __future__ import annotations

import numpy as np

from swarmlab.assignment.costs import as_square_cost_matrix
from swarmlab.models import Assignment, FloatArray

__all__ = ["greedy_assignment", "greedy_pair_assignment"]


def greedy_assignment(costs: FloatArray) -> Assignment:
    """Assign agents in index order, each to its nearest free target.

    Args:
        costs: ``(N, N)`` matrix of pair costs.

    Returns:
        A :class:`~swarmlab.models.Assignment` covering every agent.

    Raises:
        ValueError: If ``costs`` is not a finite square matrix.

    Complexity:
        ``O(N**2)`` time and ``O(N)`` extra memory: one ``argmin`` over the
        remaining targets per agent.
    """
    matrix = as_square_cost_matrix(costs)
    n = matrix.shape[0]

    available = np.ones(n, dtype=bool)
    target_index = np.empty(n, dtype=np.int64)
    for agent in range(n):
        # Masking with +inf keeps the choice inside the still-free targets.
        # ``argmin`` returns the first minimum, so ties pick the lowest index.
        masked = np.where(available, matrix[agent], np.inf)
        chosen = int(np.argmin(masked))
        target_index[agent] = chosen
        available[chosen] = False

    return Assignment(target_index=target_index)


def greedy_pair_assignment(costs: FloatArray) -> Assignment:
    """Accept pairs from cheapest to most expensive, skipping taken endpoints.

    Args:
        costs: ``(N, N)`` matrix of pair costs.

    Returns:
        A :class:`~swarmlab.models.Assignment` covering every agent.

    Raises:
        ValueError: If ``costs`` is not a finite square matrix.

    Complexity:
        ``O(N**2 log N)`` time for the sort and ``O(N**2)`` memory for the
        flattened index vector. The scan stops as soon as ``N`` pairs are
        accepted, so it usually reads only a fraction of the sorted array.
    """
    matrix = as_square_cost_matrix(costs)
    n = matrix.shape[0]

    # ``axis=None`` flattens in row-major (agent, then target) order, and a
    # stable sort keeps that order among equal costs. The resulting scan is
    # therefore ordered by (cost, agent, target): fully deterministic.
    order = np.argsort(matrix, axis=None, kind="stable")

    target_index = np.full(n, -1, dtype=np.int64)
    taken = np.zeros(n, dtype=bool)
    remaining = n
    for flat in order:
        agent, target = divmod(int(flat), n)
        if target_index[agent] != -1 or taken[target]:
            continue
        target_index[agent] = target
        taken[target] = True
        remaining -= 1
        if remaining == 0:
            break

    return Assignment(target_index=target_index)
