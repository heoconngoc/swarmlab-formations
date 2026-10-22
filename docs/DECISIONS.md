# Decision Log

This is a lightweight architecture decision record (ADR) log. Decisions may be revisited with explicit rationale; do not rewrite history silently.

## D-001 — Project orientation

**Date:** 2026-10-21  
**Status:** Accepted

**Decision:** Balanced learning, engineering, and research potential, with algorithms and optimization as the core. Visualization supports inspection, not product-first UI development.

**Rationale:** Preserve both hands-on understanding and a credible path to reproducible research.

## D-002 — Initial visualization

**Date:** 2026-10-21  
**Status:** Accepted

**Decision:** Start with Python + Plotly. Revisit Three.js only if interaction or scale requires it.

**Rationale:** Minimize frontend overhead and keep the early project focused on algorithms.

## D-003 — Educational/reference workflow

**Date:** 2026-10-21  
**Status:** Accepted

**Decision:** Implement simple methods to learn; use established libraries such as SciPy to validate and benchmark larger cases.

**Rationale:** Avoid both opaque library-only work and unnecessary reimplementation at scale.

## D-004 — Agent collaboration

**Date:** 2026-10-21  
**Status:** Accepted

**Decision:** Guided collaborator/tutor mode. Human approval precedes substantive changes.

**Rationale:** Learning and architectural ownership remain with the project author.

## D-005 — Documentation language

**Date:** 2026-10-21  
**Status:** Accepted

**Decision:** English for all repository documentation.

## D-006 — Core/viewer separation

**Date:** 2026-10-21  
**Status:** Accepted (confirmed during documentation review, 2026-10-21)

**Decision:** Headless Python core with a read-only Plotly visualization layer and separate experiment runner.

**Rationale:** Enables deterministic testing, benchmarking, and later viewer replacement.

## D-007 — Licensing

**Date:** 2026-10-21  
**Status:** Accepted

**Decision:** MIT license, added as `LICENSE` at repository creation. Contributions are released under the same terms.

**Rationale:** Maximizes reuse for a learning project and is unambiguous for collaborators. Apache-2.0 was considered and rejected because the patent clause adds no value for this scope; GPL-3.0 was rejected because copyleft would restrict reuse of the code.

**Consequences:** The repository is legally reusable as soon as `LICENSE` exists. A future change to a copyleft license is possible but must be recorded as a new decision rather than an edit.

## D-008 — Repository identity and visibility

**Date:** 2026-10-21  
**Status:** Accepted

**Decision:** Public GitHub repository `heoconngoc/swarmlab-formations`. The Python distribution name is `swarmlab-formations`; the import package name stays `swarmlab`.

**Rationale:** `swarmlab` is already taken on PyPI by an unrelated swarm-intelligence package, and an unrelated Matlab drone-swarm simulator uses the same name, so a distinct name avoids search confusion. The import name stays short because it is internal to the project.

**Consequences:** `pip install swarmlab-formations` yields `import swarmlab`. Documentation, badges, and clone URLs must use the full repository name.

## D-009 — Dependency management and CI

**Date:** 2026-10-21  
**Status:** Accepted

**Decision:** `uv` with `pyproject.toml` and a committed `uv.lock`; `hatchling` build backend; `pytest` and `ruff` in a `dev` extra; GitHub Actions runs `ruff` and `pytest` on Python 3.12 and 3.13.

**Rationale:** One tool covers environment creation, locking, and building, which is the precondition for the reproducible experiments required by `EXPERIMENTS.md`. CI runs before the repository is public so every commit is verified.

**Consequences:** Contributors install `uv`; `uv sync --all-extras` is the single setup command. `uv.lock` must be regenerated and committed whenever dependencies change.

## D-010 — Phase 1 demo entry point

**Date:** 2026-10-21  
**Status:** Accepted

**Decision:** The Phase 1 playground is a Python module runner, `swarmlab.experiments.phase1`, reachable as `python -m swarmlab.experiments.phase1` and through the console script `swarmlab-demo`. No notebook is shipped.

**Rationale:** A module runner is importable, testable, and runnable in CI, all three of which a notebook is not. It keeps the experiment reproducible from the command line and lets `tests/` call the same code path a user does. Notebooks were considered and deferred: they are convenient for exploration but add a second, untested entry point.

**Consequences:** The viewer is imported lazily inside the CLI, so `--no-html` runs without Plotly. The phase runner becomes the reference usage example for later phases.

## D-011 — Trajectory time layout

**Date:** 2026-10-21  
**Status:** Accepted

**Decision:** A trajectory stores `times` with shape `(N, M)` and `positions` with shape `(N, M, 3)`, giving every agent its own row of waypoint times, even while Phase 1 uses a synchronized schedule.

**Rationale:** Phase 4 plans staggered departures, where agents start at different times. With one time row per agent, that phase needs no change to the data structures, and the evaluator or the viewer can already work with per-agent schedules. The alternative, a shared `(M,)` time vector, would have to be replaced later.

**Consequences:** Sampling a position at time `t` must look up the segment per agent; the implementation derives the segment index from the number of waypoints before `t`, which is exact because each row is strictly increasing.

## D-012 — Formation density convention

**Date:** 2026-10-21  
**Status:** Accepted

**Decision:** Every formation generator fills the cube `[-1, 1]^3` with a spatially uniform density of `N/8` points per unit volume. For the grid this means each axis is sampled with `linspace(-1, 1, count)` regardless of the sample count.

**Rationale:** `ALGORITHMS.md` warns against treating visually similar shapes as identical distributions. If the grid occupied a smaller region than the sphere, any distance or density comparison would be biased by the sampling rule rather than by the formation. Holding the density fixed makes the comparison about the formation.

**Consequences:** When `N` has no exact three-way factorization, the grid falls back to a near-cubic box with `a·b·c ≥ N` and keeps the first `N` points in `z`-major order, which leaves one partially filled slab. The rule is deterministic and documented in `ALGORITHMS.md`.

*(2026-10-22 clarification, no change of decision:)* the fallback takes, for each candidate `(a, b)`, the **smallest** `c` with `a·b·c ≥ N`, then minimizes the aspect ratio `c/a`, then the waste. The earlier wording "a box with `a·b·c ≥ N` is chosen by the same rule" did not say that `c` is minimal, which makes a cube such as `(5, 5, 5)` look like a candidate for `N = 97` even though it wastes 28 slots. `ALGORITHMS.md` now states the rule exactly as implemented and carries the worked example.

## D-013 — One dense cost matrix defines the assignment objective

**Date:** 2026-10-22  
**Status:** Accepted

**Decision:** All assignment solvers consume the same dense `(N, N)` cost matrix, produced by one of two named objectives: `euclidean_distance` or `squared_distance`. The matrix is built once per scenario and passed unchanged to every method; the objective name is written into every report and record. `random` is the only baseline that ignores the matrix.

**Rationale:** Two methods compared on different matrices are solving different problems, and a cost value without its objective is not interpretable. Materializing the matrix also separates the `O(N²)` construction cost from the solver cost, which the benchmark protocol requires. `squared_distance` is kept because it is a genuinely different objective, not a rescaling: on `grid -> sphere`, `N = 100`, `seed = 0`, optimizing it gives a 0.36% longer Euclidean travel than the Euclidean optimum.

**Alternatives considered:** A `metric=` string inside every solver (rejected: each solver would rebuild the matrix, and they could drift apart); computing costs lazily inside solvers (rejected: same problem plus hidden time in the benchmark); supporting both objectives by transforming the matrix (rejected: the squared objective is not a monotone transform that preserves the optimal permutation).

**Consequences:** Cost matrices are `O(N²)` memory, so `N = 1000` needs 8 MB per matrix and the runner holds exactly one. Rectangular agent/target counts are rejected until a phase needs them.

## D-014 — Two greedy baselines instead of one

**Date:** 2026-10-22  
**Status:** Accepted

**Decision:** Ship both greedy rules: `greedy` (agents in index order, each takes the nearest free target) and `greedy_pair` (globally cheapest free pair first). Both are baselines; neither is presented as an optimizer.

**Rationale:** The roadmap's learning objective is "greedy limitations", and one rule cannot show them. The two rules fail differently, and the measured gaps differ by a factor of about four (5-12% versus 23-56% above the optimum on the recorded scenarios). Keeping both makes "greedy is order-dependent" a measured statement instead of a remark, at the cost of roughly thirty lines and one registry entry.

**Consequences:** Reports and figures carry both names. Tests assert the bound `optimum <= each heuristic` but never an order between the two variants, which is instance dependent.

## D-015 — Educational Hungarian with SciPy at scale

**Date:** 2026-10-22  
**Status:** Accepted

**Decision:** Implement the Kuhn-Munkres algorithm from scratch as the educational exact solver, verify it against brute force for `N <= 6` and against SciPy for `N <= 8` in tests, and use SciPy as the reference optimum and the practical large-`N` solver. Brute force is capped at `N = 8`.

**Rationale:** The roadmap asks for a small-scale educational exact implementation plus a SciPy reference. Both are present, and they are independent: brute force shares no logic with the Hungarian implementation, so agreement is evidence. Measured at `N = 1000`, the educational solver takes about 425 ms against 23 ms for the compiled reference, an 18x factor that is small enough to keep it in the benchmark rather than exclude it.

**Consequences:** The sweep has `--max-hungarian-n` (default 1000) so the educational solver can be excluded beyond a chosen size; skipped rows are written explicitly with `status = "skipped_for_size"`. The educational implementation is not used to produce any reported optimum when SciPy is available.

## D-016 — Phase 2 record format and figure split

**Date:** 2026-10-22  
**Status:** Accepted

**Decision:** Benchmark rows are written as CSV with a fixed column set, one row per `(size, seed, method, status)`, committed under `experiments/records/` when small. Rendered figures go to `results/` and stay git-ignored. Comparative visualization is split into two figures: straight paths under several assignments, and cost/runtime curves against `N`.

**Rationale:** The CSV is small (about 13 KB for 75 rows), diffable on cost values, and readable without pandas. Committing the figures would add hundreds of kilobytes of generated markup that can be regenerated from the record with one command. Splitting the figures keeps each one honest: the path view contains no metric, and the curve view contains no geometry.

**Consequences:** The only committed artifact of a run is the CSV plus the environment block in `docs/EXPERIMENTS.md`. The filename carries the short commit hash, so a record can be tied to the code that produced it. Timing values are medians and are therefore not reproducible bit-for-bit; cost values are deterministic and are.

## Open decisions

- Whether and when to publish a release on PyPI under the `swarmlab-formations` distribution name.
- Whether `CITATION.cff` and `CHANGELOG.md` are added at the research milestone or earlier.
- Whether a notebook front end is added alongside the phase runners.
- Which Python versions beyond 3.12 and 3.13 enter the CI matrix.
- How scenario diversity is introduced before Phase 5: perturbed formations (rotation, jitter) or additional formation pairs. Today the seeds vary only the random baseline, because every formation is a deterministic function of `N`.

## New record template

**ID / Date / Status / Context / Alternatives / Decision / Consequences / Revisit trigger.**
