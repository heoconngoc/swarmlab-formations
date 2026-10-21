# Development Workflow

**Status:** Approved baseline. Environment bootstrapped; CI not yet observed green.

## Environment

- Python 3.12 or newer. CI verifies 3.12 and 3.13.
- `uv` manages the environment, the lockfile, and the build. `pyproject.toml` holds project metadata.
- Runtime dependencies: NumPy (core numerics), SciPy (reference solvers), Plotly (viewer),
  pandas and Matplotlib (experiment analysis).
- `dev` extra: pytest, pytest-cov, ruff. Formatting and linting use `ruff`.
- `uv.lock` is committed so every environment resolves to the same dependency versions.

## Setup commands

```bash
git clone https://github.com/heoconngoc/swarmlab-formations.git
cd swarmlab-formations
uv sync --all-extras        # create .venv and install runtime + dev dependencies
uv run pytest               # run the test suite
uv run ruff check .         # lint
uv run ruff format .        # format
```

`uv run` uses the project environment automatically; activating `.venv` manually is optional.

## Working cycle

1. Read `STATUS.md` and the current `ROADMAP.md` phase.
2. Write a small problem statement, assumptions, examples, and implementation plan.
3. Obtain approval for substantive work.
4. Implement one narrow change with tests and simple reproducible examples.
5. Run tests; record exact commands and results.
6. Update `STATUS.md`; add a decision record if architecture changed.
7. Commit a coherent increment with a descriptive message.

## Code conventions

- Type annotations on public Python functions; concise docstrings for mathematical contracts.
- Functions should accept explicit inputs and return outputs rather than modifying global state.
- Deterministic random generation via explicit RNG/seed, not hidden global randomness.
- Validate array shape, finite values, and valid permutation constraints at boundaries.
- Keep algorithms separate from visualization and experiment orchestration.
- Name cost functions unambiguously (`euclidean_distance`, `squared_distance`).
- Separate educational algorithms from reference solver wrappers.

Note on tooling: `ruff format` also formats Python code blocks embedded in Markdown files, so `ruff format --check .` covers `docs/*.md` and the repository README. A documentation-only edit can therefore fail CI if it contains a Python snippet that is not ruff-formatted. Run `ruff format .` before committing.

## Testing hierarchy

- Unit tests for geometry and cost calculations.
- Invariant/property tests for permutations and trajectory endpoints.
- Tiny exhaustive oracle tests for assignment optimality.
- Analytic geometry tests for collision detection.
- Integration tests for scenario → solver → trajectory → metrics.
- Benchmarks are **not** pass/fail correctness tests unless thresholds are justified.

## Git workflow

Use small branches and reviewable commits; do not force-push shared branches without approval. Keep generated animations, caches, local environments, and large benchmark outputs out of version control by default. Include small reproducible fixtures where useful. Commit `uv.lock` whenever dependencies change; CI resolves with `--locked` and fails if the lockfile is stale.

## Definition of done

Implemented behavior matches stated assumptions; tests run; limitations documented; visualization matches computed data; no misleading safety claims; status updated. Phase completion requires human approval.

## Environment verification

A clean setup is verified by `uv sync --all-extras` followed by `uv run pytest` on a fresh clone, and by the GitHub Actions workflow in `.github/workflows/ci.yml`. Treat the CI result as the authoritative check, not the local run.
