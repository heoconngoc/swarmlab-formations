"""Canonical data structures for SwarmLab.

This module owns the contracts described in ``docs/ARCHITECTURE.md``:

``Scenario``
    Source and target positions, the random seed, and the active constraints.
``Assignment``
    A bijection from agents to targets, stored as a permutation.
``Trajectory``
    Per-agent waypoints in space-time plus the interpolation semantics.
``Evaluation``
    Scalar metrics, per-agent measurements, and method metadata.

Design rules enforced here:

* Every dataclass is frozen, so attributes cannot be rebound.
* Every array is stored as an independent **read-only** copy, so callers cannot
  mutate a validated object in place. ``frozen=True`` alone does not prevent
  that, because a NumPy array stored in a frozen dataclass stays mutable.
* Shapes, finiteness, permutation validity, and time monotonicity are validated
  at construction time, so an invalid object cannot exist.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any

import numpy as np
from numpy.typing import NDArray

FloatArray = NDArray[np.float64]
IntArray = NDArray[np.int64]

__all__ = [
    "Assignment",
    "Constraints",
    "Evaluation",
    "FloatArray",
    "Interpolation",
    "IntArray",
    "Scenario",
    "Trajectory",
]


class Interpolation(StrEnum):
    """How positions are defined between consecutive waypoints.

    The semantics are carried explicitly on :class:`Trajectory` so that an
    evaluator never has to guess how to reconstruct a position from waypoints.
    """

    LINEAR = "linear"
    """Position moves along the straight segment between the two waypoints."""

    HOLD = "hold"
    """Position stays at the previous waypoint until the next one is reached."""


def _readonly_copy(array: NDArray[Any, Any]) -> NDArray[Any, Any]:
    """Return an independent, read-only copy of ``array``.

    The copy guarantees that the stored array is not aliased with anything the
    caller still holds, and ``write=False`` makes in-place mutation raise.
    """
    copy = np.array(array, copy=True)
    copy.setflags(write=False)
    return copy


def _as_float_array(array: NDArray[Any, Any], name: str) -> FloatArray:
    """Validate that ``array`` is a finite ``(N, 3)`` array and return it."""
    converted = np.asarray(array, dtype=np.float64)
    if converted.ndim != 2 or converted.shape[1] != 3:
        raise ValueError(f"{name} must have shape (N, 3), got {converted.shape}")
    if not np.isfinite(converted).all():
        raise ValueError(f"{name} contains non-finite values")
    return converted


@dataclass(frozen=True)
class Constraints:
    """Scenario-level constraints.

    Phase 1 works in dimensionless coordinates, so ``min_separation`` is not
    used by any Phase 1 metric and no physical safety claim is attached to it.
    """

    min_separation: float = 0.0
    """Minimum permitted pairwise separation ``d_min`` in the same units as the positions."""

    duration_s: float = 10.0
    """Duration ``T`` of the transition, in seconds."""

    def __post_init__(self) -> None:
        if not np.isfinite(self.min_separation) or self.min_separation < 0.0:
            raise ValueError(
                f"min_separation must be finite and non-negative, got {self.min_separation}"
            )
        if not np.isfinite(self.duration_s) or self.duration_s <= 0.0:
            raise ValueError(f"duration_s must be finite and positive, got {self.duration_s}")


@dataclass(frozen=True)
class Scenario:
    """A transition problem: where the agents start and where they must end.

    Positions are dimensionless coordinates in the cube ``[-1, 1]^3`` during
    the early phases. See ``docs/ARCHITECTURE.md`` on unit scaling.
    """

    source_positions: FloatArray
    """``(N, 3)`` start positions of the agents."""

    target_positions: FloatArray
    """``(N, 3)`` goal positions, one per agent, in the same order as the agents."""

    seed: int
    """Seed that produced this scenario, recorded for reproducibility."""

    constraints: Constraints = field(default_factory=Constraints)
    """Active constraints of the scenario."""

    def __post_init__(self) -> None:
        source = _as_float_array(self.source_positions, "source_positions")
        target = _as_float_array(self.target_positions, "target_positions")
        if source.shape != target.shape:
            raise ValueError(
                f"source_positions and target_positions must have the same shape, "
                f"got {source.shape} and {target.shape}"
            )
        object.__setattr__(self, "source_positions", _readonly_copy(source))
        object.__setattr__(self, "target_positions", _readonly_copy(target))

    @property
    def n_agents(self) -> int:
        """Number of agents ``N`` in the scenario."""
        return int(self.source_positions.shape[0])


@dataclass(frozen=True)
class Assignment:
    """A bijection from agents to targets.

    ``target_index[i]`` is the index of the target assigned to agent ``i``.
    The vector contains every integer in ``range(N)`` exactly once.
    """

    target_index: IntArray
    """``(N,)`` integer vector holding a permutation of ``range(N)``."""

    def __post_init__(self) -> None:
        raw = np.asarray(self.target_index)
        if raw.ndim != 1:
            raise ValueError(f"target_index must be one-dimensional, got shape {raw.shape}")
        if not np.issubdtype(raw.dtype, np.integer) and (
            not np.all(np.isfinite(raw)) or not np.all(raw == np.floor(raw))
        ):
            raise ValueError("target_index must contain integer values")
        index = raw.astype(np.int64)
        if index.size and not np.array_equal(np.sort(index), np.arange(index.size)):
            raise ValueError("target_index must be a permutation of range(N)")
        object.__setattr__(self, "target_index", _readonly_copy(index))

    @property
    def n_agents(self) -> int:
        """Number of agents ``N`` covered by the assignment."""
        return int(self.target_index.shape[0])


@dataclass(frozen=True)
class Trajectory:
    """Time-parameterized motion of every agent.

    ``times`` has shape ``(N, M)``: one row of waypoint times per agent. Phase 1
    uses a synchronized grid, so all rows are identical, but the layout already
    supports staggered departures, which Phase 4 needs.
    """

    times: FloatArray
    """``(N, M)`` waypoint times in seconds, strictly increasing along each row."""

    positions: FloatArray
    """``(N, M, 3)`` waypoint positions in the same units as the scenario positions."""

    interpolation: Interpolation = Interpolation.LINEAR
    """Semantics used to reconstruct a position between two waypoints."""

    def __post_init__(self) -> None:
        times = np.asarray(self.times, dtype=np.float64)
        positions = np.asarray(self.positions, dtype=np.float64)

        if times.ndim != 2:
            raise ValueError(f"times must have shape (N, M), got {times.shape}")
        if positions.ndim != 3 or positions.shape[2] != 3:
            raise ValueError(f"positions must have shape (N, M, 3), got {positions.shape}")
        if times.shape != positions.shape[:2]:
            raise ValueError(
                f"times shape {times.shape} does not match positions shape {positions.shape}"
            )
        if not np.isfinite(times).all() or not np.isfinite(positions).all():
            raise ValueError("times and positions must contain only finite values")
        if times.shape[1] > 1 and not np.all(np.diff(times, axis=1) > 0.0):
            raise ValueError("times must be strictly increasing along each agent row")

        object.__setattr__(self, "times", _readonly_copy(times))
        object.__setattr__(self, "positions", _readonly_copy(positions))

    @property
    def n_agents(self) -> int:
        """Number of agents ``N``."""
        return int(self.positions.shape[0])

    @property
    def n_waypoints(self) -> int:
        """Number of waypoints ``M`` per agent."""
        return int(self.positions.shape[1])


@dataclass(frozen=True)
class Evaluation:
    """Metrics produced by the evaluators.

    Collision metrics are added in Phase 3; this Phase 1 version carries only
    travel-length and timing measurements.
    """

    total_travel_length: float
    """Sum of all segment lengths over all agents."""

    per_agent_travel_length: FloatArray
    """``(N,)`` total distance travelled by each agent."""

    makespan_s: float
    """Latest arrival time minus the common start time."""

    n_agents: int
    """Number of agents the evaluation was computed for."""

    metadata: dict[str, str] = field(default_factory=dict)
    """Method metadata, for example the algorithm name and the seed used."""
