# Mathematical Models and Algorithms

**Status:** Phase 1 models and the Phase 2 assignment solvers are implemented and tested. Later
algorithms are planned, not implemented.

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

Axis counts `(a, b, c)` are chosen by one of two exhaustive rules:

1. **Exact factorization.** If `N = a·b·c` with `2 ≤ a ≤ b ≤ c`, use the factorization with the
   smallest aspect ratio `c/a`, breaking ties by `(a, b, c)`. The lattice is then exactly filled,
   with no leftover points.
2. **Fallback.** Otherwise, for every pair `(a, b)` with `1 ≤ a ≤ b ≤ ⌈N^(1/3)⌉ + 2`, let `c` be
   the **smallest** integer with `a·b·c ≥ N`, and discard the pair when `c < b`. Among the
   surviving triples minimize the aspect ratio `c/a`, then the waste `a·b·c − N`, then `(a, b, c)`.
   The first `N` points are kept in `z`-major order (`x` varies fastest, then `y`, then `z`), so
   the box is full except for a partial final slab.

Two details of rule 2 are easy to get wrong, so they are stated explicitly.

- `c` is the *smallest* fitting value for each `(a, b)`, not an independently enumerated axis.
  For `N = 97`, `(a, b) = (5, 5)` gives `c = 4 < b`, so `(5, 5, 5)` is not a candidate, and
  `(4, 5, 5)` wins with aspect `1.25` and waste `3`. A rule that minimized aspect over *all*
  triples with `a·b·c ≥ N` would prefer the cube `(5, 5, 5)` and waste 28 points instead. Both
  rules are defensible; the smallest-fitting-`c` rule is the one implemented, and it is the one
  that keeps the leftover slab small.
- The fallback allows `a = 1`; the exact rule does not. A small `N` without a three-way
  factorization therefore becomes a flat slab or a column rather than a degenerate error.

Both rules are deterministic, so a grid is reproducible from `N` alone. Because `a ≤ N^(1/3)` and
`b ≤ sqrt(N/a)` for any exact factorization, and the fallback bound is `O(N^(1/3))` per axis, the
search examines only a small constant number of candidates.

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

The alternative squared-distance cost `Σ_i ||s_i − t_{π(i)}||₂²` is **a different objective**: it
punishes long legs disproportionately, so it can return a different optimal permutation. Every
result must name its objective; a cost number without one is meaningless. On `grid → sphere`,
`N = 100`, `seed = 0`, the two objectives disagree: minimizing the squared cost yields a
permutation whose Euclidean travel is `39.7086` instead of the minimum `39.5667` (0.36% longer),
while minimizing its own objective (`18.8958`). The difference is small here and grows with the
spread of the pair distances.

Both objectives are materialized as a dense `(N, N)` cost matrix `C`, and every solver receives
that same matrix. Building it costs `O(N²)` time and memory (16.8 ms for `N = 1000` on the
development machine) and is timed separately from the solver call.

### Implemented solvers (Phase 2)

| Name | Rule | Time | Optimal |
| --- | --- | --- | --- |
| `random` | Seeded uniform permutation; ignores `C` | `O(N)` | no, a baseline |
| `greedy` | Agents in index order, each takes the nearest free target | `O(N²)` | no |
| `greedy_pair` | Cheapest free pair first, over all `N²` entries | `O(N² log N)` | no |
| `hungarian` | Kuhn-Munkres with row/column potentials | `O(N³)` | yes |
| `brute_force` | Enumerates all `N!` permutations, `N ≤ 8` | `O(N! · N)` | yes |
| `scipy` | `scipy.optimize.linear_sum_assignment` | `O(N³)` worst case, compiled | yes |

The cost of an exact method is a lower bound for every other method,
`optimum ≤ min(random, greedy, greedy_pair)`, and the runner refuses to emit a record that
violates it. The reverse comparisons are unconstrained: either greedy rule may beat the other on
a given instance. The random gap is large and grows with `N` (measured `+173%` at `N = 50`,
`+402%` at `N = 1000`), which is why random is a correctness baseline and not a lower bound.

**Why greedy is not optimal.** With

```text
C = [[  1,   2],
     [  1, 100]]
```

agent-order greedy gives agent 0 target 0 (cost 1) and forces agent 1 onto target 1 (cost 100):
total 101. The optimum is 3. One locally cheap decision consumed the target the other agent
needed. The cheapest-pair rule finds the optimum here, which is exactly the trap: neither variant
is guaranteed to, and one example cannot rank them. Both are baselines whose gap is measured, not
assumed.

**Tie handling.** Equal costs admit many optimal permutations. `brute_force` returns the
lexicographically first optimum because it enumerates in that order; `hungarian` is deterministic
but returns whichever optimum its column scan reaches first; `scipy` may return a third one. Tests
compare objective values, never permutations. Exact ties are common in symmetric scenarios and
rare on `grid → sphere`, where the distances are generic.

**Educational versus reference solver.** `hungarian` and `scipy` agree on the objective value in
every recorded run, which is the Phase 2 exit condition. They do not compete on speed: at
`N = 1000` the educational implementation takes about 425 ms against 23 ms for the compiled
reference, and the ratio grows with `N` because its inner loop is one NumPy expression over `N`
columns per augmentation step. It is kept because it is inspectable and because it is checked
against brute force for `N ≤ 6`, which no library call can provide.

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

Cost matrix construction uses `O(N²)` pair costs and memory in a dense representation.
Hungarian-family implementations are commonly cubic for square dense problems; the exact constant
depends on the implementation, and it matters here: the educational solver and the compiled
reference differ by a factor of roughly 18 at `N = 1000` despite the same asymptotic class. Naive
pairwise separation checks are `O(N²)` per shared segment interval. Benchmark real implementations
rather than assuming constants are negligible.

Measured timings are recorded in `ARCHITECTURE.md` (Phase 1 separation benchmarks) and
`EXPERIMENTS.md` (Phase 2 assignment benchmarks). The relevant consequence for this document: the
separation formula above must be evaluated with array operations over agent pairs, not with scalar
loops, otherwise the quadratic term dominates the benchmark matrix.
