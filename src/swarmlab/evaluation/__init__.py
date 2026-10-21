"""Evaluation metrics.

Phase 1 measures how far the agents travel and how long the transition takes.
Collision metrics are added in Phase 3; nothing in this module makes any
safety claim.
"""

from swarmlab.evaluation.metrics import evaluate_trajectory, travel_lengths

__all__ = ["evaluate_trajectory", "travel_lengths"]
