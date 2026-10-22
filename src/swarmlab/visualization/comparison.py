"""Comparative figures for the Phase 2 assignment experiment.

Two views, both presentation only:

* :func:`render_assignment_comparison` draws the straight paths produced by
  several assignments of the same scenario, one 3D scene per method. Path
  crossing is exactly what an assignment solver is supposed to remove, so the
  difference between random and optimal is visible without reading a table.
* :func:`render_benchmark_curves` plots assignment cost and solver time against
  swarm size from saved benchmark rows. Every measured seed is shown as a faint
  point and the median is drawn as a line, so dispersion is not hidden.

Neither function measures anything. Anything a figure claims must already be in
the rows or in the scenario it was given.
"""

from __future__ import annotations

import math
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any

import numpy as np
import plotly.colors as pc
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from swarmlab.models import Assignment, Scenario

__all__ = [
    "render_assignment_comparison",
    "render_benchmark_curves",
    "save_figure",
]

_SOURCE_COLOR = "#7f7f7f"
_PALETTE = pc.qualitative.Plotly


def _cycle(index: int) -> str:
    return _PALETTE[index % len(_PALETTE)]


def _joined_paths(
    scenario: Scenario,
    assignment: Assignment,
    max_paths: int,
) -> tuple[list[float], list[float], list[float]]:
    """Return one polyline of straight agent paths, separated by ``NaN``.

    A single trace keeps the HTML small; ``NaN`` breaks the line between
    agents so the paths do not connect to each other.
    """
    count = min(max_paths, scenario.n_agents)
    starts = scenario.source_positions[:count]
    goals = scenario.target_positions[assignment.target_index][:count]

    x: list[float] = []
    y: list[float] = []
    z: list[float] = []
    for start, goal in zip(starts, goals, strict=True):
        x.extend([float(start[0]), float(goal[0]), float("nan")])
        y.extend([float(start[1]), float(goal[1]), float("nan")])
        z.extend([float(start[2]), float(goal[2]), float("nan")])
    return x, y, z


def render_assignment_comparison(
    scenario: Scenario,
    assignments: Mapping[str, Assignment],
    *,
    max_paths: int = 25,
    title: str | None = None,
) -> go.Figure:
    """Draw the paths of several assignments side by side.

    Args:
        scenario: The shared transition problem.
        assignments: Method name to bijection. Order is preserved.
        max_paths: Number of agents whose paths are drawn per method. Paths are
            only a diagnostic, so drawing all of them at ``N = 1000`` would
            produce an unreadable, slow page.
        title: Optional figure title.

    Returns:
        A Plotly figure with one 3D scene per assignment.

    Raises:
        ValueError: If ``assignments`` is empty or ``max_paths`` is not positive.
    """
    if not assignments:
        raise ValueError("assignments must contain at least one method")
    if max_paths < 1:
        raise ValueError(f"max_paths must be positive, got {max_paths}")

    names = list(assignments)
    n_methods = len(names)
    cols = 1 if n_methods == 1 else 2
    rows = math.ceil(n_methods / cols)
    specs = [[{"type": "scene"} for _ in range(cols)] for _ in range(rows)]

    figure = make_subplots(
        rows=rows,
        cols=cols,
        specs=specs,
        subplot_titles=names,
        horizontal_spacing=0.02,
        vertical_spacing=0.02,
    )

    source = scenario.source_positions
    for index, name in enumerate(names):
        row = index // cols + 1
        col = index % cols + 1
        assignment = assignments[name]

        figure.add_trace(
            go.Scatter3d(
                x=source[:, 0],
                y=source[:, 1],
                z=source[:, 2],
                mode="markers",
                marker={"size": 2.5, "color": _SOURCE_COLOR, "opacity": 0.5},
                name="sources",
                showlegend=index == 0,
                hoverinfo="skip",
            ),
            row=row,
            col=col,
        )

        x, y, z = _joined_paths(scenario, assignment, max_paths)
        figure.add_trace(
            go.Scatter3d(
                x=x,
                y=y,
                z=z,
                mode="lines",
                line={"width": 2, "color": _cycle(index)},
                name=name,
                hoverinfo="skip",
            ),
            row=row,
            col=col,
        )

    for index in range(n_methods):
        scene = "scene" if index == 0 else f"scene{index + 1}"
        figure.update_layout(
            {
                scene: {
                    "aspectmode": "data",
                    "xaxis": {"visible": False},
                    "yaxis": {"visible": False},
                    "zaxis": {"visible": False},
                }
            }
        )

    drawn = min(max_paths, scenario.n_agents)
    figure.update_layout(
        title=title
        or (
            f"Assignment comparison - N={scenario.n_agents}, seed={scenario.seed}, "
            f"{drawn} paths drawn per method"
        ),
        margin={"l": 0, "r": 0, "b": 0, "t": 70},
        legend={"x": 0.01, "y": 0.99},
    )
    return figure


def _group_by_size_and_method(
    rows: Sequence[Mapping[str, Any]],
) -> dict[str, dict[int, list[dict]]]:
    """Group successful benchmark rows as ``{method: {n: [row, ...]}}``."""
    grouped: dict[str, dict[int, list[dict]]] = {}
    for row in rows:
        if row.get("status") != "ok":
            continue
        method = str(row["method"])
        size = int(float(row["n"]))
        grouped.setdefault(method, {}).setdefault(size, []).append(dict(row))
    return grouped


def render_benchmark_curves(
    rows: Sequence[Mapping[str, Any]],
    *,
    title: str | None = None,
) -> go.Figure:
    """Plot cost and solver time against swarm size.

    Args:
        rows: Benchmark records with at least ``method``, ``n``, ``status``,
            ``assignment_cost`` and ``solve_time_ms``. String values (as read
            back from a CSV) are accepted.
        title: Optional figure title.

    Returns:
        A two-row figure: assignment cost on top, solve time (log scale) below.

    Raises:
        ValueError: If no row has ``status == "ok"``.
    """
    grouped = _group_by_size_and_method(rows)
    if not grouped:
        raise ValueError("no successful benchmark rows to plot")

    figure = make_subplots(
        rows=2,
        cols=1,
        shared_xaxes=True,
        subplot_titles=("assignment cost vs N", "solve time vs N (log scale)"),
        vertical_spacing=0.12,
    )

    for index, (method, by_size) in enumerate(grouped.items()):
        color = _cycle(index)
        sizes = sorted(by_size)
        median_cost = [
            float(np.median([float(r["assignment_cost"]) for r in by_size[n]])) for n in sizes
        ]
        median_time = [
            float(np.median([float(r["solve_time_ms"]) for r in by_size[n]])) for n in sizes
        ]

        for n in sizes:
            figure.add_trace(
                go.Scatter(
                    x=[n] * len(by_size[n]),
                    y=[float(r["assignment_cost"]) for r in by_size[n]],
                    mode="markers",
                    marker={"size": 5, "color": color, "opacity": 0.25},
                    name=method,
                    legendgroup=method,
                    showlegend=False,
                    hoverinfo="skip",
                ),
                row=1,
                col=1,
            )
            figure.add_trace(
                go.Scatter(
                    x=[n] * len(by_size[n]),
                    y=[float(r["solve_time_ms"]) for r in by_size[n]],
                    mode="markers",
                    marker={"size": 5, "color": color, "opacity": 0.25},
                    name=method,
                    legendgroup=method,
                    showlegend=False,
                    hoverinfo="skip",
                ),
                row=2,
                col=1,
            )

        figure.add_trace(
            go.Scatter(
                x=sizes,
                y=median_cost,
                mode="lines+markers",
                name=method,
                legendgroup=method,
                line={"color": color},
                marker={"size": 7, "color": color},
            ),
            row=1,
            col=1,
        )
        figure.add_trace(
            go.Scatter(
                x=sizes,
                y=median_time,
                mode="lines+markers",
                name=method,
                legendgroup=method,
                showlegend=False,
                line={"color": color},
                marker={"size": 7, "color": color},
            ),
            row=2,
            col=1,
        )

    figure.update_yaxes(type="log", row=2, col=1)
    figure.update_xaxes(title_text="agents N", row=2, col=1)
    figure.update_yaxes(title_text="sum of pair costs", row=1, col=1)
    figure.update_yaxes(title_text="milliseconds per solve", row=2, col=1)
    figure.update_layout(
        title=title or "Phase 2 assignment benchmark",
        margin={"l": 60, "r": 20, "b": 50, "t": 70},
        legend={"x": 1.01, "y": 1.0},
    )
    return figure


def save_figure(figure: go.Figure, path: str | Path) -> Path:
    """Write ``figure`` to a self-contained HTML file and return its path."""
    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    figure.write_html(destination, include_plotlyjs="cdn", full_html=True)
    return destination
