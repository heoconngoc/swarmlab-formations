"""Tests for the Phase 2 comparison figures."""

from __future__ import annotations

import numpy as np
import pytest

from swarmlab.assignment import greedy_assignment, random_assignment, scipy_assignment
from swarmlab.assignment.costs import euclidean_distance_costs
from swarmlab.models import Scenario
from swarmlab.visualization.comparison import (
    render_assignment_comparison,
    render_benchmark_curves,
    save_figure,
)


def _scenario(n: int = 12) -> Scenario:
    source = np.linspace(-1.0, 1.0, n * 3).reshape(n, 3)
    target = -source
    return Scenario(source_positions=source, target_positions=target, seed=0)


def test_comparison_draws_one_scene_per_method() -> None:
    scenario = _scenario()
    costs = euclidean_distance_costs(scenario.source_positions, scenario.target_positions)
    assignments = {
        "random": random_assignment(scenario.n_agents, seed=0),
        "greedy": greedy_assignment(costs),
        "scipy": scipy_assignment(costs),
    }

    figure = render_assignment_comparison(scenario, assignments)

    # Two traces per method: one source marker layer plus one path polyline.
    assert len(figure.data) == 2 * len(assignments)
    # Each 3D scene is titled with the name of the method it draws.
    assert {annotation.text for annotation in figure.layout.annotations} == set(assignments)


def test_comparison_limits_the_number_of_paths() -> None:
    scenario = _scenario()
    assignment = random_assignment(scenario.n_agents, seed=0)
    figure = render_assignment_comparison(scenario, {"random": assignment}, max_paths=3)

    path_trace = figure.data[-1]
    # Three agents, two points each, one NaN separator per agent.
    assert len(path_trace.x) == 3 * 3
    assert sum(np.isnan(path_trace.x)) == 3


def test_comparison_rejects_empty_input() -> None:
    with pytest.raises(ValueError, match="at least one method"):
        render_assignment_comparison(_scenario(), {})


def _rows() -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for n in (10, 20):
        for seed in (0, 1):
            for method, factor in (("random", 2.0), ("scipy", 1.0)):
                rows.append(
                    {
                        "n": n,
                        "seed": seed,
                        "method": method,
                        "status": "ok",
                        "assignment_cost": factor * n * (1 + 0.1 * seed),
                        "solve_time_ms": 0.01 * factor * n,
                    }
                )
    rows.append({"n": 30, "seed": 0, "method": "hungarian", "status": "skipped_for_size"})
    return rows


def test_benchmark_curves_plot_successful_rows_only() -> None:
    figure = render_benchmark_curves(_rows())

    names = {trace.name for trace in figure.data}
    assert names == {"random", "scipy"}
    # Two subplots: cost (linear) and time (log).
    assert figure.layout.yaxis2.type == "log"


def test_benchmark_curves_require_data() -> None:
    with pytest.raises(ValueError, match="no successful benchmark rows"):
        render_benchmark_curves([{"n": 1, "method": "scipy", "status": "skipped_for_size"}])


def test_save_figure_writes_html(tmp_path) -> None:
    figure = render_benchmark_curves(_rows())

    written = save_figure(figure, tmp_path / "nested" / "curves.html")

    assert written.exists()
    assert "assignment cost vs N" in written.read_text()
