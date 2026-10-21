# AI Agent Collaboration Guide

> **Mode: GUIDED.** The human is learning algorithms and retains control over scope and important design decisions.

## Read order

1. `docs/STATUS.md` — current phase and known limitations.
2. `docs/VISION.md` — purpose and non-goals.
3. `docs/ROADMAP.md` — authorized phase and exit criteria.
4. `docs/ARCHITECTURE.md` and `docs/ALGORITHMS.md` — module boundaries and mathematical contracts.
5. `docs/DEVELOPMENT.md` and `docs/EXPERIMENTS.md` as relevant.
6. `docs/DECISIONS.md` for historical rationale; `docs/RESEARCH.md` for research tasks.

## Before implementation

- State the problem, assumptions, intended outcome, and current phase.
- Propose a small plan, relevant concepts, data structures, algorithmic complexity, tests, and trade-offs.
- **Wait for human approval before substantive implementation**, dependency additions, architecture changes, or scope expansion.
- For algorithm-learning tasks, prefer intuition, examples, pseudocode, and incremental prompts before full solutions unless the human requests full code.

## During implementation

- Keep the algorithm core independent of Plotly, notebooks, and web frameworks.
- Prefer a transparent baseline implementation followed by comparison against an established reference solver.
- Keep random seeds explicit; use deterministic fixtures for correctness tests.
- Write tests for edge cases, invariants, and failure conditions; avoid unsupported performance claims.
- Never silently substitute discrete collision sampling for a continuous-time safety guarantee.
- Do not introduce robotics middleware, cloud services, databases, or ML without an approved need.
- Do not commit secrets, generated large data, or machine-specific paths.

## After implementation

- Summarize changed files, what was learned, tests actually run, results, and remaining limitations.
- Update `docs/STATUS.md` with verified progress and next steps.
- Record consequential choices in `docs/DECISIONS.md`.
- Update experiment records when benchmarks are executed; label unexecuted examples as illustrative.
- Ask before marking a phase complete or starting the next one.

## Research integrity

- Distinguish known results, hypotheses, observations, and established novelty.
- Cite identifiable sources when making literature claims; never fabricate citations, paper findings, or benchmark results.
- Reproductions must state assumptions, datasets, hardware, and deviations from source methods.

## Source of truth

`VISION.md` owns goals; `ROADMAP.md` owns milestones; `ARCHITECTURE.md` owns module contracts; `ALGORITHMS.md` owns mathematical definitions; `EXPERIMENTS.md` owns evaluation methodology; `STATUS.md` owns current progress. Avoid copying definitions across files.
