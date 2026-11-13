"""Recoverability map rules from references/recoverability-map.md, as deterministic code.

copy_eligibility() is the single definition of whether a recorded copy can serve a required version.
It is used by the what-if map and, without a scenario, by recovery source selection. It separates
negative evidence (excluded) from missing evidence (uncertain): only "eligible" counts as redundancy.
"""
from __future__ import annotations

from . import scope

LEVEL_RANK = {"verified-now": 2, "modeled": 1}


class TopologyError(ValueError):
    """The recorded domain graph cannot be used: cycle, missing parent or repeated kind in a chain."""


def ancestors(domain_id: str, domains: dict) -> list[tuple[str, str]]:
    if domain_id not in domains:
        raise TopologyError(f"domain {domain_id} is not recorded")
    chain, seen = [], {domain_id}
    kinds = {domains[domain_id].get("kind")}
    parent = domains[domain_id].get("parent")
    while parent:
        if parent in seen:
            raise TopologyError(f"cycle through {parent}")
        if parent not in domains:
            raise TopologyError(f"parent {parent} of {domain_id} is not recorded")
        kind = domains[parent].get("kind")
        if kind in kinds:
            raise TopologyError(f"kind {kind} repeated in the chain of {domain_id}")
        seen.add(parent)
        kinds.add(kind)
        chain.append((kind, parent))
        parent = domains[parent].get("parent")
    return chain


def membership_closure(location: dict, domains: dict) -> dict[str, str]:
    """Memberships by kind, extended through recorded parents; raises TopologyError on contradictions."""
    closure = dict(location.get("memberships", {}))
    for kind, domain_id in list(closure.items()):
        if domain_id not in domains:
            raise TopologyError(f"membership {domain_id} is not recorded")
        if domains[domain_id].get("kind") != kind:
            raise TopologyError(f"{domain_id} is recorded as {domains[domain_id].get('kind')}, not {kind}")
        for ancestor_kind, ancestor in ancestors(domain_id, domains):
            if closure.setdefault(ancestor_kind, ancestor) != ancestor:
                raise TopologyError(f"{ancestor_kind} is both {closure[ancestor_kind]} and {ancestor}")
    return closure


def domain_effect(location: dict, failed: str, domains: dict) -> str:
    """affected, unaffected or uncertain for the failure of one recorded domain."""
    try:
        closure = membership_closure(location, domains)
        chain = [(domains[failed]["kind"], failed)] + ancestors(failed, domains)
    except (TopologyError, KeyError):
        return "uncertain"
    kind = domains[failed]["kind"]
    if closure.get(kind) == failed:
        return "affected"
    for level_kind, level_domain in chain:
        if level_kind in closure and closure[level_kind] != level_domain:
            return "unaffected"
    return "uncertain"


def copy_effect(copy: dict, scenario: dict, memory) -> str:
    if scenario["type"] == "location":
        failed = memory.locations.get(scenario["location"])
        if failed is None:
            return "uncertain"
        verdict = scope.containment(copy["path"], failed["root"])
        return "affected" if verdict == "inside" else "unaffected" if verdict == "outside" else "uncertain"
    location = memory.locations.get(copy["location"])
    if location is None:
        return "uncertain"
    return domain_effect(location, scenario["domain"], memory.domains)


def copy_eligibility(memory, copy: dict, version_id: str, scenario: dict | None = None,
                     observed: dict[str, bool] | None = None) -> dict:
    """{"state": eligible|uncertain|excluded, "reasons": [...], "level": ...} for one copy and one version.

    excluded: evidence says the copy cannot serve (other version, recorded or re-observed digest
    differs, last observation unreadable, path outside its location, superseded, scenario excludes it).
    uncertain: evidence is missing (unknown digest, access or provenance, needs-review, unknown location
    or membership). A matching version ID alone is never enough.
    """
    observed = observed or {}
    excluded, uncertain = [], []
    version = memory.versions.get(version_id)
    if copy.get("version") != version_id:
        excluded.append("records another version")
    if version is None:
        uncertain.append("required version not recorded")
    elif copy.get("sha256") is None:
        uncertain.append("recorded digest unknown")
    elif copy["sha256"] != version["sha256"]:
        excluded.append("recorded digest differs from the version")
    seen = observed.get(copy.get("id"))
    if seen is False:
        excluded.append("re-observed digest differs")
    status = copy.get("status", "current")
    if status == "superseded":
        excluded.append("record superseded")
    elif status != "current":
        uncertain.append(f"record {status}")
    access = copy.get("access", "unknown")
    if access in ("denied", "unreadable"):
        excluded.append("last observation unreadable")
    elif access != "readable" and seen is not True:
        uncertain.append("access unknown")
    known = getattr(memory, "observations", None)
    if not copy.get("observation") or (known is not None and copy["observation"] not in known):
        if seen is not True:
            uncertain.append("no recorded observation")
    location = memory.locations.get(copy.get("location"))
    if location is None:
        uncertain.append("location not recorded")
    else:
        verdict = scope.containment(copy.get("path"), location["root"])
        if verdict != "inside":
            excluded.append(f"path not inside its location ({verdict})")
    if scenario is not None:
        effect = copy_effect(copy, scenario, memory)
        if effect == "affected":
            excluded.append("excluded by the scenario")
        elif effect == "uncertain":
            uncertain.append("scenario effect unknown")
    state = "excluded" if excluded else "uncertain" if uncertain else "eligible"
    level = None
    if state == "eligible":
        level = "verified-now" if seen else "modeled"
    return {"state": state, "reasons": excluded + uncertain, "level": level,
            "rehearsed": copy.get("id") in memory.rehearsed}


def evaluate_member(memory, version_id: str, scenario: dict, observed: dict[str, bool]) -> dict:
    """observed maps copy id -> digest matched in this session (absent: not re-observed).

    rehearsed lists eligible copies that a verified recovery used in the past: historical evidence on its
    own line, which never raises the level (it does not show the copy is still there or still correct).
    """
    eligible, uncertain, levels, reasons, rehearsed = [], [], [], {}, []
    for copy in memory.copies:
        if copy.get("version") != version_id:
            continue
        result = copy_eligibility(memory, copy, version_id, scenario, observed)
        reasons[copy["id"]] = result["reasons"]
        if result["state"] == "eligible":
            eligible.append(copy["id"])
            levels.append(result["level"])
            if result["rehearsed"]:
                rehearsed.append(copy["id"])
        elif result["state"] == "uncertain":
            uncertain.append(copy["id"])
    best = max(levels, key=LEVEL_RANK.get) if levels else ("insufficient" if uncertain else "none")
    return {"version": version_id, "eligible": len(eligible), "uncertain": len(uncertain),
            "level": best, "copies": eligible, "uncertain_copies": uncertain, "reasons": reasons,
            "rehearsed": rehearsed}


def evaluate_set(memory, set_id: str, scenario: dict, observed: dict[str, bool] | None = None) -> dict:
    observed = observed or {}
    members = {asset: evaluate_member(memory, vid, scenario, observed)
               for asset, vid in memory.sets[set_id]["members"].items()}
    return {"set": set_id, "scenario": scenario["id"], **summarize(members, memory)}


def summarize(members: dict[str, dict], memory) -> dict:
    complete = not getattr(memory, "incomplete_locations", set())
    if all(m["eligible"] > 0 for m in members.values()):
        verdict = "recoverable"
    elif any(m["eligible"] == 0 and m["uncertain"] == 0 for m in members.values()) and complete:
        verdict = "not-recoverable"
    else:
        verdict = "undetermined"
    levels = [m["level"] for m in members.values() if m["level"] in LEVEL_RANK]
    weakest = min(levels, key=LEVEL_RANK.get) if verdict == "recoverable" else None
    return {"verdict": verdict, "level": weakest, "members": members}
