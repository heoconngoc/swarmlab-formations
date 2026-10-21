"""Smoke tests for the package skeleton.

These tests intentionally contain no algorithm logic. Behavioural tests are added in Phase 1.
"""

from __future__ import annotations

import swarmlab


def test_package_imports() -> None:
    assert swarmlab.__version__


def test_package_exposes_public_api() -> None:
    assert "__version__" in swarmlab.__all__
