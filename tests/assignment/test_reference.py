"""Tests for the SciPy reference solver."""

from __future__ import annotations

import numpy as np
import pytest

from swarmlab.assignment.costs import total_cost
from swarmlab.assignment.reference import scipy_assignment


def test_scipy_solves_a_known_matrix() -> None:
    costs = np.array([[4.0, 1.0, 3.0], [2.0, 0.0, 5.0], [3.0, 2.0, 2.0]])

    assignment = scipy_assignment(costs)

    np.testing.assert_array_equal(assignment.target_index, [1, 0, 2])
    assert total_cost(costs, assignment) == pytest.approx(5.0)


def test_scipy_returns_a_bijection() -> None:
    costs = np.random.default_rng(2).random((15, 15))

    assignment = scipy_assignment(costs)

    assert np.array_equal(np.sort(assignment.target_index), np.arange(15))


def test_scipy_handles_a_single_agent() -> None:
    assignment = scipy_assignment(np.array([[7.5]]))

    np.testing.assert_array_equal(assignment.target_index, [0])


def test_scipy_rejects_non_square_matrices() -> None:
    with pytest.raises(ValueError, match="square"):
        scipy_assignment(np.zeros((3, 4)))
