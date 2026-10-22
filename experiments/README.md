# Experiments

Versioned experiment configurations and machine-readable result records.

The protocol that governs this directory is specified in
[EXPERIMENTS.md](../docs/EXPERIMENTS.md).

Contents:

- `configs/` - versioned scenario and algorithm configurations (machine-readable). Not created yet:
  every run so far is fully specified by its command line, which is recorded next to the result.
- `records/` - result records. One small CSV per recorded run, named after the code commit that
  produced it.

Large raw outputs (rendered figures, exported datasets) are regenerable and are excluded from
version control by default. See `.gitignore` and [DEVELOPMENT.md](../docs/DEVELOPMENT.md).
Figures from the Phase 2 benchmark, for example, are written to `results/` and rebuilt with the
command recorded in [EXPERIMENTS.md](../docs/EXPERIMENTS.md).
