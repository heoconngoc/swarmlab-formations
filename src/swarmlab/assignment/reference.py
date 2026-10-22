"""Reference assignment solver backed by SciPy.

``scipy.optimize.linear_sum_assignment`` is a compiled Jonker-Volgenant style
solver. Phase 2 uses it for two jobs:

* as the *reference optimum* against which the educational solvers are checked;
* as the practical solver for large instances, where the pure-Python Hungarian
  implementation is too slow.

The reference is defined by the provider of the cost matrix, so it is immune to
bugs in this repository. That is the point: an independent implementation is
evidence, a second copy of our own code is not.
"""

from __future__ import annotations

import numpy as np
from scipy.optimize import linear_sum_assignment

from swarmlab.assignment.costs import as_square_cost_matrix
from swarmlab.models import Assignment, FloatArray

__all__ = ["scipy_assignment"]


def scipy_assignment(costs: FloatArray) -> Assignment:
    """Return the optimal bijection reported by SciPy.

    Args:
        costs: ``(N, N)`` matrix of pair costs.

    Returns:
        A :class:`~swarmlab.models.Assignment` covering every agent.

    Raises:
        ValueError: If ``costs`` is not a finite square matrix.

    Complexity:
        Roughly ``O(N**3)`` in the worst case, with a compiled inner loop.
    """
    matrix = as_square_cost_matrix(costs)
    row_index, column_index = linear_sum_assignment(matrix)

    # For a square matrix SciPy returns every row exactly once; assert that
    # instead of silently reshaping a rectangular result into a bijection.
    if not np.array_equal(row_index, np.arange(matrix.shape[0])):
        raise RuntimeError(f"linear_sum_assignment returned unexpected rows: {row_index}")

    return Assignment(target_index=column_index)
