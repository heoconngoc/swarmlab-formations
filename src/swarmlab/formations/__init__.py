"""Deterministic generation of 3D formations.

Every generator returns an ``(N, 3)`` array of finite coordinates inside the
cube ``[-1, 1]^3``. The generators are deterministic: the same ``n`` always
produces exactly the same points, with no dependence on any random state.
"""

from swarmlab.formations.cube import cube_surface
from swarmlab.formations.grid import grid
from swarmlab.formations.sphere import sphere

__all__ = ["FORMATIONS", "cube_surface", "grid", "sphere"]

#: Registry of the available formation kinds, keyed by the name used on the
#: command line and in experiment configurations.
FORMATIONS = {
    "grid": grid,
    "sphere": sphere,
    "cube": cube_surface,
}
