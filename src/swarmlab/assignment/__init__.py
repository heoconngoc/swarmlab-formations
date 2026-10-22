"""Mapping agents to targets.

Two kinds of solver live here.

* ``MATRIX_SOLVERS`` consume a dense ``(N, N)`` cost matrix. They all see the
  same matrix, which is what makes their costs comparable.
* :func:`~swarmlab.assignment.random.random_assignment` never looks at the
  costs at all. It is a correctness baseline, not a solver, and is therefore
  not part of the registry.

Phase 1 shipped only the random permutation. Phase 2 adds the greedy
heuristics, the educational exact solver, and the SciPy reference.
"""

from swarmlab.assignment.costs import (
    COST_FUNCTIONS,
    euclidean_distance_costs,
    squared_distance_costs,
    total_cost,
)
from swarmlab.assignment.exact import brute_force_assignment, hungarian_assignment
from swarmlab.assignment.greedy import greedy_assignment, greedy_pair_assignment
from swarmlab.assignment.random import random_assignment
from swarmlab.assignment.reference import scipy_assignment

__all__ = [
    "COST_FUNCTIONS",
    "MATRIX_SOLVERS",
    "brute_force_assignment",
    "euclidean_distance_costs",
    "greedy_assignment",
    "greedy_pair_assignment",
    "hungarian_assignment",
    "random_assignment",
    "scipy_assignment",
    "squared_distance_costs",
    "total_cost",
]

MATRIX_SOLVERS = {
    "greedy": greedy_assignment,
    "greedy_pair": greedy_pair_assignment,
    "hungarian": hungarian_assignment,
    "brute_force": brute_force_assignment,
    "scipy": scipy_assignment,
}
"""Method name to matrix solver. ``brute_force`` only accepts small ``N``."""
