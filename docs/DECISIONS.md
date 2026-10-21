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

## Open decisions

- Whether and when to publish a release on PyPI under the `swarmlab-formations` distribution name.
- Whether `CITATION.cff` and `CHANGELOG.md` are added at the research milestone or earlier.
- Whether the first playground is a script, a notebook, or both.
- Which Python versions beyond 3.12 and 3.13 enter the CI matrix.

## New record template

**ID / Date / Status / Context / Alternatives / Decision / Consequences / Revisit trigger.**
