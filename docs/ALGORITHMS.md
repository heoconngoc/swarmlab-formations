# Mathematical Models and Algorithms

**Status:** Phase 1 models are implemented and tested. Later algorithms are planned, not implemented.

## Notation

- `N`: number of agents; `S = {s_i ∈ R³}` source coordinates; `T = {t_j ∈ R³}` target coordinates.
- `π`: permutation mapping source agent `i` to target `π(i)`.
- `p_i(t)`: agent `i` position at time `t`.
- `d_min`: minimum permitted pairwise separation, in consistent units.

## Initial assumptions

Fixed N, one target per agent, centralized offline planning, point agents, obstacle-free Euclidean 3D space, known coordinates, synchronized time. Initially ignore acceleration, rotor dynamics, and uncertainty. These assumptions must be attached to every result.

## Formation generation

Generate finite `N×3` arrays with deterministic sampling. Start with a regular grid, a Fibonacci-lattice sphere, and cube-surface points. Document sampling density and duplicate handling; do not treat visually similar shapes as identical distributions.

### Implemented rules (Phase 1)

All three generators fill the cube `[-1, 1]^3` and use no random numbers, so the same `N` always
produces exactly the same points.

**Grid.** Each axis is sampled with `linspace(-1, 1, count)`, so every axis spans the whole cube
regardless of how many samples it carries. The spatial density is therefore `N/8` points per unit
volume for any `N`, which keeps the grid comparable with the other formations.

Axis counts `(a, b, c)` with `2 ≤ a ≤ b ≤ c` are chosen as follows:

1. If `N = a·b·c` has an exact three-way factorization, the factorization with the smallest aspect
   ratio `c/a` is used. The lattice is then exactly filled, with no leftover points.
2. Otherwise a box with `a·b·c ≥ N` is chosen by the same rule, and the first `N` points in
   `z`-major order are kept (`x` varies fastest, then `y`, then `z`). The formation then fills the
   box except for a partial final slab.

Both rules are exhaustive and deterministic, so a grid is reproducible from `N` alone. Because
`a ≤ N^(1/3)` and `b ≤ sqrt(N/a)` for any exact factorization, the search is bounded by a small
constant number of candidates.

**Sphere (Fibonacci lattice).** With `i = 0 … N-1`:

`z_i = 1 − 2(i + 0.5)/N`, `r_i = √(1 − z_i²)`, `θ_i = 2π(i + 0.5)/φ`, `φ = (1 + √5)/2`

`p_i = (r_i cos θ_i, r_i sin θ_i, z_i)`

The half-offset `i + 0.5` keeps points off the poles, and the golden angle spreads longitudes
evenly. Since `r_i² + z_i² = 1` by construction, `‖p_i‖ = 1` up to floating-point error.

**Cube surface.** The sphere points are projected radially onto the cube boundary:

`scale = max(|x|, |y|, |z|)`, `q = p / scale`

Then `max(|q_x|, |q_y|, |q_z|) = 1`, so `q` lies exactly on the cube surface. Reusing the sphere
generator keeps the cube evenly covered and avoids a second, separately tuned sampling rule.

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

### Implemented layout (Phase 1)

A trajectory stores `times` with shape `(N, M)` and `positions` with shape `(N, M, 3)`: one row of
waypoint times per agent. Phase 1 uses a synchronized schedule, so all rows are identical, but the
layout already supports staggered departures, which Phase 4 needs, without a data refactor.
Interpolation semantics are carried explicitly on the trajectory (`LINEAR` or `HOLD`).

Sampling a position at an arbitrary time `t` finds, for every agent, the segment that contains `t`.
Because the times of each row are strictly increasing, the segment index is the number of waypoints
strictly before `t` minus one, clamped to `[0, M-2]`. The lookup is expressed as array operations
over the whole `(N, M)` grid rather than a loop over agents, and the interpolation ratio is clamped
to `[0, 1]` so that a time outside the trajectory span pins to the first or last waypoint.

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
