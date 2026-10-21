# Research Notebook and Literature Strategy

**Status:** Initial questions and reading plan; no formal literature review completed.

## Purpose

Build a defensible path from implementation observations to reproducible scientific questions. **An interesting idea is not automatically a research gap.**

## Focus areas

1. Formation sampling and representation.
2. Assignment and matching objectives.
3. Multi-agent path planning and collision avoidance.
4. Continuous trajectory optimization and dynamics constraints.
5. Scalability, approximation, and empirical trade-offs.

## Reading sequence

- First: foundational matching/assignment and multi-agent path finding concepts.
- Next: collision checking and trajectory generation under explicitly matched models.
- Later: recent drone-show and swarm coordination work with accessible code or clear reproducibility details.

Candidate resources to verify and read: SciPy `linear_sum_assignment` documentation; foundational Conflict-Based Search literature; Crazyswarm2 documentation; Skybrush technical documentation. These are starting points, not evidence of a comprehensive survey.

## Literature matrix template

| Citation / DOI | Problem | Assumptions | N / scale | Method | Objective | Safety guarantee | Code/data | Limitations |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| _To be researched_ | | | | | | | | |

## Initial falsifiable hypotheses

- H1: Minimum-total-distance assignment does not necessarily minimize trajectory conflicts under synchronized straight-line motion.
- H2: A faster approximate assignment can offer a useful quality/runtime trade-off as N increases.
- H3: Adding a conflict-aware penalty or a separate scheduling step may improve minimum separation at additional planning cost.

These are **test ideas**, not confirmed findings or claims of novelty.

## Research progression

Observe failure → state a measurable hypothesis → search relevant prior work → match assumptions and baselines → design controlled experiment → reproduce and analyze → reassess novelty.

## Research log template

**Date / Question / Related work / Hypothesis / Setup / Observations / Counterexamples / Next step.** Include citations and links to exact experiment configuration and commit when available.

## Publication standard

Do not claim optimality, safety, scalability, or novelty beyond proofs or measured evidence. State hardware, environment, seeds, sample sizes, and known limitations.
