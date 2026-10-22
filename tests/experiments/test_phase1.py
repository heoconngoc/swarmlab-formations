"""Tests for the Phase 1 experiment runner."""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

import numpy as np
import pytest

from swarmlab.experiments.phase1 import build_scenario, format_report, main, run_phase1

_SRC = Path(__file__).resolve().parents[2] / "src"


def test_build_scenario_uses_the_requested_formations() -> None:
    scenario = build_scenario(20, seed=3, source_kind="grid", target_kind="sphere")
    assert scenario.n_agents == 20
    assert scenario.seed == 3
    assert scenario.source_positions.shape == (20, 3)
    assert scenario.target_positions.shape == (20, 3)


def test_build_scenario_rejects_unknown_formations() -> None:
    with pytest.raises(KeyError):
        build_scenario(20, seed=3, source_kind="spiral")


def test_run_phase1_is_reproducible() -> None:
    first = run_phase1(n=25, seed=9)
    second = run_phase1(n=25, seed=9)
    np.testing.assert_array_equal(
        first.assignment.target_index,
        second.assignment.target_index,
    )
    assert first.evaluation.total_travel_length == pytest.approx(
        second.evaluation.total_travel_length
    )


def test_report_contains_the_safety_warning() -> None:
    report = format_report(run_phase1(n=10, seed=0))
    assert "NOT collision-safe" in report
    assert "random permutation" in report


def test_main_runs_without_writing_html(capsys: pytest.CaptureFixture[str]) -> None:
    exit_code = main(["--n", "8", "--seed", "1", "--no-html"])
    captured = capsys.readouterr()
    assert exit_code == 0
    assert "Phase 1" in captured.out
    assert "html" not in captured.out


def test_core_does_not_import_plotly() -> None:
    """The algorithm core must stay free of any presentation dependency."""
    env = {**os.environ, "PYTHONPATH": str(_SRC)}
    code = (
        "import swarmlab, swarmlab.experiments.phase1, sys; "
        "assert 'plotly' not in sys.modules, 'plotly leaked into the core'"
    )
    subprocess.run([sys.executable, "-c", code], env=env, check=True)
