# Project Status

**Last updated:** 2026-10-21  
**Stage:** Pre-alpha — Phase 1 implemented, exit gate pending human review  
**Current phase:** Phase 1 (Formation Playground) — code complete, awaiting approval  
**GitHub repository:** https://github.com/heoconngoc/swarmlab-formations (public)  
**Continuous integration:** Green — lint, format, and tests on Python 3.12 and 3.13  
**Implementation:** Formations, random assignment, linear trajectories, travel metrics, Plotly viewer, and the Phase 1 runner are implemented and tested

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

## Not completed

- Assignment solvers beyond the random baseline: greedy heuristic, educational
  exact solver, SciPy reference comparison (Phase 2).
- Collision analysis and minimum-separation evaluation (Phase 3).
- Collision-aware planning and staggered departures (Phase 4).
- Experiment matrix, benchmark scripts, and result records (Phase 5).
- Literature review and any published-method reproduction (Phase 6).
- `CITATION.cff` and `CHANGELOG.md` (deferred to the research milestone).

## Immediate next actions

1. Human review of the Phase 1 exit gate: re-runnable example, tests, and the visible
   *not collision-safe* label.
2. On approval, start Phase 2: greedy and exact assignment solvers with the SciPy
   reference comparison.

## Blockers / risks

No technical blockers. Known risks: scope creep; premature claims about physical collision
safety; the roadmap's time estimates assume uninterrupted work and are re-baselined after
Phase 1; name similarity with unrelated `swarmlab` projects (mitigated by the
`swarmlab-formations` name); the random assignment makes the Phase 1 travel numbers look
worse than any future solver, which is intentional but must be stated in every report.

## Update template

**Date / Phase / Changes / Verified tests / Evidence / Open issues / Next approved task.**
