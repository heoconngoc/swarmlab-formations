# Roadmap

**Status:** Approved · Phase 0 in progress. Durations are rough planning ranges in working time,
not deadlines; they are re-baselined with measured evidence after Phase 1.

## Phase 0 — Foundation and specifications

**Goal:** Make scope, contracts, development conventions, and test strategy coherent.

**Tasks:** Review and approve the documentation baseline; select license, repository name and visibility; select dependency tooling; create the project skeleton, dependency manifest, lockfile, CI workflow, and smoke tests; define the scenario schema.

**Exit gate:** Documents approved; reproducible environment and basic tests verified; `STATUS.md` updated.

## Phase 1 — Formation Playground (about 1–2 weeks)

**Learn:** Coordinate systems, vectors, Euclidean distance, point sampling, interpolation.

**Build:** Deterministic grid, sphere, and cube-surface generators; 50–100 point agents; simple synchronized linear trajectories; Plotly animation, pause/play where supported, camera orbit, selected-agent trajectory; total travel distance.

**Tests:** Shape/count, finite coordinates, seed reproducibility, endpoint correctness, no accidental mutation.

**Exit gate:** Re-runnable example and tests; visualization visibly labeled **not collision-safe**.

## Phase 2 — Assignment (about 2–3 weeks)

**Learn:** Cost matrices, permutations, greedy limitations, bipartite matching, Hungarian algorithm, asymptotic analysis.

**Build:** Random seeded assignment, simple greedy baseline, small-scale educational optimal implementation; verify against `scipy.optimize.linear_sum_assignment` for suitable instances. Use reference solver for larger N.

**Tests:** Valid bijections, tiny exhaustive optimum comparisons, deterministic tie handling where applicable, cost consistency.

**Exit gate:** Comparative visualizations and repeatable runtime/cost benchmarks; reference agreement on objective values.

## Phase 3 — Collision analysis (about 1–2 weeks)

**Learn:** Relative motion, minimum separation, continuous vs sampled-time checking.

**Build:** Piecewise-linear trajectory representation and analytic minimum-distance checking on overlapping time intervals; conflict events and Plotly highlighting.

**Tests:** Crossing, parallel, stationary, touching threshold, non-overlapping intervals, boundary times.

**Exit gate:** Correct on constructed counterexamples where frame sampling misses a collision, and the evaluator completes N = 1000 in under one second (see `ARCHITECTURE.md`, performance expectations).

## Phase 4 — Collision-aware planning (about 4–6 weeks)

**Learn:** Scheduling, priorities, planning constraints, completeness/optimality distinctions.

**Build:** One deliberately modest collision-aware baseline (e.g., staggered departures or prioritized planning), with explicit failure outcomes and constraints; compare to unsafe linear baseline.

**Tests:** Safety checked with Phase 3 evaluator; termination/failure cases; no unsupported global guarantees.

**Exit gate:** Clear trade-offs among feasibility, makespan, distance, and planning time.

## Phase 5 — Scalability and experimentation (about 2–3 weeks)

**Build:** Scenario matrix over 50, 100, 250, 500, 1000 agents as feasible; repeated seeds; profiling; data export; performance plots; separate rendering and planning times.

**Exit gate:** Reproducible benchmark scripts and report; bottlenecks identified with evidence; the evaluator stays under one second at N = 1000.

## Phase 6 — Research exploration (open-ended, optional)

**Build:** Focused literature matrix; select reproducible method; implement or integrate under matched assumptions; test one falsifiable hypothesis; document limitations.

**Exit gate:** Technical report with citations, experiment settings, comparisons, and honest conclusions; publication is not a required outcome.

## Phase discipline

Each phase must produce: (1) a concept understood and implemented, (2) a visible or inspectable artifact, and (3) tests or quantitative evaluation. Do not silently start later phases.
