"""Mapping agents to targets.

Phase 1 only ships a random assignment. It is a *baseline*, not an optimizer:
it exists so that the trajectory and evaluation layers can be exercised
end-to-end before the optimization work of Phase 2 starts.
"""

from swarmlab.assignment.random import random_assignment

__all__ = ["random_assignment"]
