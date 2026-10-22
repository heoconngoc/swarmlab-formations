"""Tests for the exact assignment solvers.

The brute-force oracle and the SciPy reference share no code with the
educational Hungarian implementation, so agreement between the three is real
evidence rather than a tautology.
"""

from __future__ import annotations

import numpy as np
import pytest

from swarmlab.assignment.costs import total_cost
from swarmlab.assignment.exact import (
    BRUTE_FORCE_LIMIT,
    brute_force_assignment,
    hungarian_assignment,
)
from swarmlab.assignment.reference import scipy_assignment


def _is_permutation(vector: np.ndarray) -> bool:
    return np.array_equal(np.sort(vector), np.arange(vector.size))


@pytest.mark.parametrize("n", [1, 2, 3, 4, 5, 6])
@pytest.mark.parametrize("seed", [0, 1, 2])
def test_brute_force_matches_scipy(n: int, seed: int) -> None:
    costs = np.random.default_rng(seed).random((n, n)) * 10.0

    brute = brute_force_assignment(costs)
    reference = scipy_assignment(costs)

    assert _is_permutation(brute.target_index)
    assert total_cost(costs, brute) == pytest.approx(total_cost(costs, reference), abs=1e-9)


@pytest.mark.parametrize("n", [1, 2, 3, 4, 5, 6, 7, 8])
@pytest.mark.parametrize("seed", [0, 1, 2])
def test_hungarian_matches_scipy(n: int, seed: int) -> None:
    costs = np.random.default_rng(seed).random((n, n)) * 10.0

    hungarian = hungarian_assignment(costs)
    reference = scipy_assignment(costs)

    assert _is_permutation(hungarian.target_index)
    assert total_cost(costs, hungarian) == pytest.approx(total_cost(costs, reference), abs=1e-9)


@pytest.mark.parametrize("n", [1, 2, 3, 4, 5, 6])
def test_hungarian_matches_the_brute_force_oracle(n: int) -> None:
    costs = np.random.default_rng(7).random((n, n))

    assert total_cost(costs, hungarian_assignment(costs)) == pytest.approx(
        total_cost(costs, brute_force_assignment(costs)), abs=1e-9
    )


@pytest.mark.parametrize("solver", [hungarian_assignment, scipy_assignment])
def test_tied_integer_costs_agree_on_the_objective(solver) -> None:
    """Several optimal permutations may exist; the objective value may not."""
    costs = np.random.default_rng(11).integers(0, 3, size=(6, 6)).astype(np.float64)

    oracle = brute_force_assignment(costs)
    candidate = solver(costs)

    assert _is_permutation(candidate.target_index)
    assert total_cost(costs, candidate) == pytest.approx(total_cost(costs, oracle), abs=1e-9)


def test_hungarian_handles_negative_costs() -> None:
    """The potentials must work without a non-negativity assumption."""
    costs = np.array([[-1.0, -5.0], [-3.0, -2.0]])

    # (0, 1) and (1, 0) cost -5 + -3 = -8, better than -1 + -2 = -3.
    assert total_cost(costs, hungarian_assignment(costs)) == pytest.approx(-8.0)


def test_hungarian_returns_the_identity_for_a_diagonal_matrix() -> None:
    costs = np.array([[0.0, 9.0, 9.0], [9.0, 0.0, 9.0], [9.0, 9.0, 0.0]])

    np.testing.assert_array_equal(hungarian_assignment(costs).target_index, [0, 1, 2])


def test_hungarian_is_deterministic() -> None:
    costs = np.random.default_rng(5).random((9, 9))

    np.testing.assert_array_equal(
        hungarian_assignment(costs).target_index,
        hungarian_assignment(costs).target_index,
    )


def test_brute_force_refuses_large_instances() -> None:
    costs = np.zeros((BRUTE_FORCE_LIMIT + 1, BRUTE_FORCE_LIMIT + 1))

    with pytest.raises(ValueError, match="limited to N"):
        brute_force_assignment(costs)


@pytest.mark.parametrize("solver", [hungarian_assignment, brute_force_assignment])
def test_exact_solvers_reject_non_square_matrices(solver) -> None:
    with pytest.raises(ValueError, match="square"):
        solver(np.zeros((2, 3)))
