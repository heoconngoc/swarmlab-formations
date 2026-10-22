"""Tests for the two greedy heuristics."""

from __future__ import annotations

import numpy as np
import pytest

from swarmlab.assignment.costs import euclidean_distance_costs, total_cost
from swarmlab.assignment.greedy import greedy_assignment, greedy_pair_assignment
from swarmlab.assignment.reference import scipy_assignment
from swarmlab.experiments.phase1 import build_scenario


def _permutation_is_valid(assignment, n: int) -> bool:
    return np.array_equal(np.sort(assignment.target_index), np.arange(n))


@pytest.mark.parametrize("n", [1, 2, 5, 20])
def test_greedy_returns_a_valid_bijection(n: int) -> None:
    rng = np.random.default_rng(0)
    costs = rng.random((n, n))

    assert _permutation_is_valid(greedy_assignment(costs), n)
    assert _permutation_is_valid(greedy_pair_assignment(costs), n)


def test_greedy_is_deterministic() -> None:
    rng = np.random.default_rng(3)
    costs = rng.random((12, 12))

    np.testing.assert_array_equal(
        greedy_assignment(costs).target_index,
        greedy_assignment(costs).target_index,
    )
    np.testing.assert_array_equal(
        greedy_pair_assignment(costs).target_index,
        greedy_pair_assignment(costs).target_index,
    )


def test_agent_order_greedy_is_not_optimal() -> None:
    """Agent 0 grabs target 0, forcing agent 1 onto a very expensive target."""
    costs = np.array([[1.0, 2.0], [1.0, 100.0]])

    greedy = greedy_assignment(costs)
    np.testing.assert_array_equal(greedy.target_index, [0, 1])
    assert total_cost(costs, greedy) == pytest.approx(101.0)
    assert total_cost(costs, scipy_assignment(costs)) == pytest.approx(3.0)


def test_pair_greedy_beats_agent_order_on_a_forced_example() -> None:
    """The globally cheapest pair belongs to the second agent."""
    costs = np.array([[5.0, 6.0], [1.0, 100.0]])

    np.testing.assert_array_equal(greedy_assignment(costs).target_index, [0, 1])
    np.testing.assert_array_equal(greedy_pair_assignment(costs).target_index, [1, 0])
    assert total_cost(costs, greedy_assignment(costs)) == pytest.approx(105.0)
    assert total_cost(costs, greedy_pair_assignment(costs)) == pytest.approx(7.0)


def test_greedy_ties_pick_the_lowest_target_index() -> None:
    costs = np.zeros((4, 4))

    np.testing.assert_array_equal(greedy_assignment(costs).target_index, [0, 1, 2, 3])
    np.testing.assert_array_equal(greedy_pair_assignment(costs).target_index, [0, 1, 2, 3])


def test_greedy_respects_the_optimal_bound_on_a_real_instance() -> None:
    """Neither greedy rule may beat the exact solver on a real scenario."""
    scenario = build_scenario(40, seed=1)
    costs = euclidean_distance_costs(scenario.source_positions, scenario.target_positions)

    first = greedy_assignment(costs)
    second = greedy_pair_assignment(costs)

    assert _permutation_is_valid(first, 40)
    assert _permutation_is_valid(second, 40)
    optimum = total_cost(costs, scipy_assignment(costs))
    assert total_cost(costs, first) >= optimum - 1e-9
    assert total_cost(costs, second) >= optimum - 1e-9


@pytest.mark.parametrize("solver", [greedy_assignment, greedy_pair_assignment])
def test_greedy_rejects_non_square_matrices(solver) -> None:
    with pytest.raises(ValueError, match="square"):
        solver(np.zeros((2, 3)))
