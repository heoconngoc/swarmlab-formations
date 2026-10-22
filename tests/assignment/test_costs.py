"""Tests for the cost-matrix layer."""

from __future__ import annotations

import numpy as np
import pytest

from swarmlab.assignment.costs import (
    COST_FUNCTIONS,
    as_square_cost_matrix,
    euclidean_distance_costs,
    squared_distance_costs,
    total_cost,
)
from swarmlab.models import Assignment


def _sample() -> tuple[np.ndarray, np.ndarray]:
    sources = np.array([[0.0, 0.0, 0.0], [1.0, 0.0, 0.0], [0.0, 2.0, 0.0]])
    targets = np.array([[3.0, 0.0, 0.0], [0.0, 0.0, 4.0], [1.0, 1.0, 1.0]])
    return sources, targets


def test_euclidean_costs_match_the_definition() -> None:
    sources, targets = _sample()
    costs = euclidean_distance_costs(sources, targets)

    assert costs.shape == (3, 3)
    for i in range(3):
        for j in range(3):
            expected = np.linalg.norm(sources[i] - targets[j])
            assert costs[i, j] == pytest.approx(expected, abs=1e-12)


def test_squared_costs_are_the_square_of_euclidean_costs() -> None:
    sources, targets = _sample()
    squared = squared_distance_costs(sources, targets)
    euclidean = euclidean_distance_costs(sources, targets)

    np.testing.assert_allclose(squared, euclidean**2, rtol=1e-12, atol=0.0)


def test_cost_matrix_is_zero_on_the_diagonal_for_identical_point_sets() -> None:
    points = np.array([[0.0, 0.0, 0.0], [1.0, 0.0, 0.0], [0.0, 0.0, -1.0]])
    costs = euclidean_distance_costs(points, points)

    np.testing.assert_allclose(np.diag(costs), 0.0, atol=1e-12)
    assert costs.min() == pytest.approx(0.0, abs=1e-12)


def test_total_cost_sums_the_selected_entries() -> None:
    costs = np.array([[1.0, 2.0, 3.0], [4.0, 5.0, 6.0], [7.0, 8.0, 9.0]])
    assignment = Assignment(target_index=np.array([2, 0, 1]))

    assert total_cost(costs, assignment) == pytest.approx(3.0 + 4.0 + 8.0)


def test_total_cost_rejects_a_size_mismatch() -> None:
    costs = np.zeros((2, 2))
    assignment = Assignment(target_index=np.array([0, 1, 2]))

    with pytest.raises(ValueError, match="do not match"):
        total_cost(costs, assignment)


def test_cost_functions_registry_is_complete() -> None:
    assert set(COST_FUNCTIONS) == {"euclidean_distance", "squared_distance"}
    assert COST_FUNCTIONS["euclidean_distance"] is euclidean_distance_costs
    assert COST_FUNCTIONS["squared_distance"] is squared_distance_costs


@pytest.mark.parametrize("builder", [euclidean_distance_costs, squared_distance_costs])
def test_cost_builders_reject_bad_input(builder) -> None:
    with pytest.raises(ValueError, match="shape"):
        builder(np.zeros((4, 2)), np.zeros((4, 2)))
    with pytest.raises(ValueError, match="finite"):
        builder(np.array([[0.0, 0.0, np.nan]]), np.zeros((1, 3)))
    with pytest.raises(ValueError, match="same shape"):
        builder(np.zeros((2, 3)), np.zeros((3, 3)))


def test_as_square_cost_matrix_validates() -> None:
    with pytest.raises(ValueError, match="square"):
        as_square_cost_matrix(np.zeros((2, 3)))
    with pytest.raises(ValueError, match="empty"):
        as_square_cost_matrix(np.zeros((0, 0)))
    with pytest.raises(ValueError, match="finite"):
        as_square_cost_matrix(np.array([[0.0, np.inf], [0.0, 0.0]]))

    matrix = as_square_cost_matrix(np.eye(2))
    assert matrix.dtype == np.float64
