"""Plotly-based visualization.

This is the only layer of the package that is allowed to import ``plotly``.
The algorithm core under ``formations``, ``assignment``, ``trajectories`` and
``evaluation`` must stay free of any plotting dependency.
"""

from swarmlab.visualization.viewer import render_transition, save_transition

__all__ = ["render_transition", "save_transition"]
