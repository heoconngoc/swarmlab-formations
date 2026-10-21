"""SwarmLab: formation assignment, trajectory planning, and collision analysis for drone swarms.

The top level package exposes the canonical data contracts only. It never
imports :mod:`swarmlab.visualization`, so ``import swarmlab`` stays free of
Plotly and of any other presentation dependency.

See ``docs/STATUS.md`` for what is implemented and ``docs/ARCHITECTURE.md`` for
the module contracts.
"""

from swarmlab.models import (
    Assignment,
    Constraints,
    Evaluation,
    Interpolation,
    Scenario,
    Trajectory,
)

__version__ = "0.1.0"

__all__ = [
    "Assignment",
    "Constraints",
    "Evaluation",
    "Interpolation",
    "Scenario",
    "Trajectory",
    "__version__",
]
