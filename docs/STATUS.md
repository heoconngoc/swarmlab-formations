# Project Status

**Last updated:** 2026-10-22  
**Stage:** Pre-alpha — Phases 1 and 2 implemented, Phase 2 exit gate pending human review  
**Current phase:** Phase 2 (Assignment) — code complete, benchmarks recorded, awaiting approval  
**GitHub repository:** https://github.com/heoconngoc/swarmlab-formations (public)  
**Continuous integration:** Green — lint, format, and tests on Python 3.12 and 3.13  
**Implementation:** Formations, four assignment solvers plus a SciPy reference, linear trajectories, travel metrics, Plotly viewer and comparison figures, and the Phase 1 and Phase 2 runners are implemented and tested

## Approved direction

- Balanced learning + engineering + research potential.
- Algorithms and optimization are primary; visualization supports understanding.
- English documentation.
- Python + Plotly as initial visualization path.
- Guided AI collaboration: plan and explain before substantive code.
- Educational implementation first, standard reference libraries for verification and scale.
- MIT license; public repository named `swarmlab-formations`.
- `uv` + `pyproject.toml` for dependency management; GitHub Actions for CI.

## Completed

### Phase 0 — Foundation

- Discussed project goals, initial architecture, phase structure, and documentation inventory.
- Prepared the initial documentation draft.
- Human review of all 11 Markdown files; documentation baseline approved.
- Open decisions resolved: license (MIT), repository name and visibility, dependency tooling.
- Repository scaffolding: `pyproject.toml`, `src/swarmlab/` skeleton, `tests/`,
  `.github/workflows/ci.yml`, `.gitignore`, `LICENSE`.
- Verified the documented setup from a clean clone of the published repository.

### Phase 1 — Formation Playground

- Core contracts in `src/swarmlab/models.py`: `Scenario`, `Assignment`, `Trajectory`,
  `Evaluation`, `Constraints`, `Interpolation`. Every dataclass is frozen and stores
  independent read-only array copies, and validates shape, finiteness, permutation
  validity, and time monotonicity at construction time.
- Deterministic formation generators in `src/swarmlab/formations/`: rectangular lattice
  (`grid`), Fibonacci-lattice sphere (`sphere`), and cube-surface projection
  (`cube_surface`), registered in the `FORMATIONS` mapping.
- Seeded random assignment in `src/swarmlab/assignment/random.py`. It is a baseline,
  not an optimizer, and is reported as such.
- Linear baseline trajectory in `src/swarmlab/trajectories/linear.py` with the
  per-agent `(N, M)` time layout, plus the vectorized position sampler in
  `src/swarmlab/trajectories/interpolate.py`.
- Travel-length and makespan metrics in `src/swarmlab/evaluation/metrics.py`.
- Plotly viewer in `src/swarmlab/visualization/viewer.py`: animated agent markers, the
  path of a selected agent, equal data aspect, and a red **not collision-safe**
  annotation. It never writes to a trajectory.
- Phase 1 runner and CLI in `src/swarmlab/experiments/phase1.py`, reachable as
  `python -m swarmlab.experiments.phase1` and as the `swarmlab-demo` console script.
- Tests: 89 passing, 97% statement coverage. Includes a golden fixture for `grid(8)`,
  surface-norm checks for the sphere and the cube, reproducibility checks, endpoint
  correctness, mutation guards, and a subprocess test proving the core never imports
  Plotly.
- Decisions recorded: D-010 (demo entry point), D-011 (trajectory time layout),
  D-012 (formation density convention).

### Phase 1 — defects found after acceptance

Two defects survived the Phase 1 exit gate and were fixed on 2026-10-22, each with a regression
test:

- **Sphere angular step.** `formations/sphere.py` advanced the azimuth by `1/φ` radians
  (35.4°) instead of the golden angle `2π/φ` (137.5°). Points were still on the unit sphere and
  still distinct, so every invariant test passed, but they lined up along a spiral: the
  nearest-neighbour coefficient of variation was 0.09-0.17 instead of about 0.02. The exact
  coordinates of `sphere(4)` and a spread test (CV < 0.05, max/min < 1.25) now pin the angle.
- **Dead time slider.** Plotly slider steps address frames by *name*, and the viewer passed the
  frame time as a float, so every step pointed at a frame that did not exist. Frames now have
  stable names (`t000`, `t001`, ...), the steps reference them, and Play/Pause buttons were added.
  Tests assert that every step names a real frame and that consecutive frames differ.

Lesson recorded for later phases: invariant tests ("points are on the sphere", "frames exist")
cannot detect a wrong sampling rule; at least one test must check a *distribution* or a
*reference value*.

### Phase 2 — Assignment

- Cost layer in `assignment/costs.py`: one dense `(N, N)` matrix per scenario, built from a named
  objective (`euclidean_distance` or `squared_distance`), plus `total_cost` and a
  `COST_FUNCTIONS` registry.
- Four matrix solvers in `assignment/`: `greedy` (agent order, nearest free target),
  `greedy_pair` (cheapest free pair first), `hungarian` (educational Kuhn-Munkres, `O(N³)`), and
  `scipy` (reference optimum). `random` remains the seeded Phase 1 baseline. Registered in
  `MATRIX_SOLVERS`.
- Brute-force oracle in `exact.py` for `N <= 8`, tested against both SciPy and the Hungarian
  implementation.
- Phase 2 runner in `experiments/phase2.py`, reachable as `swarmlab-assign`. It times matrix
  construction separately, reports median/min/max solver time over repeated calls, computes the
  optimality gap, exports CSV, and **refuses** to emit a record when a heuristic beats the exact
  optimum or when two exact solvers disagree on the objective value.
- Comparison figures in `visualization/comparison.py`: straight paths under several assignments
  (one 3D scene each) and cost/runtime curves against `N` with every seed shown.
- Tests: 206 passing, 98% statement coverage. Assignment tests cover permutations, the
  `optimum <= each heuristic` bound, brute-force and Hungarian agreement with SciPy over many
  random, tied-integer, and negative-cost matrices, determinism, and rejection of malformed
  input. Runner tests cover reproducibility, the report, the CSV schema, skipped-method rows, and
  the invalid-record guards.
- Recorded benchmark: `experiments/records/phase2_sweep_8c8a9e2.csv`, summarised in
  [Experiments](EXPERIMENTS.md). Medians over seeds 0-2, `grid -> sphere`, Euclidean objective:

  | N | random | greedy | greedy_pair | scipy / hungarian |
  | --- | --- | --- | --- | --- |
  | 50 | +173.0% | +55.8% | +5.3% | optimum |
  | 100 | +285.8% | +23.3% | +11.1% | optimum |
  | 250 | +338.1% | +40.5% | +9.5% | optimum |
  | 500 | +355.3% | +44.7% | +9.0% | optimum |
  | 1000 | +402.4% | +35.8% | +12.1% | optimum |

  Hungarian and SciPy agree on the objective value at every size and seed. At `N = 1000` the
  educational solver takes 425 ms against 23 ms for SciPy; `greedy_pair` takes 218 ms, slower than
  either exact solver despite its lower asymptotic class.
- Decisions recorded: D-013 (one cost matrix, two named objectives), D-014 (two greedy
  baselines), D-015 (educational Hungarian plus SciPy at scale), D-016 (record format and figure
  split). D-012 was clarified: the grid fallback takes the smallest fitting `c` per `(a, b)`.

## Not completed

- Collision analysis and minimum-separation evaluation (Phase 3).
- Collision-aware planning and staggered departures (Phase 4).
- Experiment matrix, benchmark scripts, and result records (Phase 5).
- Literature review and any published-method reproduction (Phase 6).
- `CITATION.cff` and `CHANGELOG.md` (deferred to the research milestone).

## Immediate next actions

1. Human review of the Phase 2 exit gate: `uv run swarmlab-assign --html results/compare.html`
   for the comparative figure, `--sweep` for the benchmark, and
   `experiments/records/phase2_sweep_8c8a9e2.csv` for the recorded numbers.
2. On approval, start Phase 3: analytic continuous-time separation between linear segments, with
   vectorized pair evaluation and constructed counterexamples where frame sampling misses a
   collision.

## Blockers / risks

No technical blockers. Known risks: scope creep; premature claims about physical collision
safety; the roadmap's time estimates assume uninterrupted work and are re-baselined after each
phase; name similarity with unrelated `swarmlab` projects (mitigated by the
`swarmlab-formations` name).

Phase-specific limitations that must be repeated in any report:

- **Scenario diversity is thin.** Formations are deterministic functions of `N`, so the seeds in
  the Phase 2 record change only the random baseline; every other method returns the same
  assignment for seeds 0, 1, 2. Seed variation becomes meaningful only when scenarios are
  perturbed (rotation, jitter) or new formation pairs are added, which is Phase 5 work.
- **A cost-optimal assignment is not collision-safe.** Nothing in Phase 2 checks separation; the
  linear paths cross routinely, and the runner still prints the warning.
- **The random baseline is not a lower bound.** Its cost is an upper bound on achievable quality;
  the gap it shows is an upper bound on the gain from optimizing, not a typical one.

## Update template

**Date / Phase / Changes / Verified tests / Evidence / Open issues / Next approved task.**
