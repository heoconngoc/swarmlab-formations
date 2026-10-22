"""Tests for the Phase 2 experiment runner."""

from __future__ import annotations

import csv
import os
import subprocess
import sys
from pathlib import Path

import numpy as np
import pytest

from swarmlab.assignment import total_cost
from swarmlab.evaluation.metrics import evaluate_trajectory
from swarmlab.experiments.phase2 import (
    CSV_FIELDS,
    MethodResult,
    Phase2Result,
    _check_exact_agreement,
    _validate,
    environment,
    format_report,
    main,
    result_rows,
    run_phase2,
    run_sweep,
    sweep_rows,
    write_rows_csv,
)
from swarmlab.models import Assignment, Evaluation, Scenario
from swarmlab.trajectories.linear import linear_trajectory

_SRC = Path(__file__).resolve().parents[2] / "src"


def _fake_method(name: str, cost: float, travel: float | None = None) -> MethodResult:
    """Build a MethodResult without running a solver, for invariant tests."""
    scenario = Scenario(
        source_positions=np.array([[0.0, 0.0, 0.0], [1.0, 0.0, 0.0]]),
        target_positions=np.array([[1.0, 0.0, 0.0], [0.0, 0.0, 0.0]]),
        seed=0,
    )
    assignment = Assignment(target_index=np.array([0, 1]))
    trajectory = linear_trajectory(scenario, assignment)
    evaluation = evaluate_trajectory(scenario, assignment, trajectory, assignment_method=name)
    if travel is not None:
        evaluation = Evaluation(
            total_travel_length=travel,
            per_agent_travel_length=evaluation.per_agent_travel_length,
            makespan_s=evaluation.makespan_s,
            n_agents=evaluation.n_agents,
            metadata=evaluation.metadata,
        )
    return MethodResult(
        method=name,
        assignment=assignment,
        evaluation=evaluation,
        assignment_cost=cost,
        solve_time_s=0.0,
        solve_time_min_s=0.0,
        solve_time_max_s=0.0,
        repeats=1,
    )


def _fake_result(methods: tuple[MethodResult, ...], optimum: float) -> Phase2Result:
    return Phase2Result(
        scenario=Scenario(
            source_positions=np.array([[0.0, 0.0, 0.0], [1.0, 0.0, 0.0]]),
            target_positions=np.array([[1.0, 0.0, 0.0], [0.0, 0.0, 0.0]]),
            seed=0,
        ),
        source_kind="grid",
        target_kind="grid",
        objective="euclidean_distance",
        costs=np.zeros((2, 2)),
        cost_matrix_time_s=0.0,
        methods=methods,
        reference_method="scipy",
        optimum_cost=optimum,
    )


_METHODS = ("random", "greedy", "greedy_pair", "hungarian", "scipy")


@pytest.fixture(scope="module")
def result() -> Phase2Result:
    return run_phase2(30, seed=4, methods=_METHODS, repeats=1)


def test_every_method_gets_a_valid_bijection(result: Phase2Result) -> None:
    for method in result.methods:
        assert np.array_equal(
            np.sort(method.assignment.target_index), np.arange(result.scenario.n_agents)
        )


def test_optimal_bound_holds(result: Phase2Result) -> None:
    """Every heuristic must be at least as expensive as the exact optimum."""
    assert result.optimum_cost is not None
    for method in result.methods:
        if method.method == "random":
            continue
        assert method.assignment_cost >= result.optimum_cost - 1e-9


def test_random_is_the_worst_method_on_this_instance(result: Phase2Result) -> None:
    by_name = {method.method: method.assignment_cost for method in result.methods}
    assert by_name["random"] > by_name["hungarian"]


def test_euclidean_cost_equals_the_measured_travel(result: Phase2Result) -> None:
    for method in result.methods:
        assert method.evaluation.total_travel_length == pytest.approx(
            method.assignment_cost, rel=1e-9
        )


def test_evaluation_records_the_solver_name(result: Phase2Result) -> None:
    for method in result.methods:
        assert method.evaluation.metadata["assignment_method"] == method.method


def test_run_phase2_is_reproducible() -> None:
    first = run_phase2(20, seed=7, methods=_METHODS, repeats=1)
    second = run_phase2(20, seed=7, methods=_METHODS, repeats=1)

    for left, right in zip(first.methods, second.methods, strict=True):
        np.testing.assert_array_equal(left.assignment.target_index, right.assignment.target_index)
        assert left.assignment_cost == right.assignment_cost


def test_squared_objective_is_a_different_quantity() -> None:
    result = run_phase2(20, seed=1, methods=("scipy",), objective="squared_distance", repeats=1)

    method = result.methods[0]
    scenario = result.scenario
    squared = np.sum(
        (scenario.source_positions[:, None, :] - scenario.target_positions[None, :, :]) ** 2,
        axis=2,
    )
    assert method.assignment_cost == pytest.approx(total_cost(squared, method.assignment))
    # Squared distances are not distances: the two numbers must not coincide.
    # Their order is not fixed either, since a pair distance may exceed one.
    assert method.evaluation.total_travel_length != pytest.approx(method.assignment_cost)


def test_report_names_the_methods_and_the_warning(result: Phase2Result) -> None:
    report = format_report(result)

    assert "Phase 2" in report
    for name in _METHODS:
        assert name in report
    assert "collision-safe" in report
    assert "optimum" in report


def test_report_without_an_exact_method_says_gaps_are_unavailable() -> None:
    result = run_phase2(10, seed=0, methods=("greedy",), repeats=1)

    assert result.optimum_cost is None
    assert "gaps are not available" in format_report(result)


def test_unknown_objective_and_method_are_rejected() -> None:
    with pytest.raises(ValueError, match="unknown objective"):
        run_phase2(5, seed=0, objective="manhattan")
    with pytest.raises(ValueError, match="unknown method"):
        run_phase2(5, seed=0, methods=("hungarian_lite",))
    with pytest.raises(ValueError, match="repeats"):
        run_phase2(5, seed=0, repeats=0)


def test_validate_rejects_a_cost_below_the_exact_optimum() -> None:
    """A heuristic that beats the exact solver means one of them is broken."""
    result = _fake_result((_fake_method("greedy", 0.5),), optimum=1.0)

    with pytest.raises(ValueError, match="below the exact optimum"):
        _validate(result)


def test_validate_rejects_travel_that_contradicts_the_cost() -> None:
    """Under the Euclidean objective these two numbers must agree."""
    result = _fake_result((_fake_method("greedy", 1.0, travel=99.0),), optimum=1.0)

    with pytest.raises(ValueError, match="does not match the assignment cost"):
        _validate(result)


def test_disagreeing_exact_solvers_invalidate_the_record() -> None:
    methods = (_fake_method("hungarian", 1.0), _fake_method("scipy", 2.0))

    with pytest.raises(ValueError, match="disagree on the optimum"):
        _check_exact_agreement(methods)


def test_zero_optimum_reports_a_zero_gap() -> None:
    """Identical formations make every cost zero; the gap must stay finite."""
    result = run_phase2(10, seed=0, source_kind="grid", target_kind="grid", repeats=1)

    assert result.optimum_cost == pytest.approx(0.0)
    report = format_report(result)
    assert "+0.00%" in report


def test_rows_have_a_fixed_schema(result: Phase2Result) -> None:
    rows = result_rows(result)

    assert len(rows) == len(result.methods)
    for row in rows:
        assert tuple(row) == CSV_FIELDS
        assert row["status"] == "ok"
        assert row["objective"] == "euclidean_distance"


def test_write_rows_csv_round_trips(tmp_path: Path, result: Phase2Result) -> None:
    destination = write_rows_csv(result_rows(result), tmp_path / "rows.csv")

    with destination.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))

    assert len(rows) == len(result.methods)
    assert rows[0]["method"] == "random"
    assert float(rows[0]["assignment_cost"]) == pytest.approx(result.methods[0].assignment_cost)


def test_sweep_marks_methods_it_skipped() -> None:
    sizes = [10, 60]
    seeds = [0]
    results = run_sweep(
        sizes,
        seeds,
        methods=_METHODS,
        repeats=1,
        max_hungarian_n=10,
    )
    rows = sweep_rows(
        results,
        sizes=sizes,
        seeds=seeds,
        methods=_METHODS,
        max_hungarian_n=10,
    )

    skipped = [row for row in rows if row["status"] != "ok"]
    assert [(row["n"], row["method"]) for row in skipped] == [(60, "hungarian")]
    assert "N=10" in skipped[0]["note"]
    # A skipped row must not be mistaken for a measurement of zero.
    assert skipped[0]["assignment_cost"] == ""


def test_environment_reports_the_required_fields() -> None:
    info = environment()

    assert set(info) == {
        "commit",
        "python",
        "numpy",
        "scipy",
        "platform",
        "machine",
        "processor",
    }
    assert all(value for value in info.values())


def test_main_sweep_writes_csv(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    destination = tmp_path / "sweep.csv"

    exit_code = main(
        [
            "--sweep",
            "8,12",
            "--seeds",
            "0",
            "--repeats",
            "1",
            "--max-hungarian-n",
            "8",
            "--csv",
            str(destination),
        ]
    )

    assert exit_code == 0
    output = capsys.readouterr().out
    assert "Phase 2 sweep" in output
    assert "not run at the largest sizes: hungarian" in output
    assert destination.exists()


def test_core_does_not_import_plotly() -> None:
    """The solver and experiment layers must stay free of Plotly."""
    env = {**os.environ, "PYTHONPATH": str(_SRC)}
    code = (
        "import swarmlab.experiments.phase2, sys; "
        "assert 'plotly' not in sys.modules, 'plotly leaked into the core'"
    )
    subprocess.run([sys.executable, "-c", code], env=env, check=True)


def test_main_rejects_unknown_methods() -> None:
    with pytest.raises(SystemExit, match="unknown methods"):
        main(["--n", "5", "--methods", "hungarian_lite"])


def test_main_writes_a_comparison_figure(tmp_path: Path) -> None:
    destination = tmp_path / "compare.html"

    exit_code = main(["--n", "8", "--seed", "0", "--repeats", "1", "--html", str(destination)])

    assert exit_code == 0
    assert "Assignment comparison" in destination.read_text()


def test_main_writes_benchmark_curves(tmp_path: Path) -> None:
    destination = tmp_path / "curves.html"

    exit_code = main(["--sweep", "8", "--seeds", "0", "--repeats", "1", "--html", str(destination)])

    assert exit_code == 0
    assert "assignment cost vs N" in destination.read_text()
