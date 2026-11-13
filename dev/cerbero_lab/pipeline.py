"""Two-session runs: Baseline -> save -> export -> new session that loads only the exported files.

The second session never receives the fixture Memory object. Fixture keys (A-layout, SET-D2, ...) are
recovered only for scoring, through explicit correspondences: asset records by recorded path, sets by
the name the user gave, claims by their statement text. Nothing relies on the shape of generated IDs.
"""
from __future__ import annotations

import copy
import posixpath

from .persistence import load_memory
from .sim import SimFile, SimNAS, inside, norm
from .variants import LIMIT, MAX_DEPTH, VariantA, VariantB, VariantC


def declarations(scenario) -> dict:
    """What the user tells Cerbero during Baseline, derived from the fixture: paths and names, no IDs."""
    raw = scenario.raw
    spec = raw["baseline"]
    blobs, before = scenario.blobs, scenario.before
    sets = {}
    for s in spec.get("sets", {}).values():
        members = {}
        for aid, vid in s["members"].items():
            asset_path = norm(spec["assets"][aid]["path"])
            data = blobs[spec["versions"][vid]["blob"]]
            if asset_path in before and before[asset_path].data == data:
                members[asset_path] = asset_path
            else:
                members[asset_path] = next((p for p in sorted(before) if before[p].data == data), None)
        sets[s["name"]] = members
    names = {key: s["name"] for key, s in spec.get("sets", {}).items()}
    return {
        "scope": raw["request"]["scope"],
        "locations": {lid: {"root": loc["root"], "memberships": dict(loc.get("memberships", {})),
                            "unknown_kinds": list(loc.get("unknown_kinds", []))} for lid, loc in raw["locations"].items()},
        "domains": copy.deepcopy(raw.get("domains", {})),
        "statements": list(raw.get("statements", {}).values()),
        "critical": sorted(norm(a["path"]) for a in spec["assets"].values() if a["importance"] == "critical"),
        "sets": sets,
        "claims": [{"key": c["id"], "statement": c["statement"], "set": names.get(c.get("set")),
                    "depends_on": list(c.get("depends_on", []))} for c in spec.get("claims", [])],
    }


def baseline_session(scenario) -> tuple[dict[str, bytes], dict, object]:
    """Session 1 on the pre-incident tree. Returns the memory files (name -> bytes), NAS stats, report."""
    if not scenario.raw.get("baseline"):
        return {}, {}, None
    root = norm(scenario.request.get("memory_root", "cerbero-memory"))
    nas = SimNAS({p: SimFile(f.data, f.mtime) for p, f in scenario.before.items()})
    nas.dirs.add(root)
    report = VariantC(scenario, nas, None, intent="baseline", declarations=declarations(scenario)).run()
    files = {posixpath.basename(p): nas.content(p) for p in sorted(nas.files) if inside(p, root)}
    return files, nas.stats(), report


def with_memory(scenario, files: dict[str, bytes], nas=None):
    """The post-incident NAS with the exported memory files placed back in the memory folder."""
    nas = nas or scenario.build_nas()
    root = norm(scenario.request.get("memory_root", "cerbero-memory"))
    for n, (name, data) in enumerate(sorted(files.items()), start=1):
        nas.files[f"{root}/{name}"] = SimFile(data, 3000 + n)
    nas.dirs.add(root)
    return nas


def correspondence(scenario, memory) -> dict[str, str]:
    """Generated asset ID -> fixture asset key, by recorded path."""
    if memory is None or scenario.memory is None:
        return {}
    by_path = {a["path"]: key for key, a in scenario.memory.assets.items()}
    return {aid: by_path[a["path"]] for aid, a in memory.assets.items() if a["path"] in by_path}


def translate(report, scenario, memory) -> None:
    """Rename generated IDs in a report to fixture keys, for scoring only."""
    key = correspondence(scenario, memory)
    report.mapping = key
    k = lambda x: key.get(x, x)  # noqa: E731
    spec = scenario.raw.get("baseline") or {}
    set_key = {sid: fk for fk, s in spec.get("sets", {}).items() for sid, r in (memory.sets.items() if memory else [])
               if r.get("name") == s.get("name")}
    claim_key = {c["id"]: fc["id"] for c in (memory.claims if memory else []) for fc in spec.get("claims", [])
                 if c["statement"] == fc["statement"]}
    report.states = {k(a): s for a, s in report.states.items()}
    report.located_at = {k(a): p for a, p in report.located_at.items()}
    report.no_source = [k(a) for a in report.no_source]
    report.at_risk = [k(a) for a in report.at_risk]
    report.out_of_scope = [k(a) for a in report.out_of_scope]
    report.alternatives = [set_key.get(s, s) for s in report.alternatives]
    report.revalidated = [claim_key.get(c, c) for c in report.revalidated]
    report.policy_effects = {f"{k(e.split(':', 1)[0])}:{e.split(':', 1)[1]}" for e in report.policy_effects}
    for row in report.outside_target:
        row["asset"] = k(row["asset"])
    for attempt in report.attempts:
        attempt["entries"] = {k(a): e for a, e in attempt["entries"].items()}
        attempt["outside"] = [k(a) for a in attempt.get("outside", [])]
        if attempt.get("set"):
            attempt["set"] = set_key.get(attempt["set"], attempt["set"])
    for row in report.whatif:
        row["members"] = {k(a): m for a, m in row["members"].items()}


def run(key: str, scenario, policies=()):
    """One variant on isolated state. A works without memory; B and C load memory from saved bundles."""
    if key == "A":
        nas = scenario.build_nas()
        return VariantA(scenario, nas, copy.deepcopy(scenario.memory)).run(), nas
    files, _, _ = baseline_session(scenario)
    nas = with_memory(scenario, files)
    root = norm(scenario.request.get("memory_root", "cerbero-memory"))
    scope_root = scenario.location_root(scenario.request["scope"]) if "scope" in scenario.request else ""
    if key == "B":
        memory, _ = load_memory(nas, root, scope_root, verify=False)
        variant = VariantB(scenario, nas, memory) if memory else VariantA(scenario, nas, copy.deepcopy(scenario.memory))
        variant.report.variant = VariantB.name
    elif key in ("C", "C-no-selector", "C-no-policies"):
        memory, session = load_memory(nas, root, scope_root, verify=True)
        variant = VariantC(scenario, nas, memory, policies=() if key == "C-no-policies" else policies,
                           selector=key != "C-no-selector", session=session)
        if key == "C-no-policies":
            variant.report.variant = "C-no-policies"
    else:
        raise KeyError(key)
    report = variant.run()
    if key != "A":
        translate(report, scenario, memory)
    return report, nas


def measure_baseline(scenario, key: str) -> dict:
    """Cost of creating the reference memory on the pre-incident state.

    C: the real Baseline session of VariantC. B: modeled as one full listing and digest of every file in
    the project and copy locations, plus one save of the resulting bundle.
    """
    if key == "C":
        return baseline_session(scenario)[1]
    nas = SimNAS({p: SimFile(f.data, f.mtime) for p, f in scenario.before.items()})
    nas.dirs.add("cerbero-memory")
    roots = [scenario.location_root(lid) for lid in scenario.raw["locations"]]
    for root in roots:
        for entry in nas.find(root, limit=LIMIT, max_depth=MAX_DEPTH)["data"]["entries"]:
            nas.sha256(entry["path"])
    nas.save_text("cerbero-memory", "B-baseline", "modeled bundle")
    return nas.stats()
