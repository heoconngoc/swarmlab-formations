"""Phase 1 experiment: the formation playground.

The experiment wires the four layers together:

1. build a source formation and a target formation;
2. assign agents to targets with a seeded random permutation;
3. move every agent along the straight line to its goal;
4. measure the travel lengths and the makespan.

The result is a *geometric* reference, not a plan. The random assignment is
not optimized and no separation constraint is checked, so the paths routinely
cross. Both facts are printed with the result and stamped onto the figure.
"""

from __future__ import annotations

import argparse
from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path

from swarmlab.assignment.random import random_assignment
from swarmlab.evaluation.metrics import evaluate_trajectory
from swarmlab.formations import FORMATIONS
from swarmlab.models import Assignment, Constraints, Evaluation, Scenario, Trajectory
from swarmlab.trajectories.linear import linear_trajectory

__all__ = ["Phase1Result", "build_scenario", "main", "run_phase1"]

_DEFAULT_OUTPUT = "swarmlab_phase1.html"


@dataclass(frozen=True)
class Phase1Result:
    """Everything produced by a single Phase 1 run."""

    scenario: Scenario
    """The transition problem that was solved."""

    assignment: Assignment
    """The random bijection that was used."""

    trajectory: Trajectory
    """The linear trajectory that was evaluated."""

    evaluation: Evaluation
    """The Phase 1 metrics of that trajectory."""

    source_kind: str
    """Name of the source formation in the formation registry."""

    target_kind: str
    """Name of the target formation in the formation registry."""


def build_scenario(
    n: int,
    seed: int,
    source_kind: str = "grid",
    target_kind: str = "sphere",
    *,
    duration_s: float = 10.0,
) -> Scenario:
    """Build a scenario from two formation kinds.

    Args:
        n: Number of agents.
        seed: Seed recorded on the scenario.
        source_kind: Key of the source formation, for example ``"grid"``.
        target_kind: Key of the target formation, for example ``"sphere"``.
        duration_s: Duration of the transition, in seconds.

    Returns:
        The assembled :class:`~swarmlab.models.Scenario`.

    Raises:
        KeyError: If a formation kind is unknown.
    """
    source = FORMATIONS[source_kind](n)
    target = FORMATIONS[target_kind](n)
    return Scenario(
        source_positions=source,
        target_positions=target,
        seed=seed,
        constraints=Constraints(duration_s=duration_s),
    )


def run_phase1(
    n: int = 100,
    seed: int = 42,
    source_kind: str = "grid",
    target_kind: str = "sphere",
    *,
    duration_s: float = 10.0,
) -> Phase1Result:
    """Run the whole Phase 1 pipeline.

    Args:
        n: Number of agents.
        seed: Seed used for the scenario and for the random assignment.
        source_kind: Key of the source formation.
        target_kind: Key of the target formation.
        duration_s: Duration of the transition, in seconds.

    Returns:
        A :class:`Phase1Result` holding the scenario, the assignment, the
        trajectory and the metrics.
    """
    scenario = build_scenario(
        n,
        seed,
        source_kind,
        target_kind,
        duration_s=duration_s,
    )
    assignment = random_assignment(scenario.n_agents, seed)
    trajectory = linear_trajectory(scenario, assignment)
    evaluation = evaluate_trajectory(scenario, assignment, trajectory)
    return Phase1Result(
        scenario=scenario,
        assignment=assignment,
        trajectory=trajectory,
        evaluation=evaluation,
        source_kind=source_kind,
        target_kind=target_kind,
    )


def format_report(result: Phase1Result) -> str:
    """Return the human-readable report of a Phase 1 run."""
    evaluation = result.evaluation
    mean_travel = float(evaluation.per_agent_travel_length.mean())
    return "\n".join(
        [
            "SwarmLab - Phase 1: Formation Playground",
            "-" * 44,
            f"scenario      : N={result.scenario.n_agents} "
            f"source={result.source_kind} target={result.target_kind} "
            f"seed={result.scenario.seed}",
            "assignment    : random permutation (baseline, not an optimizer)",
            f"trajectory    : linear interpolation, "
            f"{result.trajectory.n_waypoints} waypoints per agent, "
            f"T={result.scenario.constraints.duration_s:g}s",
            f"total travel  : {evaluation.total_travel_length:.4f}",
            f"mean travel   : {mean_travel:.4f}",
            f"makespan      : {evaluation.makespan_s:.2f}s",
            "",
            "WARNING: this baseline is NOT collision-safe. The assignment is",
            "random and no separation constraint is checked anywhere in Phase 1.",
        ]
    )


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="swarmlab-demo",
        description="Run the SwarmLab Phase 1 formation playground.",
    )
    parser.add_argument("--n", type=int, default=100, help="number of agents (default: 100)")
    parser.add_argument("--seed", type=int, default=42, help="random seed (default: 42)")
    parser.add_argument(
        "--source",
        choices=sorted(FORMATIONS),
        default="grid",
        help="source formation (default: grid)",
    )
    parser.add_argument(
        "--target",
        choices=sorted(FORMATIONS),
        default="sphere",
        help="target formation (default: sphere)",
    )
    parser.add_argument(
        "--duration",
        type=float,
        default=10.0,
        help="duration of the transition in seconds (default: 10)",
    )
    parser.add_argument(
        "--agent",
        type=int,
        default=0,
        help="index of the agent whose path is highlighted (default: 0)",
    )
    parser.add_argument(
        "--frames",
        type=int,
        default=60,
        help="number of animation frames (default: 60)",
    )
    parser.add_argument(
        "--out",
        type=Path,
        default=None,
        help=f"path of the HTML output (default: ./{_DEFAULT_OUTPUT})",
    )
    parser.add_argument(
        "--no-html",
        action="store_true",
        help="skip the HTML output and only print the report",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    """Command line entry point of the Phase 1 demo.

    Args:
        argv: Argument list. Defaults to ``sys.argv[1:]``.

    Returns:
        The process exit code, ``0`` on success.
    """
    args = _build_parser().parse_args(argv)
    result = run_phase1(
        n=args.n,
        seed=args.seed,
        source_kind=args.source,
        target_kind=args.target,
        duration_s=args.duration,
    )
    print(format_report(result))

    if not args.no_html:
        from swarmlab.visualization.viewer import save_transition

        destination = args.out if args.out is not None else Path.cwd() / _DEFAULT_OUTPUT
        written = save_transition(
            result.scenario,
            result.trajectory,
            destination,
            selected_agent=args.agent,
            n_frames=args.frames,
        )
        print(f"\nhtml          : {written}")

    return 0


if __name__ == "__main__":  # pragma: no cover - module entry point
    raise SystemExit(main())
