"""Travel-length and timing metrics.

The metrics are deliberately simple and fully vectorized: the segment lengths of
every agent are obtained with one NumPy expression, so evaluating a swarm of
``N`` agents costs ``O(N * M)`` and not ``O(N * M)`` Python iterations.

Nothing here checks whether the agents collide. The linear baseline is a
geometric shortest-path reference, not a safe plan.
"""

from __future__ import annotations

import numpy as np

from swarmlab.models import (
    Assignment,
    Evaluation,
    FloatArray,
    Interpolation,
    Scenario,
    Trajectory,
)

__all__ = ["evaluate_trajectory", "travel_lengths"]


def travel_lengths(trajectory: Trajectory) -> FloatArray:
    """Return the total distance travelled by each agent.

    Args:
        trajectory: The trajectory to measure.

    Returns:
        An ``(N,)`` array with the summed length of each agent's segments.

    Raises:
        NotImplementedError: If the trajectory uses another interpolation mode.
    """
    if trajectory.interpolation is not Interpolation.LINEAR:
        raise NotImplementedError(
            f"travel_lengths only supports LINEAR interpolation, got {trajectory.interpolation}"
        )

    deltas = np.diff(trajectory.positions, axis=1)
    segment_lengths = np.linalg.norm(deltas, axis=2)
    return segment_lengths.sum(axis=1)


def evaluate_trajectory(
    scenario: Scenario,
    assignment: Assignment,
    trajectory: Trajectory,
    *,
    assignment_method: str = "unspecified",
) -> Evaluation:
    """Compute the Phase 1 metrics of a trajectory.

    Args:
        scenario: The transition problem that was solved.
        assignment: The bijection that was used.
        trajectory: The trajectory to evaluate.
        assignment_method: Name of the solver that produced ``assignment``.
            Recorded in the metadata. The default ``"unspecified"`` keeps an
            unknown method visibly unknown instead of guessing ``"random"``.

    Returns:
        An :class:`~swarmlab.models.Evaluation` with the total travel length,
        the per-agent travel lengths, the makespan, and method metadata.

    Raises:
        ValueError: If the trajectory does not cover the scenario's agents.
        NotImplementedError: If the trajectory uses another interpolation mode.
    """
    if trajectory.n_agents != scenario.n_agents:
        raise ValueError(
            f"trajectory covers {trajectory.n_agents} agents, "
            f"but the scenario has {scenario.n_agents}"
        )

    per_agent = travel_lengths(trajectory)
    start_time = float(trajectory.times[:, 0].min())
    end_time = float(trajectory.times[:, -1].max())

    return Evaluation(
        total_travel_length=float(per_agent.sum()),
        per_agent_travel_length=per_agent,
        makespan_s=end_time - start_time,
        n_agents=scenario.n_agents,
        metadata={
            "assignment_method": assignment_method,
            "trajectory_method": "linear",
            "interpolation": trajectory.interpolation.value,
            "scenario_seed": str(scenario.seed),
            "n_agents": str(scenario.n_agents),
        },
    )
