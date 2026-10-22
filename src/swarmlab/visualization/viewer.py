"""Interactive viewer for a Phase 1 transition.

The figure shows the swarm moving from the source formation to the target
formation:

* one marker per agent, animated over the duration of the transition;
* the straight path of one highlighted agent, drawn as a line;
* a red warning, because nothing in Phase 1 checks for collisions.

The viewer is presentation only. It reads a trajectory and never writes one, so
a bug in the visualization can never change a metric.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import plotly.graph_objects as go

from swarmlab.models import Scenario, Trajectory
from swarmlab.trajectories.interpolate import sample_positions

__all__ = ["render_transition", "save_transition"]

_AGENT_COLOR = "#1f77b4"
_PATH_COLOR = "#ff7f0e"
_WARNING = "NOT collision-safe - Phase 1 does not check any separation constraint"


def _agent_trace(positions: np.ndarray, name: str) -> go.Scatter3d:
    """Return a marker trace for a set of agent positions."""
    return go.Scatter3d(
        x=positions[:, 0],
        y=positions[:, 1],
        z=positions[:, 2],
        mode="markers",
        name=name,
        marker={"size": 3.5, "color": _AGENT_COLOR, "opacity": 0.85},
        hoverinfo="x+y+z",
    )


def render_transition(
    scenario: Scenario,
    trajectory: Trajectory,
    *,
    selected_agent: int = 0,
    n_frames: int = 60,
    title: str | None = None,
) -> go.Figure:
    """Build the animated figure of a transition.

    Args:
        scenario: The scenario that produced the trajectory.
        trajectory: The trajectory to visualize.
        selected_agent: Index of the agent whose path is drawn as a line.
        n_frames: Number of animation frames. Fewer frames means a smaller
            HTML file.
        title: Optional figure title.

    Returns:
        A ``plotly.graph_objects.Figure`` ready to be shown or written out.

    Raises:
        ValueError: If ``selected_agent`` is out of range or ``n_frames`` is
            smaller than two.
    """
    n_agents = trajectory.n_agents
    if not 0 <= selected_agent < n_agents:
        raise ValueError(f"selected_agent must be in range({n_agents}), got {selected_agent}")
    if n_frames < 2:
        raise ValueError(f"n_frames must be at least 2, got {n_frames}")

    start_time = float(trajectory.times[:, 0].min())
    end_time = float(trajectory.times[:, -1].max())
    frame_times = np.linspace(start_time, end_time, n_frames)
    # Frame names are the only stable handle on a frame: Plotly sliders and
    # animation buttons address frames by name, never by index or by time.
    frame_names = [f"t{index:03d}" for index in range(n_frames)]
    # Playback advances at roughly real time: T seconds spread over n_frames.
    frame_duration_ms = max(20, round(1000.0 * (end_time - start_time) / n_frames))

    initial = sample_positions(trajectory, start_time)
    path = trajectory.positions[selected_agent]
    path_trace = go.Scatter3d(
        x=path[:, 0],
        y=path[:, 1],
        z=path[:, 2],
        mode="lines",
        name=f"agent {selected_agent} path",
        line={"color": _PATH_COLOR, "width": 4},
    )

    frames = [
        go.Frame(
            data=[_agent_trace(sample_positions(trajectory, float(time)), "agents")],
            name=name,
        )
        for name, time in zip(frame_names, frame_times, strict=True)
    ]

    figure = go.Figure(
        data=[_agent_trace(initial, "agents"), path_trace],
        frames=frames,
    )
    figure.update_layout(
        title=title
        or (
            f"SwarmLab Phase 1 - N={n_agents}, "
            f"{scenario.constraints.duration_s:g}s, seed={scenario.seed}"
        ),
        scene={
            "aspectmode": "data",
            "xaxis": {"title": "x", "range": [-1.05, 1.05]},
            "yaxis": {"title": "y", "range": [-1.05, 1.05]},
            "zaxis": {"title": "z", "range": [-1.05, 1.05]},
        },
        margin={"l": 0, "r": 0, "b": 0, "t": 60},
        legend={"x": 0.01, "y": 0.99},
        sliders=[
            {
                "active": 0,
                "currentvalue": {"prefix": "t = ", "suffix": " s"},
                "pad": {"t": 40},
                "x": 0.1,
                "len": 0.8,
                "steps": [
                    {
                        "label": f"{time:.2f}",
                        "method": "animate",
                        "args": [
                            [name],
                            {
                                "mode": "immediate",
                                "frame": {"duration": 0, "redraw": True},
                                "transition": {"duration": 0},
                            },
                        ],
                    }
                    for name, time in zip(frame_names, frame_times, strict=True)
                ],
            }
        ],
        updatemenus=[
            {
                "type": "buttons",
                "showactive": False,
                "x": 0.1,
                "y": -0.05,
                "xanchor": "right",
                "yanchor": "top",
                "pad": {"r": 10, "t": 40},
                "buttons": [
                    {
                        "label": "Play",
                        "method": "animate",
                        "args": [
                            [None],
                            {
                                "fromcurrent": True,
                                "frame": {
                                    "duration": frame_duration_ms,
                                    "redraw": True,
                                },
                                "transition": {"duration": 0},
                            },
                        ],
                    },
                    {
                        "label": "Pause",
                        "method": "animate",
                        "args": [
                            [None],
                            {
                                "mode": "immediate",
                                "frame": {"duration": 0, "redraw": False},
                                "transition": {"duration": 0},
                            },
                        ],
                    },
                ],
            }
        ],
    )
    figure.add_annotation(
        text=_WARNING,
        xref="paper",
        yref="paper",
        x=0.5,
        y=1.06,
        showarrow=False,
        font={"size": 14, "color": "#d62728"},
    )
    return figure


def save_transition(
    scenario: Scenario,
    trajectory: Trajectory,
    path: str | Path,
    *,
    selected_agent: int = 0,
    n_frames: int = 60,
    title: str | None = None,
) -> Path:
    """Render a transition and write it to an HTML file.

    Args:
        scenario: The scenario that produced the trajectory.
        trajectory: The trajectory to visualize.
        path: Destination of the HTML file. Parent directories are created.
        selected_agent: Index of the agent whose path is drawn as a line.
        n_frames: Number of animation frames.
        title: Optional figure title.

    Returns:
        The path of the written file.
    """
    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    figure = render_transition(
        scenario,
        trajectory,
        selected_agent=selected_agent,
        n_frames=n_frames,
        title=title,
    )
    figure.write_html(destination, include_plotlyjs="cdn")
    return destination
