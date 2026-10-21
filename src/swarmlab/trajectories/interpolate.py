"""Reconstructing positions at an arbitrary time.

The trajectory stores waypoints; a viewer or an evaluator often needs the
position of every agent at a specific instant. This module interpolates
between the two waypoints that surround that instant.

The lookup is fully vectorized: the segment index of every agent is found at
once, so sampling a frame costs one pass over the ``(N, M)`` time grid rather
than one Python loop iteration per agent.
"""

from __future__ import annotations

import numpy as np

from swarmlab.models import FloatArray, Interpolation, Trajectory

__all__ = ["sample_positions"]


def sample_positions(trajectory: Trajectory, time: float) -> FloatArray:
    """Return the position of every agent at ``time``.

    Args:
        trajectory: The trajectory to sample. Only
            :attr:`~swarmlab.models.Interpolation.LINEAR` is supported.
        time: The instant of interest, in seconds. Values outside the
            trajectory's time span are clamped to the first or last waypoint.

    Returns:
        An ``(N, 3)`` array with the interpolated positions.

    Raises:
        NotImplementedError: If the trajectory uses another interpolation mode.
    """
    if trajectory.interpolation is not Interpolation.LINEAR:
        raise NotImplementedError(
            f"sample_positions only supports LINEAR interpolation, got {trajectory.interpolation}"
        )

    times = trajectory.times
    positions = trajectory.positions
    n_agents, n_waypoints = times.shape

    if n_waypoints == 1:
        return np.array(positions[:, 0], copy=True)

    # Index of the last waypoint at or before ``time``, minus one: this is the
    # first index of the segment that contains ``time``.
    segment = np.clip(np.count_nonzero(times < time, axis=1) - 1, 0, n_waypoints - 2)
    rows = np.arange(n_agents)

    t_start = times[rows, segment]
    t_end = times[rows, segment + 1]
    span = t_end - t_start
    ratio = np.divide(
        time - t_start,
        span,
        out=np.zeros_like(span),
        where=span > 0.0,
    )
    ratio = np.clip(ratio, 0.0, 1.0)

    start = positions[rows, segment]
    end = positions[rows, segment + 1]
    return start + ratio[:, None] * (end - start)
