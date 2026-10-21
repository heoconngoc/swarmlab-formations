"""Tests for the canonical data contracts."""

from __future__ import annotations

import numpy as np
import pytest

from swarmlab.models import (
    Assignment,
    Constraints,
    Evaluation,
    Interpolation,
    Scenario,
    Trajectory,
)


def test_scenario_accepts_valid_input() -> None:
    scenario = Scenario(
        source_positions=np.zeros((3, 3)),
        target_positions=np.ones((3, 3)),
        seed=7,
    )
    assert scenario.n_agents == 3
    assert scenario.seed == 7
    assert scenario.constraints == Constraints()


def test_scenario_rejects_wrong_shape() -> None:
    with pytest.raises(ValueError, match=r"shape \(N, 3\)"):
        Scenario(
            source_positions=np.zeros((3, 2)),
            target_positions=np.zeros((3, 2)),
            seed=0,
        )


def test_scenario_rejects_non_finite_values() -> None:
    source = np.zeros((2, 3))
    source[0, 0] = np.nan
    with pytest.raises(ValueError, match="non-finite"):
        Scenario(source_positions=source, target_positions=np.zeros((2, 3)), seed=0)


def test_scenario_rejects_mismatched_shapes() -> None:
    with pytest.raises(ValueError, match="same shape"):
        Scenario(
            source_positions=np.zeros((3, 3)),
            target_positions=np.zeros((2, 3)),
            seed=0,
        )


def test_scenario_stores_read_only_copies() -> None:
    source = np.zeros((2, 3))
    scenario = Scenario(source_positions=source, target_positions=np.zeros((2, 3)), seed=0)

    source[0, 0] = 9.0
    assert scenario.source_positions[0, 0] == 0.0

    with pytest.raises(ValueError):
        scenario.source_positions[0, 0] = 5.0


def test_constraints_reject_invalid_values() -> None:
    with pytest.raises(ValueError, match="min_separation"):
        Constraints(min_separation=-1.0)
    with pytest.raises(ValueError, match="duration_s"):
        Constraints(duration_s=0.0)


def test_assignment_accepts_a_permutation() -> None:
    assignment = Assignment(target_index=np.array([2, 0, 1]))
    assert assignment.n_agents == 3
    assert np.array_equal(assignment.target_index, [2, 0, 1])


def test_assignment_rejects_non_permutations() -> None:
    with pytest.raises(ValueError, match="permutation"):
        Assignment(target_index=np.array([0, 0, 1]))
    with pytest.raises(ValueError, match="permutation"):
        Assignment(target_index=np.array([0, 2]))


def test_assignment_rejects_non_integer_values() -> None:
    with pytest.raises(ValueError, match="integer"):
        Assignment(target_index=np.array([0.5, 1.5]))


def test_assignment_is_read_only() -> None:
    assignment = Assignment(target_index=np.array([1, 0]))
    with pytest.raises(ValueError):
        assignment.target_index[0] = 1


def test_trajectory_accepts_valid_input() -> None:
    trajectory = Trajectory(
        times=np.array([[0.0, 1.0], [0.0, 2.0]]),
        positions=np.zeros((2, 2, 3)),
    )
    assert trajectory.n_agents == 2
    assert trajectory.n_waypoints == 2
    assert trajectory.interpolation is Interpolation.LINEAR


def test_trajectory_rejects_shape_mismatch() -> None:
    with pytest.raises(ValueError, match="does not match"):
        Trajectory(times=np.zeros((2, 2)), positions=np.zeros((2, 3, 3)))


def test_trajectory_rejects_non_monotonic_times() -> None:
    with pytest.raises(ValueError, match="strictly increasing"):
        Trajectory(times=np.array([[0.0, 0.0]]), positions=np.zeros((1, 2, 3)))


def test_evaluation_defaults_to_empty_metadata() -> None:
    evaluation = Evaluation(
        total_travel_length=1.0,
        per_agent_travel_length=np.array([0.5, 0.5]),
        makespan_s=10.0,
        n_agents=2,
    )
    assert evaluation.metadata == {}
