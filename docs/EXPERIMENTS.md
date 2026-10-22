# Experiment and Benchmark Protocol

**Status:** Protocol in use. Phase 2 assignment benchmark executed and recorded; later phases have
no results yet.

## Goals

Measure assignment quality, planning quality, runtime, safety metrics, and scaling under reproducible conditions. Visualization is diagnostic and excluded from algorithm timing.

## Scenario matrix (proposed)

- Sizes: `N ∈ {50, 100, 250, 500, 1000}` where feasible.
- Transitions: grid→sphere, sphere→cube, cube→grid; add adversarial crossing scenarios.
- Seeds: fixed list, initially 10 per configuration; record exact seed values.
- Baselines: random, greedy, exact/reference assignment; add collision-aware planners later.
- All algorithms on a scenario receive identical source and target coordinates and the same cost definition.

## Primary metrics

| Metric | Definition / caution |
| --- | --- |
| Assignment cost | Sum of chosen pair costs; state Euclidean vs squared Euclidean |
| Total travel length | Sum of actual trajectory segment lengths |
| Makespan | Latest arrival time minus common start |
| Minimum separation | Minimum pairwise distance over shared time domain |
| Conflicting pairs | Number of distinct agent pairs violating threshold |
| Conflict events | Requires a documented event-merging policy |
| Planning time | Timed separately from data generation, I/O, and rendering |
| Evaluator time | Separation checking is timed on its own; it must not be hidden inside planning time |
| Peak memory | Measurement method and tool recorded |

## Protocol

1. Record code commit, Python/library versions, OS, CPU, memory, and optional accelerator.
2. Generate scenarios once per seed; save or deterministically regenerate them.
3. Warm up when appropriate; separate solver construction/setup from solve time where meaningful.
4. Repeat timed runs; report distribution (median, dispersion, and trial count), not only the best run.
5. Validate solver outputs before measuring their quality.
6. Compare algorithms only under matched constraints and declared failure policies.
7. Store machine-readable configuration and results; produce plots from saved records.

## Suggested result record

```json
{
  "status": "illustrative_schema_only",
  "scenario_id": "grid_to_sphere_n100_seed42",
  "seed": 42,
  "n_agents": 100,
  "algorithm": "greedy",
  "objective": "sum_euclidean_distance",
  "planning_time_ms": null,
  "travel_length": null,
  "min_separation": null,
  "hardware": null,
  "commit": null
}
```

Null fields must not be interpreted as zero. The Phase 2 runner writes CSV rows instead of this
JSON object; the field set is `docs`-external and versioned in
`src/swarmlab/experiments/phase2.py::CSV_FIELDS`. Skipped measurements carry
`status = "skipped_for_size"` with empty numeric fields, never zeros.

## Recorded runs

### Phase 2 - assignment solvers

| Field | Value |
| --- | --- |
| Date | 2026-10-22 |
| Code commit | `8c8a9e2` |
| Record | [`experiments/records/phase2_sweep_8c8a9e2.csv`](../experiments/records/phase2_sweep_8c8a9e2.csv) |
| Environment | macOS 26.6 on Apple silicon (`arm64`), CPython 3.12.5, NumPy 2.5.4, SciPy 1.18.1 |
| Scenario | `grid -> sphere`, duration 10 s, seeds 0, 1, 2 |
| Sizes | N = 50, 100, 250, 500, 1000 |
| Objective | `euclidean_distance` (sum of pair distances) |
| Timing | median of 7 calls per method after one warm-up call; matrix construction timed separately |
| Command | see below |

```bash
uv run swarmlab-assign --sweep 50,100,250,500,1000 --seeds 0,1,2 --repeats 7   --csv experiments/records/phase2_sweep_8c8a9e2.csv   --html results/phase2_curves.html
```

Medians over the three seeds:

| N | random | greedy | greedy_pair | hungarian | scipy | scipy time |
| --- | --- | --- | --- | --- | --- | --- |
| 50 | 79.7893 (+173.0%) | 45.5216 (+55.8%) | 30.7831 (+5.3%) | 29.2223 | 29.2223 | 0.017 ms |
| 100 | 152.6481 (+285.8%) | 48.8043 (+23.3%) | 43.9720 (+11.1%) | 39.5667 | 39.5667 | 0.058 ms |
| 250 | 374.5201 (+338.1%) | 120.1005 (+40.5%) | 93.6149 (+9.5%) | 85.4832 | 85.4832 | 0.572 ms |
| 500 | 704.5619 (+355.3%) | 223.8329 (+44.7%) | 168.5967 (+9.0%) | 154.7371 | 154.7371 | 4.483 ms |
| 1000 | 1392.0788 (+402.4%) | 376.3373 (+35.8%) | 310.5633 (+12.1%) | 277.0959 | 277.0959 | 23.012 ms |

Observations, kept separate from interpretation:

- `hungarian` and `scipy` report identical objective values at every size and seed. This is the
  Phase 2 exit condition on reference agreement.
- The random gap grows with `N` (+173% to +402%), so random is a baseline, not a lower bound.
- Neither greedy rule is consistently closer: `greedy_pair` is 5.3-12.1% above the optimum here,
  while agent-order `greedy` is 23-56% above. The ordering of the two variants is instance
  dependent; only the bound `optimum <= each heuristic` is guaranteed.
- Solver time is not ordered by asymptotic class at these sizes: `greedy_pair` (quadratic) is
  slower than the cubic SciPy solver at every measured size.
- The educational Hungarian solver is about 18x slower than SciPy at `N = 1000`, with the same
  result.

**Known limitation of this run.** The formations are deterministic functions of `N`, so the three
seeds change only the random baseline: every other method returns the same assignment for seeds
0, 1 and 2. The seed axis is therefore not yet a diversity axis. Meaningful seed variation needs
perturbed scenarios (rotations, jitter, different formation pairs), which is Phase 5 work; the
seeds are kept in the record so that the omission is visible.

## Validity threats

Different formation sampling; hidden randomization; tie handling; Python overhead; library implementations in compiled code; collision missed by time sampling; overfitting to attractive visual examples; inconsistent units; biased scenario selection.

## Deliverables

Versioned experiment configs, raw result files (or regeneration instructions), scripts to reproduce figures, and a concise limitations section. Do not commit very large artifacts by default.
