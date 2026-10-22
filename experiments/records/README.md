# Result records

One file per recorded run. The filename carries the short commit hash of the code that produced
it, so a record can be tied back to its implementation.

| File | Phase | Scope |
| --- | --- | --- |
| `phase2_sweep_8c8a9e2.csv` | 2 | `grid -> sphere`, Euclidean objective, N = 50-1000, seeds 0-2, 7 timed calls per method |

## `phase2_sweep_8c8a9e2.csv`

Columns, in order:

| Column | Meaning |
| --- | --- |
| `n` | Number of agents |
| `seed` | Scenario seed |
| `source`, `target` | Formation names |
| `objective` | Cost function that defines the matrix |
| `method` | `random`, `greedy`, `greedy_pair`, `hungarian`, `scipy` |
| `assignment_cost` | Objective value of the chosen bijection |
| `travel_length` | Measured length of the linear paths |
| `gap_vs_reference` | `(cost - optimum) / optimum` |
| `solve_time_ms` | Median of the timed solver calls |
| `solve_time_min_ms`, `solve_time_max_ms` | Observed range over those calls |
| `repeats` | Number of timed calls behind the median |
| `reference_method` | Exact method that defines the optimum |
| `status` | `ok`, or `skipped_for_size` |
| `note` | Why a row was skipped |

A skipped row has empty numeric fields and must never be read as a zero. Cost values are
deterministic and reproducible; timing values are machine dependent and only comparable within
the environment recorded in [EXPERIMENTS.md](../../docs/EXPERIMENTS.md).

Regenerate the run and its figure with:

```bash
uv run swarmlab-assign --sweep 50,100,250,500,1000 --seeds 0,1,2 --repeats 7 \
  --csv results/phase2_sweep.csv --html results/phase2_curves.html
```

Cost values will match the committed record; timings will not, and are not expected to.
