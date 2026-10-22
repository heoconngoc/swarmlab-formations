"""Tests for the Phase 1 evaluation metrics."""

from __future__ import annotations

import numpy as np
import pytest

from swarmlab.assignment.random import random_assignment
from swarmlab.evaluation.metrics import evaluate_trajectory, travel_lengths
from swarmlab.models import Constraints, Interpolation, Scenario, Trajectory
from swarmlab.trajectories.linear import linear_trajectory


def _scenario(n: int = 6) -> Scenario:
    source = np.linspace(-1.0, 1.0, n * 3).reshape(n, 3)
    target = np.roll(source, 1, axis=0)
    return Scenario(
        source_positions=source,
        target_positions=target,
        seed=1,
        constraints=Constraints(duration_s=12.0),
    )


def test_travel_lengths_match_the_direct_distances() -> None:
    scenario = _scenario()
    assignment = random_assignment(scenario.n_agents, seed=2)
    trajectory = linear_trajectory(scenario, assignment)

    expected = np.linalg.norm(
        scenario.target_positions[assignment.target_index] - scenario.source_positions,
        axis=1,
    )
    np.testing.assert_allclose(travel_lengths(trajectory), expected, atol=1e-12)


def test_evaluate_trajectory_reports_the_totals() -> None:
    scenario = _scenario()
    assignment = random_assignment(scenario.n_agents, seed=2)
    trajectory = linear_trajectory(scenario, assignment)
    evaluation = evaluate_trajectory(scenario, assignment, trajectory, assignment_method="random")

    per_agent = travel_lengths(trajectory)
    assert evaluation.n_agents == scenario.n_agents
    np.testing.assert_allclose(evaluation.per_agent_travel_length, per_agent, atol=1e-12)
    assert evaluation.total_travel_length == pytest.approx(float(per_agent.sum()))
    assert evaluation.makespan_s == pytest.approx(12.0)
    assert evaluation.metadata["assignment_method"] == "random"
    assert evaluation.metadata["trajectory_method"] == "linear"


def test_evaluate_trajectory_does_not_guess_the_assignment_method() -> None:
    """An unknown solver must stay unknown instead of being labelled random."""
    scenario = _scenario()
    assignment = random_assignment(scenario.n_agents, seed=2)
    trajectory = linear_trajectory(scenario, assignment)

    evaluation = evaluate_trajectory(scenario, assignment, trajectory)

    assert evaluation.metadata["assignment_method"] == "unspecified"


def test_evaluate_trajectory_rejects_a_mismatched_trajectory() -> None:
    scenario = _scenario(n=6)
    trajectory = Trajectory(
        times=np.array([[0.0, 1.0]] * 3),
        positions=np.zeros((3, 2, 3)),
    )
    with pytest.raises(ValueError, match="covers 3 agents"):
        evaluate_trajectory(scenario, random_assignment(6, seed=0), trajectory)


def test_metrics_reject_unsupported_interpolation() -> None:
    trajectory = Trajectory(
        times=np.array([[0.0, 1.0]]),
        positions=np.zeros((1, 2, 3)),
        interpolation=Interpolation.HOLD,
    )
    with pytest.raises(NotImplementedError, match="LINEAR"):
        travel_lengths(trajectory)
