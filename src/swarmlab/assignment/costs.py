"""Pairwise cost matrices for the assignment problem.

Every matrix solver in this package consumes a dense ``(N, N)`` cost matrix, so
the objective is defined in exactly one place. Two objectives are available:

``euclidean_distance``
    ``costs[i, j] = ||source_i - target_j||_2``. Minimizing the sum minimizes
    the total straight-line travel length of a linear transition.
``squared_distance``
    ``costs[i, j] = ||source_i - target_j||_2 ** 2``. This is a **different**
    objective: it punishes long legs much harder than short ones, so it can
    produce a different optimal permutation. Name the objective in every
    experiment record; a cost number without its objective is meaningless.

Both objectives are derived from one array of pairwise deltas and therefore
cost ``O(N**2)`` time and memory. The matrix is the shared input of all
solvers: comparing two methods on two different matrices would compare two
different problems.
"""

from __future__ import annotations

from collections.abc import Callable

import numpy as np

from swarmlab.models import Assignment, FloatArray

__all__ = [
    "COST_FUNCTIONS",
    "as_square_cost_matrix",
    "euclidean_distance_costs",
    "squared_distance_costs",
    "total_cost",
]


def _as_positions(array: np.ndarray, name: str) -> FloatArray:
    """Return ``array`` as a finite ``(N, 3)`` float array.

    Raises:
        ValueError: If the shape is wrong or a value is not finite.
    """
    converted = np.asarray(array, dtype=np.float64)
    if converted.ndim != 2 or converted.shape[1] != 3:
        raise ValueError(f"{name} must have shape (N, 3), got {converted.shape}")
    if not np.isfinite(converted).all():
        raise ValueError(f"{name} contains non-finite values")
    return converted


def _pairwise_squared_distances(sources: FloatArray, targets: FloatArray) -> FloatArray:
    """Return ``||sources_i - targets_j||**2`` for every pair.

    The subtraction is broadcast to an ``(N, N, 3)`` temporary, which is the
    dominant allocation. The sum over the last axis is done with ``einsum`` so
    that no extra ``(N, N, 3)`` square has to be materialized.
    """
    deltas = sources[:, None, :] - targets[None, :, :]
    return np.einsum("ijk,ijk->ij", deltas, deltas)


def euclidean_distance_costs(sources: FloatArray, targets: FloatArray) -> FloatArray:
    """Return the matrix of Euclidean distances ``||s_i - t_j||_2``.

    Args:
        sources: ``(N, 3)`` start positions.
        targets: ``(N, 3)`` goal positions.

    Returns:
        An ``(N, N)`` matrix whose entry ``[i, j]`` is the distance from agent
        ``i`` to target ``j``.

    Raises:
        ValueError: If the inputs are not finite ``(N, 3)`` arrays of equal
            length.
    """
    source = _as_positions(sources, "sources")
    target = _as_positions(targets, "targets")
    if source.shape != target.shape:
        raise ValueError(
            f"sources and targets must have the same shape, got {source.shape} and {target.shape}"
        )
    return np.sqrt(_pairwise_squared_distances(source, target))


def squared_distance_costs(sources: FloatArray, targets: FloatArray) -> FloatArray:
    """Return the matrix of squared Euclidean distances ``||s_i - t_j||_2**2``.

    Args:
        sources: ``(N, 3)`` start positions.
        targets: ``(N, 3)`` goal positions.

    Returns:
        An ``(N, N)`` matrix of squared distances.

    Raises:
        ValueError: If the inputs are not finite ``(N, 3)`` arrays of equal
            length.
    """
    source = _as_positions(sources, "sources")
    target = _as_positions(targets, "targets")
    if source.shape != target.shape:
        raise ValueError(
            f"sources and targets must have the same shape, got {source.shape} and {target.shape}"
        )
    return _pairwise_squared_distances(source, target)


def as_square_cost_matrix(costs: np.ndarray) -> FloatArray:
    """Validate that ``costs`` is a finite ``(N, N)`` matrix and return it.

    Raises:
        ValueError: If the matrix is not square or contains non-finite values.
    """
    matrix = np.asarray(costs, dtype=np.float64)
    if matrix.ndim != 2 or matrix.shape[0] != matrix.shape[1]:
        raise ValueError(f"costs must be a square (N, N) matrix, got shape {matrix.shape}")
    if matrix.shape[0] == 0:
        raise ValueError("costs must not be empty")
    if not np.isfinite(matrix).all():
        raise ValueError("costs contains non-finite values")
    return matrix


def total_cost(costs: np.ndarray, assignment: Assignment) -> float:
    """Return the objective value ``sum_i costs[i, assignment[i]]``.

    Args:
        costs: ``(N, N)`` cost matrix that the assignment was optimized for.
        assignment: Bijection from agents to targets.

    Returns:
        The summed cost of the chosen pairs.

    Raises:
        ValueError: If the matrix and the assignment do not describe the same
            number of agents.
    """
    matrix = np.asarray(costs, dtype=np.float64)
    index = assignment.target_index
    if matrix.shape != (index.size, index.size):
        raise ValueError(
            f"costs of shape {matrix.shape} do not match an assignment of {index.size} agents"
        )
    return float(matrix[np.arange(index.size), index].sum())


COST_FUNCTIONS: dict[str, Callable[[FloatArray, FloatArray], FloatArray]] = {
    "euclidean_distance": euclidean_distance_costs,
    "squared_distance": squared_distance_costs,
}
"""Objective name to cost-matrix builder. Keys are recorded in experiment output."""
