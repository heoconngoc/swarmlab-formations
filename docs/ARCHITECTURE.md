# Architecture

**Status:** Proposed design, not an implemented directory tree.

## Design rule

**Headless algorithms first.** The computation and evaluation pipeline must run without Plotly, notebooks, browsers, or an API server.

## Logical data flow

`Scenario / Formation Generator → Assignment Solver → Trajectory Planner → Evaluator → Experiment Records`

`Experiment Records / Trajectories → Plotly Viewer (read-only)`

## Components and responsibilities

| Component | Responsibility | Does not own |
| --- | --- | --- |
| Scenario | Workspace, agents, source/target positions, constraints, seed | Rendering |
| Formation generator | Deterministic N-point coordinate sets | Assignment |
| Assignment solver | Bijective mapping from agents to targets | Physical trajectories |
| Trajectory planner | Time-parameterized motion with explicit assumptions | Visualization |
| Collision evaluator | Minimum separation and conflict events | Path modification |
| Metrics evaluator | Costs, runtime, makespan, safety metrics | Algorithm selection |
| Experiment runner | Parameter sweeps, seeds, repetitions, exports | Interactive UI |
| Plotly viewer | Render formations, paths, events and comparisons | Authoritative metric calculation |

## Canonical contracts (conceptual)

- `Scenario`: `source_positions: float[N,3]`, `target_positions: float[N,3]`, `seed`, `constraints`.
- `Assignment`: integer vector `target_index[N]` containing each integer `0..N-1` exactly once.
- `Trajectory`: per-agent ordered `(time, position[3])` waypoints with increasing times; interpolation semantics explicit.
- `Evaluation`: scalar metrics, per-agent measurements, conflicts, and method metadata.

Use SI-like units when meaningful: meters and seconds. Early formation coordinates may be dimensionless; do not mix them with physical safety distances without declaring a scale.

## Package structure

The distribution name on PyPI is `swarmlab-formations`; the import package name is `swarmlab`
(see `DECISIONS.md` D-008). The layout below is the target structure; only the package skeleton
exists today.

```text
src/swarmlab/
  __init__.py
  py.typed
  models.py
  formations/
  assignment/
  trajectories/
  evaluation/
  experiments/
  visualization/
tests/
experiments/
```

## Dependency boundaries

- Numerical core: Python standard library and NumPy.
- Reference methods may use SciPy but educational implementations should remain independently testable.
- Viewer imports results from core; core must not import Plotly.
- Benchmark runner must exclude visualization overhead from algorithm timings.
- A future API or web viewer is optional and should consume stable exported data contracts.

## Performance expectations

Measured on the development machine (Python 3.12, NumPy 2.5, SciPy 1.18) while bootstrapping the
repository:

| Operation | Scale | Observed time |
| --- | --- | --- |
| `scipy.optimize.linear_sum_assignment` | N = 1000, dense | ~30 ms |
| Analytic separation, vectorized over all agent pairs | N = 1000 (499,500 pairs) | ~31 ms |
| Same separation math, Python double loop | N = 250 | ~108 ms |

The last row extrapolates to roughly 28 s at N = 1000 with four segment pairs per agent pair,
which is too slow for a benchmark matrix of repeated seeds. Consequences:

- The collision evaluator **must** be vectorized over agent pairs. Scalar loops are acceptable
  only in tests and in the educational implementations of Phase 3.
- Phase 3 and Phase 5 exit gates require the evaluator to finish N = 1000 in under one second.
- The SciPy reference solver is fast enough to serve as the optimal baseline at N = 1000, so the
  roadmap does not need an approximate assignment method purely for runtime reasons.

## Design risks and decisions to revisit

Point-agent model ignores dynamics; formation sampling may bias comparisons; assignment cost does not capture collision risk; naive pairwise safety evaluation scales quadratically per segment pair. Record revisions in `DECISIONS.md`.

