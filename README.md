# SwarmLab

**An interactive laboratory for drone swarm formation, assignment, and trajectory optimization.**

[![CI](https://github.com/heoconngoc/swarmlab-formations/actions/workflows/ci.yml/badge.svg)](https://github.com/heoconngoc/swarmlab-formations/actions/workflows/ci.yml)
[![Python](https://img.shields.io/badge/python-3.12%2B-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Status](https://img.shields.io/badge/status-pre--alpha-lightgrey.svg)](docs/STATUS.md)

> **Status: pre-alpha — documentation-first.**
> This repository contains specifications, a decision log, and a minimal Python package skeleton.
> No algorithm is implemented yet, and **no result here has been measured**.
> [Status](docs/STATUS.md) records what is actually complete.

SwarmLab is an algorithms-first learning and experimentation project. It studies how many
simulated drones can transition between 3D formations efficiently and safely. Interactive
visualizations make the algorithms inspectable; they are not the project's primary objective.

## What this project is

- A learning project for assignment, trajectory planning, and collision analysis.
- An idealized, offline, centralized simulator of point agents.
- A reproducible benchmark harness that runs without a renderer.
- A credible path toward reproducing published methods.

## What this project is not

- **Not a flight controller.** Early versions use idealized point agents, not physically accurate
  quadcopters. No real-drone operation or safety certification is implied.
- Not a physically accurate flight simulator, and not a drone-show choreography product.
- Not a claim of research novelty. Published baselines come first.
- Not a distributed-coordination or reinforcement-learning system.

## Central question

How can we efficiently assign agents to target positions and plan trajectories between 3D
formations while controlling travel cost, computation time, and collision risk?

This is a guiding question, **not** a claim of research novelty.

## Core loop

```text
Scenario / Formation generator -> Assignment solver -> Trajectory planner
        -> Evaluator (metrics + continuous-time collision check) -> Experiment records
        -> Plotly viewer (read-only)
```

The algorithm core never imports Plotly, notebooks, or a browser. Visualization is a diagnostic
layer, never the source of a metric.

## Roadmap

| Phase | Focus | Status |
| --- | --- | --- |
| 0 | Foundation and specifications | in progress |
| 1 | Formation playground (50-100 agents, linear trajectories, Plotly) | planned |
| 2 | Assignment: random, greedy, exact, SciPy reference | planned |
| 3 | Collision analysis: analytic continuous-time separation | planned |
| 4 | Collision-aware planning baseline | planned |
| 5 | Scalability and benchmark matrix (N up to 1000) | planned |
| 6 | Research exploration and literature reproduction | optional |

Phase gates require human review. See [Roadmap](docs/ROADMAP.md) for exit criteria.

## Quick start

```bash
git clone https://github.com/heoconngoc/swarmlab-formations.git
cd swarmlab-formations
uv sync --all-extras      # create .venv and install dependencies
uv run pytest             # run the test suite
uv run ruff check .       # lint
```

**What works today:** the environment builds, the test suite runs, and the linter passes.
**What does not exist yet:** there is no scenario generator, no assignment solver, and no
trajectory planner. The first runnable demo arrives in Phase 1. Do not infer functionality from
this document.

## Repository layout

```text
src/swarmlab/        # library package (algorithms core, no viewer imports)
tests/               # deterministic unit and invariant tests
experiments/         # versioned experiment configs and result records
docs/                # specifications, protocol, and decision log
```

The module contract for each package is specified in [Architecture](docs/ARCHITECTURE.md).

## Documentation

| Document | Purpose |
| --- | --- |
| [Vision](docs/VISION.md) | Goals, boundaries, and success criteria |
| [Roadmap](docs/ROADMAP.md) | Phase-by-phase milestones and exit gates |
| [Architecture](docs/ARCHITECTURE.md) | Modules, contracts, and dependencies |
| [Algorithms](docs/ALGORITHMS.md) | Mathematical formulation and baseline methods |
| [Development](docs/DEVELOPMENT.md) | Setup and engineering workflow |
| [Experiments](docs/EXPERIMENTS.md) | Reproducible evaluation protocol |
| [Research](docs/RESEARCH.md) | Reading strategy, questions, and hypotheses |
| [Status](docs/STATUS.md) | Current work and next action |
| [Decisions](docs/DECISIONS.md) | Design decision log |
| [Agent instructions](AGENTS.md) | Rules for AI collaborators |

## Research direction

Initial hypotheses (test ideas, **not** findings):

- **H1** - Minimum-total-distance assignment does not necessarily minimize trajectory conflicts
  under synchronized straight-line motion.
- **H2** - A faster approximate assignment can offer a useful quality/runtime trade-off as N grows.
- **H3** - A conflict-aware penalty or a separate scheduling step may improve minimum separation
  at additional planning cost.

Method and literature plan in [Research](docs/RESEARCH.md).

## Contributing

Issues and pull requests are welcome, especially corrections to the mathematics or the protocol.
Read [AGENTS.md](AGENTS.md) for the collaboration rules this project follows - in short, changes
are proposed, explained, and approved before they land, and every result must be reproducible
from a recorded configuration.

## License

MIT - see [LICENSE](LICENSE). Code contributed after this point is released under the same terms.

## Frequently asked questions

**Is this a system that flies drones?** No. Agents are idealized points in a simulated 3D
workspace. No hardware, radio, or flight-control code exists in this repository.

**Is the output collision-safe?** No. The Phase 1 baseline is explicitly labelled
**not collision-safe**. Analytic continuous-time separation checking is planned for Phase 3, and
collision-aware planning for Phase 4. Nothing here is a safety guarantee about physical drones.

**Does this project contain original research?** Not yet. Phase 6 reproduces a published method
before any hypothesis is tested. Novelty is not a goal.

**Where do benchmark results live?** `experiments/` holds versioned configs and machine-readable
records. Large raw outputs are regenerable and are not committed by default, per
[Development](docs/DEVELOPMENT.md) and [Experiments](docs/EXPERIMENTS.md).
