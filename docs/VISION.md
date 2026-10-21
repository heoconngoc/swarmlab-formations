# Vision and Project Charter

**Status:** Approved · Documentation baseline v1.0

## Mission

Build an interactive, reproducible laboratory to learn, implement, evaluate, and eventually investigate algorithms for large-scale 3D drone formation transitions.

## Central question

How can we efficiently assign agents to target positions and plan trajectories between 3D formations while controlling travel cost, computation time, and collision risk?

This is a guiding question, **not** a claim of research novelty.

## Balanced objectives

1. **Learning:** Derive and implement simple versions of algorithms; understand invariants, correctness, and complexity.
2. **Engineering:** Build modular, tested, observable software that can be benchmarked without rendering.
3. **Research potential:** Reproduce published baselines and test clearly stated hypotheses after literature review.

## Principles

- Algorithms first; visualization makes behavior understandable.
- Simple implementation before standard-library verification.
- Model assumptions are explicit and revised deliberately.
- Repeatable experiments beat anecdotal demos.
- Scope expands only after working, tested baselines.
- AI agents are guided collaborators, not autonomous substitutes for learning.

## Initial scope

- Idealized point agents in a 3D Euclidean workspace.
- Fixed-size source/target point formations with unique agent IDs.
- Offline, centralized assignment and planning.
- Deterministic scenario generation with configurable random seeds.
- Simple synchronized linear interpolation as an initial **unsafe baseline**.
- Travel cost, runtime, minimum separation, and conflict measurements.

## Explicit non-goals for early phases

Real drone control; GPS/radio protocols; hardware certification; motor dynamics; obstacles; distributed coordination; reinforcement learning; text-to-formation generation; full drone-show choreography; backend/cloud infrastructure.

## Success criteria

**MVP:** A tested 50–100-agent Plotly demo with deterministic formation generation and inspectable trajectories.

**Engineering milestone:** Multiple assignment methods, independently verified results, continuous-time collision checking for piecewise-linear segments, and reproducible benchmarks.

**Research milestone (optional):** A documented reproduction of a suitable published method, measured limitations, and an honestly scoped hypothesis test. A novel contribution is not guaranteed.

## Audience

Primary: the project author learning CS algorithms. Secondary: future collaborators, coding agents, reviewers, and potentially research mentors.

## Decision policy

Phase gates require human review. `ROADMAP.md` defines implementation stages; `STATUS.md` records what is actually complete.
