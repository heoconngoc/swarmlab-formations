"""Trajectory generation.

A trajectory is a list of waypoints per agent, tagged with the times at which
those waypoints are reached. Phase 1 provides the linear baseline: every agent
moves along the straight segment from its start position to its assigned goal.
"""

from swarmlab.trajectories.interpolate import sample_positions
from swarmlab.trajectories.linear import linear_trajectory

__all__ = ["linear_trajectory", "sample_positions"]
