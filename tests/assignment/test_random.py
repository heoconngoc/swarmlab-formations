"""Tests for the seeded random assignment."""

from __future__ import annotations

import numpy as np
import pytest

from swarmlab.assignment.random import random_assignment


@pytest.mark.parametrize("n", [1, 2, 10, 100])
def test_assignment_is_a_permutation(n: int) -> None:
    assignment = random_assignment(n, seed=3)
    assert assignment.n_agents == n
    np.testing.assert_array_equal(np.sort(assignment.target_index), np.arange(n))


def test_assignment_is_reproducible() -> None:
    np.testing.assert_array_equal(
        random_assignment(50, seed=11).target_index,
        random_assignment(50, seed=11).target_index,
    )


def test_different_seeds_give_different_assignments() -> None:
    first = random_assignment(100, seed=1).target_index
    second = random_assignment(100, seed=2).target_index
    assert not np.array_equal(first, second)


def test_assignment_rejects_invalid_sizes() -> None:
    with pytest.raises(ValueError, match="positive"):
        random_assignment(0, seed=0)
