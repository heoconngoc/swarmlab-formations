"""Tests for the linear baseline trajectory and the position sampler."""

from __future__ import annotations

import numpy as np
import pytest

from swarmlab.assignment.random import random_assignment
from swarmlab.models import Constraints, Interpolation, Scenario, Trajectory
from swarmlab.trajectories.interpolate import sample_positions
from swarmlab.trajectories.linear import linear_trajectory


def _scenario(n: int = 5, duration_s: float = 10.0) -> Scenario:
    source = np.linspace(-1.0, 1.0, n * 3).reshape(n, 3)
    target = -source
    return Scenario(
        source_positions=source,
        target_positions=target,
        seed=0,
        constraints=Constraints(duration_s=duration_s),
    )


def test_trajectory_endpoints_match_the_scenario() -> None:
    scenario = _scenario()
    assignment = random_assignment(scenario.n_agents, seed=5)
    trajectory = linear_trajectory(scenario, assignment)

    assert trajectory.n_waypoints == 2
    assert trajectory.interpolation is Interpolation.LINEAR
    np.testing.assert_array_equal(trajectory.positions[:, 0], scenario.source_positions)
    np.testing.assert_array_equal(
        trajectory.positions[:, -1],
        scenario.target_positions[assignment.target_index],
    )


def test_trajectory_times_span_the_duration() -> None:
    scenario = _scenario(duration_s=7.5)
    assignment = random_assignment(scenario.n_agents, seed=5)
    trajectory = linear_trajectory(scenario, assignment)

    assert trajectory.times.shape == (scenario.n_agents, 2)
    np.testing.assert_allclose(trajectory.times[:, 0], 0.0)
    np.testing.assert_allclose(trajectory.times[:, -1], 7.5)


def test_trajectory_rejects_a_mismatched_assignment() -> None:
    scenario = _scenario(n=5)
    assignment = random_assignment(3, seed=5)
    with pytest.raises(ValueError, match="covers 3 agents"):
        linear_trajectory(scenario, assignment)


def test_sampler_returns_the_start_positions_at_t_zero() -> None:
    scenario = _scenario()
    assignment = random_assignment(scenario.n_agents, seed=5)
    trajectory = linear_trajectory(scenario, assignment)

    np.testing.assert_allclose(
        sample_positions(trajectory, 0.0),
        scenario.source_positions,
        atol=1e-12,
    )


def test_sampler_returns_the_goals_at_the_end() -> None:
    scenario = _scenario()
    assignment = random_assignment(scenario.n_agents, seed=5)
    trajectory = linear_trajectory(scenario, assignment)

    np.testing.assert_allclose(
        sample_positions(trajectory, scenario.constraints.duration_s),
        scenario.target_positions[assignment.target_index],
        atol=1e-12,
    )


def test_sampler_interpolates_linearly_in_the_middle() -> None:
    scenario = _scenario(duration_s=10.0)
    assignment = random_assignment(scenario.n_agents, seed=5)
    trajectory = linear_trajectory(scenario, assignment)

    midpoint = sample_positions(trajectory, 5.0)
    expected = 0.5 * (
        scenario.source_positions + scenario.target_positions[assignment.target_index]
    )
    np.testing.assert_allclose(midpoint, expected, atol=1e-12)


def test_sampler_clamps_outside_the_time_span() -> None:
    scenario = _scenario(duration_s=10.0)
    assignment = random_assignment(scenario.n_agents, seed=5)
    trajectory = linear_trajectory(scenario, assignment)

    np.testing.assert_allclose(
        sample_positions(trajectory, -5.0),
        scenario.source_positions,
        atol=1e-12,
    )
    np.testing.assert_allclose(
        sample_positions(trajectory, 99.0),
        scenario.target_positions[assignment.target_index],
        atol=1e-12,
    )


def test_sampler_handles_asynchronous_waypoint_times() -> None:
    trajectory = Trajectory(
        times=np.array([[0.0, 4.0], [0.0, 8.0]]),
        positions=np.array(
            [
                [[0.0, 0.0, 0.0], [1.0, 0.0, 0.0]],
                [[0.0, 0.0, 0.0], [0.0, 2.0, 0.0]],
            ]
        ),
    )
    positions = sample_positions(trajectory, 2.0)
    np.testing.assert_allclose(positions[0], [0.5, 0.0, 0.0], atol=1e-12)
    np.testing.assert_allclose(positions[1], [0.0, 0.5, 0.0], atol=1e-12)


def test_sampler_rejects_unsupported_interpolation() -> None:
    trajectory = Trajectory(
        times=np.array([[0.0, 1.0]]),
        positions=np.zeros((1, 2, 3)),
        interpolation=Interpolation.HOLD,
    )
    with pytest.raises(NotImplementedError, match="LINEAR"):
        sample_positions(trajectory, 0.5)
