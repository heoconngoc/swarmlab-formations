"""Tests for the Plotly viewer."""

from __future__ import annotations

import numpy as np
import pytest

from swarmlab.assignment.random import random_assignment
from swarmlab.models import Scenario
from swarmlab.trajectories.linear import linear_trajectory
from swarmlab.visualization.viewer import render_transition, save_transition


def _trajectory(n: int = 8):
    source = np.linspace(-1.0, 1.0, n * 3).reshape(n, 3)
    scenario = Scenario(
        source_positions=source,
        target_positions=-source,
        seed=0,
    )
    assignment = random_assignment(n, seed=1)
    return scenario, linear_trajectory(scenario, assignment)


def test_render_transition_builds_the_expected_frames() -> None:
    scenario, trajectory = _trajectory()
    figure = render_transition(scenario, trajectory, n_frames=12)

    assert len(figure.frames) == 12
    assert len(figure.data) == 2


def test_render_transition_rejects_an_invalid_agent() -> None:
    scenario, trajectory = _trajectory()
    with pytest.raises(ValueError, match="selected_agent"):
        render_transition(scenario, trajectory, selected_agent=99)


def test_render_transition_rejects_too_few_frames() -> None:
    scenario, trajectory = _trajectory()
    with pytest.raises(ValueError, match="n_frames"):
        render_transition(scenario, trajectory, n_frames=1)


def test_slider_steps_reference_existing_frames() -> None:
    """A slider step must name a frame; a float or an index does nothing."""
    scenario, trajectory = _trajectory()
    figure = render_transition(scenario, trajectory, n_frames=7)

    frame_names = {frame.name for frame in figure.frames}
    steps = figure.layout.sliders[0].steps

    assert len(steps) == 7
    for step in steps:
        assert step.args[0][0] in frame_names


def test_playback_buttons_exist() -> None:
    scenario, trajectory = _trajectory()
    figure = render_transition(scenario, trajectory, n_frames=5)

    buttons = figure.layout.updatemenus[0].buttons
    assert [button.label for button in buttons] == ["Play", "Pause"]


def test_frames_move_the_agents() -> None:
    """Consecutive frames must actually differ, otherwise the slider looks frozen."""
    scenario, trajectory = _trajectory()
    figure = render_transition(scenario, trajectory, n_frames=5)

    first = np.asarray(figure.frames[0].data[0].x)
    last = np.asarray(figure.frames[-1].data[0].x)
    assert not np.allclose(first, last)


def test_save_transition_writes_an_html_file(tmp_path) -> None:
    scenario, trajectory = _trajectory()
    destination = save_transition(scenario, trajectory, tmp_path / "out" / "demo.html", n_frames=5)

    assert destination.exists()
    content = destination.read_text(encoding="utf-8")
    assert "NOT collision-safe" in content
