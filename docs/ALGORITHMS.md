# Mathematical Models and Algorithms

**Status:** Initial model specification. Later algorithms are planned, not implemented.

## Notation

- `N`: number of agents; `S = {s_i ∈ R³}` source coordinates; `T = {t_j ∈ R³}` target coordinates.
- `π`: permutation mapping source agent `i` to target `π(i)`.
- `p_i(t)`: agent `i` position at time `t`.
- `d_min`: minimum permitted pairwise separation, in consistent units.

## Initial assumptions

Fixed N, one target per agent, centralized offline planning, point agents, obstacle-free Euclidean 3D space, known coordinates, synchronized time. Initially ignore acceleration, rotor dynamics, and uncertainty. These assumptions must be attached to every result.

## Formation generation

Generate finite `N×3` arrays with deterministic sampling. Start with a regular grid, a Fibonacci-lattice sphere, and cube-surface points. Document sampling density and duplicate handling; do not treat visually similar shapes as identical distributions.

## Assignment objective

For Euclidean travel length:

`min_π Σ_i ||s_i − t_{π(i)}||₂`

Alternative squared-distance cost `Σ_i ||s_i − t_{π(i)}||₂²` is **a different objective** and may yield a different assignment. Explicitly name the objective in experiments.

### Planned solvers

- Seeded random permutation: correctness baseline, not optimization.
- Greedy nearest unassigned target: easy educational heuristic; order-dependent, not generally optimal.
- Small-scale exact solver (brute force for tiny N and/or educational Hungarian implementation): verify understanding and optimality.
- SciPy `linear_sum_assignment`: reference optimum for a given linear cost matrix.

A cost-optimal assignment alone does not guarantee collision safety or minimal makespan.

## Baseline trajectories

For normalized time `u∈[0,1]`, linear interpolation is `p_i(u)=(1−u)s_i+u t_{π(i)}`. For physical time `[0,T]`, use `u=t/T`. This is a geometric baseline, not a dynamically feasible or collision-safe trajectory.

## Continuous-time separation for linear segments

For overlapping segment interval `[a,b]`, express relative position as `r(τ)=r₀+v_rel τ`, `τ∈[0,b−a]`. The closest time is

`τ* = clamp(−(r₀·v_rel)/||v_rel||², 0, b−a)`

when `||v_rel||²>0`; otherwise separation is constant. Evaluate `||r(τ*)||` and flag a conflict if it is below `d_min` (boundary equality policy must be specified). For piecewise paths, compare all overlapping segment pairs. This gives exact minimum distance for the **assumed piecewise-linear model**, not a guarantee about physical drones.

## Collision-aware planning candidates

Begin with simple departure-time scheduling or prioritized planning, documenting any incompleteness and inability to find a feasible solution. Explore more sophisticated methods only after baseline measurements and literature review.

## Correctness requirements

- Valid bijective assignments; no NaNs/infinite coordinates.
- Correct trajectory endpoints and strictly ordered timestamps.
- Analytic separation tests for known crossing and near-miss examples.
- Distinguish collision count, number of conflicting pairs, and minimum separation.
- Compare educational and reference solvers on identical cost matrices; ties can produce different permutations with the same optimum.

## Complexity notes

Cost matrix construction uses O(N²) pair costs and memory in a dense representation. Hungarian-family implementations are commonly cubic for square dense problems; exact complexity depends on implementation. Naive pairwise separation checks are O(N²) per shared segment interval. Benchmark real implementations rather than assuming constants are negligible.

Measured timings that motivated the performance gate are recorded in `ARCHITECTURE.md`. The relevant consequence for this document: the separation formula above must be evaluated with array operations over agent pairs, not with scalar loops, otherwise the quadratic term dominates the benchmark matrix.
