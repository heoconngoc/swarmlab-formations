# Project Status

**Last updated:** 2026-10-21  
**Stage:** Pre-alpha — documentation approved, repository bootstrapped  
**Current phase:** Phase 0 (scaffolding)  
**GitHub repository:** https://github.com/heoconngoc/swarmlab-formations (public)  
**Implementation:** Package skeleton only; no algorithms implemented

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

- Discussed project goals, initial architecture, phase structure, and documentation inventory.
- Prepared the initial documentation draft.
- Human review of all 11 Markdown files; documentation baseline approved.
- Open decisions resolved: license (MIT), repository name and visibility, dependency tooling.
- Repository scaffolding: `pyproject.toml`, `src/swarmlab/` skeleton, `tests/`,
  `.github/workflows/ci.yml`, `.gitignore`, `LICENSE`.

## Not completed

- Scenario generators, assignment solvers, trajectory planners, and collision evaluators
  (Phases 1-4).
- Experiment matrix, benchmark scripts, and result records (Phase 5).
- Literature review and any published-method reproduction (Phase 6).
- `CITATION.cff` and `CHANGELOG.md` (deferred to the research milestone).
- Continuous integration observed green on GitHub Actions (workflow added; first run pending).

## Immediate next actions

1. Verify the first GitHub Actions run is green.
2. Confirm `uv sync --all-extras` and `uv run pytest` from a clean clone.
3. Approve the Phase 0 exit gate.
4. Begin Phase 1: deterministic formation generators and the linear-trajectory baseline.

## Blockers / risks

No technical blockers. Known risks: scope creep; premature claims about physical collision
safety; the roadmap's time estimates assume uninterrupted work and are re-baselined after
Phase 1; name similarity with unrelated `swarmlab` projects (mitigated by the
`swarmlab-formations` name).

## Update template

**Date / Phase / Changes / Verified tests / Evidence / Open issues / Next approved task.**
