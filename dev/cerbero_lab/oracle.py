"""Ground truth computed directly from synthetic contents, independent of the variant code.

Used to check that the hand-written expectations in each fixture agree with the bytes.
"""
from __future__ import annotations

import hashlib

from .sim import inside


def _denied(scenario, path: str) -> bool:
    return any(f["kind"] == "permission_denied" and inside(path, f["prefix"]) for f in scenario.faults)


def truth_states(scenario) -> dict[str, str]:
    memory = scenario.memory
    after = {p: hashlib.sha256(f.data).hexdigest() for p, f in scenario.after.items()}
    states = {}
    for aid, asset in memory.assets.items():
        expected = memory.versions[asset["current"]]["sha256"]
        path = asset["path"]
        if _denied(scenario, path):
            states[aid] = "unknown"
        elif path in after:
            states[aid] = "intact" if after[path] == expected else "altered"
        elif any(d == expected and inside(p, memory.scope_root) and not _denied(scenario, p) for p, d in after.items()):
            states[aid] = "moved"
        else:
            states[aid] = "missing"
    return states


def truth_sources(scenario, digest: str) -> list[str]:
    """Paths in the named copy locations whose current content has this digest."""
    roots = [scenario.location_root(lid) for lid in scenario.request.get("copy_locations", [])]
    return sorted(p for p, f in scenario.after.items()
                  if any(inside(p, r) for r in roots) and hashlib.sha256(f.data).hexdigest() == digest)
