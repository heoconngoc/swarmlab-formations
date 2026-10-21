# Experiment and Benchmark Protocol

**Status:** Proposed methodology; no results collected yet.

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

Null fields must not be interpreted as zero. Schema is a proposal, not an observed result.

## Validity threats

Different formation sampling; hidden randomization; tie handling; Python overhead; library implementations in compiled code; collision missed by time sampling; overfitting to attractive visual examples; inconsistent units; biased scenario selection.

## Deliverables

Versioned experiment configs, raw result files (or regeneration instructions), scripts to reproduce figures, and a concise limitations section. Do not commit very large artifacts by default.
