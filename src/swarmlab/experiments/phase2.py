"""Phase 2 experiment: assignment solvers measured on one shared problem.

Every method is applied to the same scenario and the same cost matrix, so the
cost columns are directly comparable:

* ``random`` - seeded permutation, the Phase 1 baseline;
* ``greedy`` - agents in index order, each takes the nearest free target;
* ``greedy_pair`` - cheapest free pair first;
* ``hungarian`` - educational ``O(N**3)`` exact solver;
* ``brute_force`` - oracle for ``N <= 8`` only;
* ``scipy`` - reference optimum.

The runner reports three things that are easy to conflate:

``assignment_cost``
    The objective value of the chosen bijection under the declared cost.
``travel_length``
    The measured length of the linear paths. Equal to ``assignment_cost`` for
    the Euclidean objective, and different for the squared objective.
``solve_time``
    Wall-clock time of the solver call, excluding cost-matrix construction and
    visualization. Reported as a median over repeated runs, with the observed
    minimum and maximum, as required by ``docs/EXPERIMENTS.md``.
"""

from __future__ import annotations

import argparse
import csv
import platform
import subprocess
import time
from collections.abc import Callable, Iterable, Sequence
from dataclasses import dataclass
from functools import partial
from pathlib import Path
from typing import Any

import numpy as np
import scipy

from swarmlab.assignment import (
    COST_FUNCTIONS,
    MATRIX_SOLVERS,
    random_assignment,
    total_cost,
)
from swarmlab.evaluation.metrics import evaluate_trajectory
from swarmlab.experiments.phase1 import build_scenario
from swarmlab.models import Assignment, Evaluation, FloatArray, Scenario
from swarmlab.trajectories.linear import linear_trajectory

__all__ = [
    "CSV_FIELDS",
    "MethodResult",
    "Phase2Result",
    "environment",
    "format_report",
    "format_sweep_report",
    "main",
    "run_phase2",
    "run_sweep",
    "sweep_rows",
    "write_rows_csv",
]

_DEFAULT_METHODS = ("random", "greedy", "greedy_pair", "hungarian", "scipy")
_EXACT_METHODS = frozenset({"brute_force", "hungarian", "scipy"})
_ALL_METHODS = _DEFAULT_METHODS + ("brute_force",)
_METHOD_ORDER = {name: index for index, name in enumerate(_ALL_METHODS)}

CSV_FIELDS = (
    "n",
    "seed",
    "source",
    "target",
    "objective",
    "method",
    "assignment_cost",
    "travel_length",
    "gap_vs_reference",
    "solve_time_ms",
    "solve_time_min_ms",
    "solve_time_max_ms",
    "repeats",
    "reference_method",
    "status",
    "note",
)


@dataclass(frozen=True)
class MethodResult:
    """One solver applied to the scenario's shared cost matrix."""

    method: str
    """Name of the solver."""

    assignment: Assignment
    """The bijection it returned."""

    evaluation: Evaluation
    """Metrics of the linear trajectory built from that bijection."""

    assignment_cost: float
    """Objective value ``sum_i costs[i, assignment[i]]``."""

    solve_time_s: float
    """Median wall-clock time of one solver call, in seconds."""

    solve_time_min_s: float
    """Fastest timed solver call, in seconds."""

    solve_time_max_s: float
    """Slowest timed solver call, in seconds."""

    repeats: int
    """Number of timed calls the median is taken over."""


@dataclass(frozen=True)
class Phase2Result:
    """Everything produced by one Phase 2 run."""

    scenario: Scenario
    """The transition problem every method solved."""

    source_kind: str
    """Name of the source formation in the registry."""

    target_kind: str
    """Name of the target formation in the registry."""

    objective: str
    """Key of the cost function in ``COST_FUNCTIONS``."""

    costs: FloatArray
    """The shared ``(N, N)`` cost matrix."""

    cost_matrix_time_s: float
    """Time spent building the shared matrix, in seconds."""

    methods: tuple[MethodResult, ...]
    """One entry per solver, in the requested order."""

    reference_method: str | None
    """Exact method whose cost defines the optimum, or ``None``."""

    optimum_cost: float | None
    """Lowest cost reported by an exact method, or ``None``."""


def _relative_gap(cost: float, optimum: float) -> float:
    """Return ``(cost - optimum) / |optimum|``, safe when the optimum is zero."""
    scale = abs(optimum)
    if scale == 0.0:
        return 0.0 if cost == 0.0 else float("inf")
    return (cost - optimum) / scale


def _time_solver(
    solve: Callable[[], Assignment],
    *,
    repeats: int,
) -> tuple[Assignment, float, float, float]:
    """Run ``solve`` once as a warm-up, then ``repeats`` timed times.

    Returns:
        The last assignment, the median, the minimum and the maximum duration
        in seconds.
    """
    assignment = solve()  # Warm-up: excluded from the measurement.
    samples: list[float] = []
    for _ in range(repeats):
        start = time.perf_counter()
        assignment = solve()
        samples.append(time.perf_counter() - start)
    return assignment, float(np.median(samples)), min(samples), max(samples)


def _check_exact_agreement(results: Sequence[MethodResult]) -> None:
    """Raise if two exact methods disagree on the optimal objective value.

    They may return different permutations when the optimum is tied; they may
    not return different costs.
    """
    costs = {result.method: result.assignment_cost for result in results}
    exact = [costs[name] for name in _EXACT_METHODS if name in costs]
    if len(exact) < 2:
        return
    tolerance = 1e-9 * max(1.0, max(abs(value) for value in exact))
    if max(exact) - min(exact) > tolerance:
        raise ValueError(
            f"exact solvers disagree on the optimum: {exact}; "
            f"one of them is wrong and the record is invalid"
        )


def _validate(result: Phase2Result) -> None:
    """Check the invariants that make a benchmark record trustworthy.

    Raises:
        ValueError: If a heuristic reports a cost below the exact optimum, or if
            the measured path length contradicts the assignment cost under the
            Euclidean objective.
    """
    if result.optimum_cost is not None:
        tolerance = 1e-9 * max(1.0, abs(result.optimum_cost))
        for method in result.methods:
            if method.assignment_cost < result.optimum_cost - tolerance:
                raise ValueError(
                    f"{method.method} reported cost {method.assignment_cost} below the "
                    f"exact optimum {result.optimum_cost}; the record is invalid"
                )

    if result.objective != "euclidean_distance":
        return
    for method in result.methods:
        cost = method.assignment_cost
        travel = method.evaluation.total_travel_length
        if abs(travel - cost) > 1e-9 * max(1.0, abs(cost)):
            raise ValueError(
                f"{method.method}: travel length {travel} does not match the assignment "
                f"cost {cost} for the Euclidean objective"
            )


def _solver_for(name: str, costs: FloatArray, n_agents: int, seed: int) -> Callable[[], Assignment]:
    """Return a zero-argument callable that solves the problem with ``name``."""
    if name == "random":
        # Random ignores the cost matrix entirely; it is a baseline, not a solver.
        return partial(random_assignment, n_agents, seed)
    if name not in MATRIX_SOLVERS:
        raise ValueError(f"unknown method {name!r}; choose from {sorted(_ALL_METHODS)}")
    return partial(MATRIX_SOLVERS[name], costs)


def run_phase2(
    n: int = 250,
    seed: int = 0,
    source_kind: str = "grid",
    target_kind: str = "sphere",
    *,
    duration_s: float = 10.0,
    objective: str = "euclidean_distance",
    methods: Sequence[str] = _DEFAULT_METHODS,
    repeats: int = 5,
) -> Phase2Result:
    """Solve one scenario with every requested method.

    Args:
        n: Number of agents.
        seed: Scenario seed. It also seeds the random baseline.
        source_kind: Key of the source formation.
        target_kind: Key of the target formation.
        duration_s: Duration of the transition, in seconds.
        objective: Key of the cost function, ``"euclidean_distance"`` or
            ``"squared_distance"``.
        methods: Solver names. ``"random"`` is the only one that is not a
            matrix solver.
        repeats: Number of timed solver calls per method.

    Returns:
        A :class:`Phase2Result` holding the shared matrix and one
        :class:`MethodResult` per method.

    Raises:
        ValueError: If the objective or a method is unknown, if ``repeats`` is
            not positive, or if the results violate a benchmark invariant.
    """
    if objective not in COST_FUNCTIONS:
        raise ValueError(f"unknown objective {objective!r}; choose from {sorted(COST_FUNCTIONS)}")
    if repeats < 1:
        raise ValueError(f"repeats must be positive, got {repeats}")

    scenario = build_scenario(n, seed, source_kind, target_kind, duration_s=duration_s)
    builder = COST_FUNCTIONS[objective]

    start = time.perf_counter()
    costs = builder(scenario.source_positions, scenario.target_positions)
    cost_matrix_time_s = time.perf_counter() - start

    results: list[MethodResult] = []
    for name in methods:
        solve = _solver_for(name, costs, scenario.n_agents, seed)
        assignment, median_s, min_s, max_s = _time_solver(solve, repeats=repeats)
        trajectory = linear_trajectory(scenario, assignment)
        evaluation = evaluate_trajectory(
            scenario,
            assignment,
            trajectory,
            assignment_method=name,
        )
        results.append(
            MethodResult(
                method=name,
                assignment=assignment,
                evaluation=evaluation,
                assignment_cost=total_cost(costs, assignment),
                solve_time_s=median_s,
                solve_time_min_s=min_s,
                solve_time_max_s=max_s,
                repeats=repeats,
            )
        )

    _check_exact_agreement(results)

    exact = [result for result in results if result.method in _EXACT_METHODS]
    if not exact:
        reference_method = None
        optimum_cost = None
    else:
        reference_method = next(
            (result.method for result in exact if result.method == "scipy"),
            exact[0].method,
        )
        optimum_cost = min(result.assignment_cost for result in exact)

    result = Phase2Result(
        scenario=scenario,
        source_kind=source_kind,
        target_kind=target_kind,
        objective=objective,
        costs=costs,
        cost_matrix_time_s=cost_matrix_time_s,
        methods=tuple(results),
        reference_method=reference_method,
        optimum_cost=optimum_cost,
    )
    _validate(result)
    return result


def format_report(result: Phase2Result) -> str:
    """Return the human-readable report of a single Phase 2 run."""
    scenario = result.scenario
    lines = [
        "SwarmLab - Phase 2: Assignment Solvers",
        "-" * 74,
        f"scenario      : N={scenario.n_agents} source={result.source_kind} "
        f"target={result.target_kind} seed={scenario.seed}",
        f"objective     : {result.objective} (sum of pairwise costs)",
        f"cost matrix   : {result.cost_matrix_time_s * 1e3:.2f} ms for "
        f"{scenario.n_agents} x {scenario.n_agents} pairs",
        "",
        f"{'method':<12}{'cost':>12}{'gap':>9}{'travel':>13}{'solve(med)':>13}{'range':>17}",
    ]

    for method in result.methods:
        if result.optimum_cost is None:
            gap = "n/a"
        else:
            gap = f"{_relative_gap(method.assignment_cost, result.optimum_cost):+.2%}"
        lines.append(
            f"{method.method:<12}"
            f"{method.assignment_cost:>12.4f}"
            f"{gap:>9}"
            f"{method.evaluation.total_travel_length:>13.4f}"
            f"{method.solve_time_s * 1e3:>11.3f} ms"
            f"{method.solve_time_min_s * 1e3:>8.3f}-{method.solve_time_max_s * 1e3:.3f} ms"
        )

    if result.optimum_cost is None:
        lines.append("")
        lines.append("reference     : none requested; gaps are not available")
    else:
        lines.append("")
        lines.append(
            f"reference     : {result.reference_method} optimum = {result.optimum_cost:.4f}"
        )
    lines.extend(
        [
            "",
            "Equal cost does not imply the same permutation: tied optima are broken",
            "differently by different solvers, and that is not an error.",
            "",
            "WARNING: a cost-optimal assignment is not collision-safe. Nothing here",
            "checks separation between agents; that is Phase 3.",
        ]
    )
    return "\n".join(lines)


def result_rows(result: Phase2Result) -> list[dict[str, Any]]:
    """Return one flat CSV-ready row per method of ``result``."""
    rows: list[dict[str, Any]] = []
    for method in result.methods:
        gap = (
            ""
            if result.optimum_cost is None
            else _relative_gap(method.assignment_cost, result.optimum_cost)
        )
        rows.append(
            {
                "n": result.scenario.n_agents,
                "seed": result.scenario.seed,
                "source": result.source_kind,
                "target": result.target_kind,
                "objective": result.objective,
                "method": method.method,
                "assignment_cost": method.assignment_cost,
                "travel_length": method.evaluation.total_travel_length,
                "gap_vs_reference": gap,
                "solve_time_ms": method.solve_time_s * 1e3,
                "solve_time_min_ms": method.solve_time_min_s * 1e3,
                "solve_time_max_ms": method.solve_time_max_s * 1e3,
                "repeats": method.repeats,
                "reference_method": result.reference_method or "",
                "status": "ok",
                "note": "",
            }
        )
    return rows


def run_sweep(
    sizes: Iterable[int],
    seeds: Iterable[int],
    source_kind: str = "grid",
    target_kind: str = "sphere",
    *,
    duration_s: float = 10.0,
    objective: str = "euclidean_distance",
    methods: Sequence[str] = _DEFAULT_METHODS,
    repeats: int = 5,
    max_hungarian_n: int = 1000,
) -> list[Phase2Result]:
    """Run every ``(size, seed)`` pair, dropping the educational solver when slow.

    Args:
        sizes: Swarm sizes to run.
        seeds: Seeds to run for every size.
        source_kind: Key of the source formation.
        target_kind: Key of the target formation.
        duration_s: Duration of the transition, in seconds.
        objective: Key of the cost function.
        methods: Solver names to run.
        repeats: Number of timed solver calls per method.
        max_hungarian_n: Largest size at which ``hungarian`` is attempted. The
            educational implementation is cubic with a large constant, so above
            this size only the reference solver is used. The measured constant
            is recorded in ``docs/STATUS.md``.

    Returns:
        One :class:`Phase2Result` per ``(size, seed)`` pair, in order.
    """
    results: list[Phase2Result] = []
    for n in sizes:
        active = tuple(
            name for name in methods if not (name == "hungarian" and n > max_hungarian_n)
        )
        for seed in seeds:
            results.append(
                run_phase2(
                    n,
                    seed,
                    source_kind,
                    target_kind,
                    duration_s=duration_s,
                    objective=objective,
                    methods=active,
                    repeats=repeats,
                )
            )
    return results


def sweep_rows(
    results: Sequence[Phase2Result],
    *,
    sizes: Sequence[int],
    seeds: Sequence[int],
    methods: Sequence[str],
    max_hungarian_n: int,
) -> list[dict[str, Any]]:
    """Flatten a sweep into rows, including explicit rows for skipped methods.

    A method that was not run gets ``status = "skipped_for_size"`` rather than
    a missing row, so a reader can tell "not measured" from "lost".
    """
    rows = [row for result in results for row in result_rows(result)]
    measured = {
        (result.scenario.n_agents, result.scenario.seed, method.method)
        for result in results
        for method in result.methods
    }
    for n in sizes:
        for seed in seeds:
            for name in methods:
                if (n, seed, name) in measured:
                    continue
                note = (
                    f"educational Hungarian solver not run above N={max_hungarian_n}"
                    if name == "hungarian"
                    else "not measured"
                )
                rows.append(
                    {
                        "n": n,
                        "seed": seed,
                        "source": results[0].source_kind if results else "",
                        "target": results[0].target_kind if results else "",
                        "objective": results[0].objective if results else "",
                        "method": name,
                        "assignment_cost": "",
                        "travel_length": "",
                        "gap_vs_reference": "",
                        "solve_time_ms": "",
                        "solve_time_min_ms": "",
                        "solve_time_max_ms": "",
                        "repeats": "",
                        "reference_method": "",
                        "status": "skipped_for_size",
                        "note": note,
                    }
                )
    return rows


def format_sweep_report(rows: Sequence[dict[str, Any]]) -> str:
    """Return a compact table of medians over seeds, one block per size."""
    grouped: dict[tuple[int, str], list[dict[str, Any]]] = {}
    for row in rows:
        if row["status"] != "ok":
            continue
        grouped.setdefault((int(row["n"]), str(row["method"])), []).append(dict(row))

    lines = [f"{'n':>6}  {'method':<12}{'median cost':>14}{'vs ref':>10}{'median solve':>15}"]
    ordered = sorted(
        grouped.items(),
        key=lambda item: (item[0][0], _METHOD_ORDER.get(item[0][1], len(_ALL_METHODS))),
    )
    for (n, method), group in ordered:
        costs = [float(row["assignment_cost"]) for row in group]
        times = [float(row["solve_time_ms"]) for row in group]
        gaps = [float(row["gap_vs_reference"]) for row in group if row["gap_vs_reference"] != ""]
        gap_text = f"{np.median(gaps):+.2%}" if gaps else "n/a"
        lines.append(
            f"{n:>6}  {method:<12}{np.median(costs):>14.4f}{gap_text:>10}"
            f"{np.median(times):>11.3f} ms"
        )
    return "\n".join(lines)


def write_rows_csv(rows: Sequence[dict[str, Any]], path: str | Path) -> Path:
    """Write benchmark rows to ``path`` with a stable column order."""
    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    with destination.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=CSV_FIELDS)
        writer.writeheader()
        writer.writerows(rows)
    return destination


def _git_commit() -> str:
    """Return the short commit hash, or ``"unknown"`` outside a repository."""
    try:
        completed = subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"],
            capture_output=True,
            check=True,
            text=True,
        )
    except (OSError, subprocess.CalledProcessError):
        return "unknown"
    return completed.stdout.strip() or "unknown"


def environment() -> dict[str, str]:
    """Return the environment fields that ``docs/EXPERIMENTS.md`` requires."""
    return {
        "commit": _git_commit(),
        "python": platform.python_version(),
        "numpy": np.__version__,
        "scipy": scipy.__version__,
        "platform": platform.platform(),
        "machine": platform.machine(),
        "processor": platform.processor() or "unknown",
    }


def format_environment(info: dict[str, str]) -> str:
    """Return the environment block printed above every report."""
    return "  ".join(f"{key}={value}" for key, value in info.items())


def _parse_int_list(text: str) -> list[int]:
    """Parse a comma-separated list of integers."""
    return [int(part) for part in text.split(",") if part.strip()]


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="swarmlab-assign",
        description="Compare Phase 2 assignment solvers on one shared cost matrix.",
    )
    parser.add_argument("--n", type=int, default=250, help="number of agents (default: 250)")
    parser.add_argument("--seed", type=int, default=0, help="scenario seed (default: 0)")
    parser.add_argument(
        "--source",
        choices=("grid", "sphere", "cube"),
        default="grid",
        help="source formation (default: grid)",
    )
    parser.add_argument(
        "--target",
        choices=("grid", "sphere", "cube"),
        default="sphere",
        help="target formation (default: sphere)",
    )
    parser.add_argument("--duration", type=float, default=10.0, help="transition duration (s)")
    parser.add_argument(
        "--objective",
        choices=sorted(COST_FUNCTIONS),
        default="euclidean_distance",
        help="cost objective (default: euclidean_distance)",
    )
    parser.add_argument(
        "--methods",
        default=",".join(_DEFAULT_METHODS),
        help="comma-separated solver names (default: all five)",
    )
    parser.add_argument(
        "--repeats",
        type=int,
        default=5,
        help="timed solver calls per method; the median is reported (default: 5)",
    )
    parser.add_argument(
        "--sweep",
        default=None,
        help="comma-separated sizes for a benchmark sweep, for example 50,100,250",
    )
    parser.add_argument(
        "--seeds",
        default="0",
        help="comma-separated seeds used by --sweep (default: 0)",
    )
    parser.add_argument(
        "--max-hungarian-n",
        type=int,
        default=1000,
        help="skip the educational Hungarian solver above this size (default: 1000)",
    )
    parser.add_argument("--csv", type=Path, default=None, help="write benchmark rows to CSV")
    parser.add_argument("--html", type=Path, default=None, help="write a comparison figure")
    parser.add_argument(
        "--paths",
        type=int,
        default=25,
        help="paths drawn per method in the single-run figure (default: 25)",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    """Command line entry point of the Phase 2 experiment.

    Args:
        argv: Argument list. Defaults to ``sys.argv[1:]``.

    Returns:
        The process exit code, ``0`` on success.
    """
    args = _build_parser().parse_args(argv)
    methods = tuple(part.strip() for part in args.methods.split(",") if part.strip())
    unknown = sorted(set(methods) - set(_ALL_METHODS))
    if unknown:
        raise SystemExit(f"unknown methods: {unknown}; choose from {list(_ALL_METHODS)}")

    info = environment()
    print(format_environment(info))
    print()

    if args.sweep is not None:
        sizes = _parse_int_list(args.sweep)
        seeds = _parse_int_list(args.seeds)
        results = run_sweep(
            sizes,
            seeds,
            args.source,
            args.target,
            duration_s=args.duration,
            objective=args.objective,
            methods=methods,
            repeats=args.repeats,
            max_hungarian_n=args.max_hungarian_n,
        )
        rows = sweep_rows(
            results,
            sizes=sizes,
            seeds=seeds,
            methods=methods,
            max_hungarian_n=args.max_hungarian_n,
        )
        print(f"SwarmLab - Phase 2 sweep: sizes={sizes} seeds={seeds} objective={args.objective}")
        print("-" * 74)
        print(format_sweep_report(rows))
        skipped = sorted({row["method"] for row in rows if row["status"] != "ok"})
        if skipped:
            print(f"\nnot run at the largest sizes: {', '.join(skipped)}")
    else:
        result = run_phase2(
            args.n,
            args.seed,
            args.source,
            args.target,
            duration_s=args.duration,
            objective=args.objective,
            methods=methods,
            repeats=args.repeats,
        )
        print(format_report(result))
        rows = result_rows(result)

    if args.csv is not None:
        print(f"\ncsv           : {write_rows_csv(rows, args.csv)}")

    if args.html is not None:
        if args.sweep is not None:
            from swarmlab.visualization.comparison import render_benchmark_curves, save_figure

            figure = render_benchmark_curves(rows)
        else:
            from swarmlab.visualization.comparison import (
                render_assignment_comparison,
                save_figure,
            )

            figure = render_assignment_comparison(
                result.scenario,
                {method.method: method.assignment for method in result.methods},
                max_paths=args.paths,
            )
        print(f"html          : {save_figure(figure, args.html)}")

    return 0


if __name__ == "__main__":  # pragma: no cover - module entry point
    raise SystemExit(main())
