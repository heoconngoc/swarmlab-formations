"""Linear baseline trajectory.

Every agent moves at constant speed along the straight segment that joins its
start position to its assigned goal. The whole transition takes the scenario
duration ``T``, so all agents share the same start time and the same arrival
time.

The resulting path is the shortest possible path for a given assignment, which
makes the linear baseline the reference against which longer, safer paths are
compared later.
"""

from __future__ import annotations

import numpy as np

from swarmlab.models import Assignment, Interpolation, Scenario, Trajectory

__all__ = ["linear_trajectory"]


def linear_trajectory(scenario: Scenario, assignment: Assignment) -> Trajectory:
    """Build the straight-line transition for ``scenario`` under ``assignment``.

    Args:
        scenario: The transition problem. Its ``source_positions`` give the
            start points and its ``constraints.duration_s`` gives the duration.
        assignment: The bijection from agents to targets.

    Returns:
        A :class:`~swarmlab.models.Trajectory` with ``M == 2`` waypoints per
        agent: the start position at ``t = 0`` and the goal at ``t = T``.

    Raises:
        ValueError: If ``assignment`` does not cover the scenario's agents.
    """
    n = scenario.n_agents
    if assignment.n_agents != n:
        raise ValueError(f"assignment covers {assignment.n_agents} agents but the scenario has {n}")

    duration = scenario.constraints.duration_s
    times = np.tile(np.array([0.0, duration], dtype=np.float64), (n, 1))

    source = scenario.source_positions
    goal = scenario.target_positions[assignment.target_index]
    positions = np.stack([source, goal], axis=1)

    return Trajectory(
        times=times,
        positions=positions,
        interpolation=Interpolation.LINEAR,
    )
