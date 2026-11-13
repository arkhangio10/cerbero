"""Load Cerbero memory only from the bundles saved in the memory folder, as Step 3 of SKILL.md describes.

The loader resolves the memory folder (D2), lists it (D3) and keeps only files whose real path lies inside it
before any read or digest. It reads each such CERBERO- file (D4), parses and validates it, checks it against
the newest index snapshot (D7), resolves supersedes chains and builds the Memory used by a new session.
Files that are unlisted, listed without a digest, changed since indexing, unparseable, read only in part or
whose real path is outside the folder or unreported are needs-review: their IDs still count for numbering,
their records are not evidence. From the trusted records it also rebuilds the recovery evidence (which copy
served which verified receipt entry) and the policies that are allowed to change a review.

Checking a real path before reading does not make the two operations atomic: a link changed between the
check and the read is detected only by the real path the read itself reports (checked again here).
"""
from __future__ import annotations

import posixpath
import re
from dataclasses import dataclass, field

from . import records as rec
from . import scope
from .fixtures import Memory

LIMIT = 200
LISTING_BUDGET = 60
KNOWN_PREFIXES = ("CERBERO-IDX-", "CERBERO-B-", "CERBERO-TD-", "CERBERO-TH-")
_NUMBERED = re.compile(r"\b[A-Z]{1,4}-(\d{4})(?![0-9])")
_INDEX_ID = re.compile(r"^IDX-(\d{4})-(\d{2})$")
VERIFIED = ("verified", "already-present-verified")
REQUIRED_KINDS = {"origin", "similar", "counterexample", "insufficient"}
# Policy effects as written in policy records ("<kind> <argument>"): the lab adapter implements two of the
# allowed kinds; the others are allowed by the Skill but never applied here; forbidden kinds fail the guard.
LAB_EFFECTS = {"promote-critical": "promote_critical", "informational": "informational"}
SKILL_ONLY_EFFECTS = {"add-search-location", "add-check", "add-recoverability-check", "report-order"}
FORBIDDEN_EFFECTS = {"add-capability": "I1", "expand-scope": "I2", "auto-approve": "I3", "merge-approvals": "I3",
                     "allow-overwrite": "I4", "allow-move": "I4", "allow-delete": "I4", "skip-source-check": "I5",
                     "skip-destination-check": "I5", "lower-critical": "I6", "label-cause": "I7",
                     "trust-document-instructions": "I7", "hide-coverage": "I8", "hide-pending": "I8"}


@dataclass
class Session:
    next_case: int = 1
    files: dict[str, dict] = field(default_factory=dict)   # path -> bundle_id, sha256, status, reason
    problems: list[str] = field(default_factory=list)
    unfinished_plans: list[str] = field(default_factory=list)
    index_file: str | None = None
    records: dict[str, dict] = field(default_factory=dict)  # active, trusted records
    history: dict[str, dict] = field(default_factory=dict)  # trusted records, superseded ones included
    record_files: dict[str, str] = field(default_factory=dict)  # record id -> file
    listings: int = 0
    inventory_complete: bool = True
    policies: list[dict] = field(default_factory=list)      # executable, with their evidence
    policy_decisions: dict[str, str] = field(default_factory=dict)  # policy record id -> why (not) applied


@dataclass
class Listing:
    seen: list[str] = field(default_factory=list)            # every CERBERO- path listed, read or not
    usable: dict[str, str] = field(default_factory=dict)     # listed path -> real path proven inside the root
    rejected: dict[str, str] = field(default_factory=dict)   # listed path -> why it is not read
    problems: list[str] = field(default_factory=list)
    complete: bool = False
    index_complete: bool = False
    listings: int = 0


def next_case_number(texts) -> int:
    highest = 0
    for text in texts:
        for match in _NUMBERED.finditer(text):
            highest = max(highest, int(match.group(1)))
    return highest + 1


def _partition(nas, root: str, pattern: str, out: Listing, entries: dict, budget: int) -> bool:
    """List names containing pattern; split a truncated listing by the next digit. True when complete."""
    if out.listings >= budget:
        out.problems.append(f"listing budget reached before {pattern} was listed")
        return False
    out.listings += 1
    result = nas.ls(root, limit=LIMIT, name_contains=pattern)
    if not result["ok"]:
        out.problems.append(f"memory listing for {pattern} failed: {result['error']['code']}")
        return False
    for entry in result["data"]["entries"]:
        if entry["type"] == "file":
            entries[entry["path"]] = entry
    if not result["data"]["truncated"] and len(result["data"]["entries"]) < LIMIT:
        return True
    return all([_partition(nas, root, pattern + digit, out, entries, budget) for digit in "0123456789"])


def list_memory(nas, root: str, budget: int | None = None) -> Listing:
    """D2 on the memory folder, then D3 (partitioned by name when truncated), then a real path for every file."""
    budget = LISTING_BUDGET if budget is None else budget
    out = Listing()
    folder = nas.stat(root)
    if not folder["ok"]:
        out.problems.append(f"memory folder not readable: {folder['error']['code']}")
        return out
    real = folder["data"].get("realpath")
    if real is None:
        out.problems.append("memory folder real path not reported: containment of memory files cannot be shown; nothing read")
        return out
    if real != root:
        out.problems.append(f"memory folder resolves to {real}, not to the authorized real path {root}; nothing read")
        return out
    entries: dict[str, dict] = {}
    out.listings = 1
    full = nas.ls(root, limit=LIMIT, name_contains="CERBERO-")
    if not full["ok"]:
        out.problems.append(f"memory folder not readable: {full['error']['code']}")
        return out
    for entry in full["data"]["entries"]:
        if entry["type"] == "file":
            entries[entry["path"]] = entry
    if not full["data"]["truncated"] and len(full["data"]["entries"]) < LIMIT:
        out.complete = out.index_complete = True
    else:
        out.problems.append("memory listing truncated: listed again by bundle prefix; names with other prefixes may exist unseen")
        done = {p: _partition(nas, root, p, out, entries, budget) for p in KNOWN_PREFIXES}
        out.index_complete = done["CERBERO-IDX-"]
        if not all(done.values()):
            out.problems.append("memory inventory incomplete: " + ", ".join(p for p, ok in done.items() if not ok))
    for path in sorted(entries):
        if "CERBERO-" not in posixpath.basename(path):
            continue
        out.seen.append(path)
        real = entries[path].get("realpath")
        if real is None:
            seen = nas.stat(path)
            real = seen["data"].get("realpath") if seen["ok"] else None
        if scope.containment(path, root) != "inside":
            out.rejected[path] = "listed path outside the memory folder: not read"
        elif real is None:
            out.rejected[path] = "real path not reported: not read"
        elif scope.containment(real, root) != "inside":
            out.rejected[path] = f"real path {real} is outside the memory folder ({scope.containment(real, root)}): not read"
        else:
            out.usable[path] = real
    return out


def scan_session(nas, root: str, memory=None) -> Session:
    """Numbering only (used when a Memory object is injected): D3 and the IDs it already holds."""
    listing = list_memory(nas, root)
    known = list(getattr(memory, "assets", {})) + list(getattr(memory, "statements", {}))
    session = Session(next_case=next_case_number(listing.seen + known), problems=list(listing.problems),
                      listings=listing.listings, inventory_complete=listing.complete)
    session.files = {p: {"bundle_id": None, "sha256": None, "status": "needs-review", "reason": "not loaded"}
                     for p in listing.seen}
    return session


def _index_order(bundle_id: str):
    match = _INDEX_ID.match(bundle_id or "")
    return (int(match.group(1)), int(match.group(2))) if match else None


def _digest(nas, path: str, real: str) -> str | None:
    """D7 on a file whose real path was proven inside the folder; the real path D7 reports must be the same."""
    seen = nas.sha256(path)
    if not seen["ok"] or seen["data"].get("realpath") != real:
        return None
    return seen["data"]["sha256"]


def load_memory(nas, root: str, scope_root: str, verify: bool = True, confirmed: tuple[str, ...] = (),
                read_holdout: bool = True) -> tuple[Memory | None, Session]:
    """confirmed: file names the user confirmed in this session (for example authorized test-case files).
    read_holdout=False (Mode Learn before a freeze): holdout files are hashed for the index, never read."""
    listing = list_memory(nas, root)
    session = Session(problems=list(listing.problems), listings=listing.listings, inventory_complete=listing.complete)
    for path, reason in listing.rejected.items():
        session.files[path] = {"bundle_id": None, "sha256": None, "status": "needs-review", "reason": reason}
    parsed: dict[str, dict] = {}
    unread_holdout: dict[str, str] = {}
    for path, real in listing.usable.items():
        if not read_holdout and "CERBERO-TH-" in posixpath.basename(path):
            unread_holdout[path] = real
            continue
        read = nas.cat(path)
        if not read["ok"]:
            reason = f"unreadable: {read['error']['code']}"
        elif read["data"].get("realpath") != real:
            reason = f"resolved to {read['data'].get('realpath')} when read; content discarded"
        elif read["data"].get("partial"):
            reason = f"returned only in part ({read['data'].get('bytes_returned')} bytes)"
        else:
            try:
                parsed[path] = rec.parse(read["data"]["text"])
                continue
            except ValueError as exc:
                reason = f"unparseable: {exc}"
        session.files[path] = {"bundle_id": None, "sha256": None, "status": "needs-review", "reason": reason}
    all_ids = [rid for b in parsed.values() for rid in b["records"]] + \
              [b["header"]["bundle_id"] for b in parsed.values()]
    session.next_case = next_case_number(listing.seen + all_ids)

    indexes = {p: b for p, b in parsed.items()
               if b["records"] and all(r.get("type") == "index-entry" for r in b["records"].values())
               and _index_order(b["header"]["bundle_id"])}
    newest = max(indexes, key=lambda p: _index_order(indexes[p]["header"]["bundle_id"]), default=None)
    unproven_index = bool(newest) and not listing.index_complete
    if unproven_index:
        session.problems.append("index snapshots not completely listed: none can be taken as the newest")
        newest = None
    session.index_file = newest
    listed = {}
    parts: set[str] = set()
    if newest:
        session_number = _index_order(indexes[newest]["header"]["bundle_id"])[0]
        for r in indexes[newest]["records"].values():
            if scope.containment(r.get("file"), root) == "inside":
                listed[r["file"]] = r
            else:
                session.problems.append(f"newest index lists a path outside the memory folder: {r.get('file')}")
        # An index snapshot saved in parts: each part lists the previous part of the same session with its
        # digest. Follow that chain from the newest part; a part is merged only when its digest matches.
        chain = [newest]
        while chain:
            rows = indexes[chain.pop()]["records"].values()
            for r in rows:
                path = r.get("file")
                if path in indexes and path not in parts and path != newest \
                        and _index_order(indexes[path]["header"]["bundle_id"])[0] == session_number:
                    if r.get("status") == "current" and r.get("sha256") and \
                            (not verify or _digest(nas, path, listing.usable[path]) == r["sha256"]):
                        parts.add(path)
                        chain.append(path)
                        for row in indexes[path]["records"].values():
                            if scope.containment(row.get("file"), root) == "inside":
                                listed.setdefault(row["file"], row)
        for path, bundle in indexes.items():
            if path != newest and path not in parts and _index_order(bundle["header"]["bundle_id"])[0] == session_number:
                session.problems.append(f"{posixpath.basename(path)}: part of the newest index not bound to it by digest")
        digest = _digest(nas, newest, listing.usable[newest]) if verify else None
        session.files[newest] = {"bundle_id": indexes[newest]["header"]["bundle_id"], "sha256": digest,
                                 "status": "superseded", "reason": "index snapshot"}
        for path in parts:
            session.files[path] = {"bundle_id": indexes[path]["header"]["bundle_id"], "sha256": listed[path]["sha256"],
                                   "status": "superseded", "reason": "part of the newest index snapshot"}
    elif parsed and not unproven_index:
        session.problems.append("no index snapshot: every memory file needs review")

    for path, real in unread_holdout.items():
        entry = listed.get(path) or {}
        digest = _digest(nas, path, real) if verify else entry.get("sha256")
        ok = digest is not None and digest == entry.get("sha256")
        session.files[path] = {"bundle_id": entry.get("bundle_id"), "sha256": digest if ok else None,
                               "status": "current" if ok else "needs-review",
                               "reason": "holdout file: hashed, not read before the freeze"}
    trusted: dict[str, dict] = {}
    for path, bundle in parsed.items():
        if path == newest or path in parts:
            continue
        bundle_id = bundle["header"]["bundle_id"]
        entry = listed.get(path)
        status, reason, digest = "current", "listed and verified", entry.get("sha256") if entry else None
        if path in indexes:
            status, reason = "superseded", "older index snapshot"
        elif posixpath.basename(path) in confirmed:
            digest = _digest(nas, path, listing.usable[path]) if verify else None
            status, reason = ("current", "confirmed by the user in this session") if digest or not verify \
                else ("needs-review", "confirmed by the user but not hashed")
        elif entry is None:
            status, reason = "needs-review", "not listed in the newest index"
        elif entry.get("sha256") is None or entry.get("status") != "current":
            status, reason = "needs-review", f"listed as {entry.get('status')} without a usable digest"
        elif verify and (seen := _digest(nas, path, listing.usable[path])) != entry["sha256"]:
            status, reason = "needs-review", "digest differs from the index" if seen else \
                "not hashed, or its real path changed when hashed"
        session.files[path] = {"bundle_id": bundle_id, "sha256": digest if status != "needs-review" else None,
                               "status": status, "reason": reason}
        if status == "current":
            trusted[path] = bundle

    records: dict[str, dict] = {}
    conflicting: set[str] = set()
    for path, bundle in trusted.items():
        for record_id, fields in bundle["records"].items():
            if record_id in records:
                if records[record_id] != fields:  # an identical copy is a save repeated after a failure
                    conflicting.add(record_id)
                    session.problems.append(f"record {record_id} differs between {session.record_files[record_id]} "
                                            f"and {path}: neither copy is used")
                continue
            records[record_id] = fields
            session.record_files[record_id] = path
    for record_id in conflicting:
        records.pop(record_id)
        session.record_files.pop(record_id)
    invalid = rec.validate(records)
    session.problems += invalid
    for problem in invalid:
        records.pop(problem.split(":", 1)[0], None)
    while True:
        dangling = rec.check_references(records)
        if not dangling:
            break
        session.problems += dangling
        for problem in dangling:
            records.pop(problem.split(":", 1)[0], None)
    session.history = dict(records)
    active = _resolve_supersedes(records, session)
    session.records = active

    plans = {rid for rid, r in active.items() if r["type"] == "plan"}
    receipted = {r["plan_id"] for r in active.values() if r["type"] == "receipt"}
    session.unfinished_plans = sorted(plans - receipted)
    session.policies, session.policy_decisions = active_policies(session)
    memory = build_memory(active, scope_root)
    if memory is not None:
        memory.rehearsals = rehearsals(records, active)
        memory.rehearsed = {r["copy"] for r in memory.rehearsals}
    return memory, session


def _resolve_supersedes(records: dict[str, dict], session: Session) -> dict[str, dict]:
    superseded = {}
    for record_id, fields in records.items():
        target = fields.get("supersedes")
        if target is None:
            continue
        if target in records and records[target]["type"] != fields["type"]:
            session.problems.append(f"{record_id}: supersedes a record of another type ({target})")
            continue
        superseded[target] = record_id
    active = {rid: f for rid, f in records.items() if rid not in superseded}
    for target in superseded:
        head, seen = target, set()
        while head in superseded:
            if head in seen:
                session.problems.append(f"supersedes cycle through {target}")
                break
            seen.add(head)
            head = superseded[head]
    return active


def rehearsals(records: dict[str, dict], active: dict[str, dict]) -> list[dict]:
    """Recovery evidence rebuilt from trusted records: a copy served a verified entry of an approved plan.

    Every link is checked: receipt -> plan and its confirmed digest, approval granted for that digest,
    receipt entry -> plan entry -> version, source digest before the copy and destination digest equal to the
    version. The result is historical: it says the copy held the version when the recovery ran, not now.
    """
    found = []
    for rid, entry in sorted(records.items()):
        if entry["type"] != "receipt-entry" or entry["status"] != "verified":
            continue
        receipt = records.get(entry["receipt_id"]) or {}
        plan_entry = records.get(entry.get("entry_id")) or {}
        plan_id = receipt.get("plan_id")
        if receipt.get("reference") != "approved-version" or plan_entry.get("plan_id") != plan_id:
            continue
        approvals = [a for a in records.values() if a["type"] == "approval" and a["plan_id"] == plan_id
                     and a["decision"] == "granted" and a["plan_sha256"] and a["plan_sha256"] == receipt.get("plan_sha256")]
        version = records.get(plan_entry.get("version_id")) or {}
        digest = version.get("sha256")
        if not approvals or not digest or not (digest == plan_entry["expected_sha256"] == entry["destination_sha256"]
                                               == entry["source_sha256_before"]):
            continue
        for cid, copy in sorted(active.items()):
            if copy["type"] == "copy" and copy["real_path"] == plan_entry["source_path"] \
                    and copy["version_id"] == plan_entry["version_id"] and copy.get("sha256") == digest:
                found.append({"copy": cid, "version": plan_entry["version_id"], "receipt": entry["receipt_id"],
                              "receipt_entry": rid, "plan": plan_id, "plan_sha256": receipt["plan_sha256"],
                              "source": plan_entry["source_path"], "destination": entry["destination_path"],
                              "observed_at": "unknown: the NAS returned no time", "copy_status": copy["status"]})
    return found


def parse_effects(effects: list[str]) -> tuple[dict, list[str], list[str]]:
    """Policy effect lines -> (lab effect dict, guard violations, effects the lab adapter does not implement)."""
    executable, violations, unsupported = {}, [], []
    for line in effects:
        kind, _, argument = line.strip().partition(" ")
        if kind in FORBIDDEN_EFFECTS:
            violations.append(f"{FORBIDDEN_EFFECTS[kind]} forbidden effect {kind}")
        elif kind in LAB_EFFECTS:
            folder = argument.strip().rstrip("/")
            if folder != "." and scope.child("project", folder)[0] is None:
                violations.append(f"I2 effect {kind} needs a canonical folder inside the project, got {argument!r}")
            else:
                executable.setdefault(LAB_EFFECTS[kind], []).append(folder)
        elif kind in SKILL_ONLY_EFFECTS:
            unsupported.append(kind)
        else:
            violations.append(f"I1 unknown effect {kind}")
    return executable, violations, unsupported


def _evaluation_ok(evaluation: dict, history: dict) -> str | None:
    kinds, holdout = set(), False
    for item in evaluation["cases"]:
        parts = item.split()
        if len(parts) != 4 or parts[3] != "pass":
            return f"case {item!r} did not pass"
        case = history.get(parts[0])
        if not case or case["type"] != "test-case" or (case["split"], case["kind"]) != (parts[1], parts[2]):
            return f"case {parts[0]} is not a trusted test-case record with that split and kind"
        kinds.add(case["kind"])
        holdout |= case["split"] == "holdout"
    if not REQUIRED_KINDS <= kinds or not holdout:
        return "evaluation lacks one of the four case kinds or a holdout case"
    return None


def active_policies(session: Session) -> tuple[list[dict], dict[str, str]]:
    """Policies that may change a review: only an active record whose whole chain is persisted and verified."""
    history, decisions, executable = session.history, {}, []
    for pid, policy in sorted(session.records.items()):
        if policy["type"] != "policy":
            continue
        if policy["status"] != "active":
            decisions[pid] = f"not applied: status {policy['status']}"
            continue
        frozen_id, frozen, seen = pid, policy, set()
        while frozen.get("status") != "candidate" and frozen.get("supersedes") and frozen["supersedes"] not in seen:
            seen.add(frozen["supersedes"])
            frozen_id = frozen["supersedes"]
            frozen = history.get(frozen_id, {})
        same_rule = all(frozen.get(k) == policy[k] for k in ("version", "condition", "scope", "effect"))
        frozen_file = session.record_files.get(frozen_id)
        file_digest = session.files.get(frozen_file, {}).get("sha256") if frozen_file else None
        evaluations = [e for e in history.values() if e["type"] == "evaluation" and e["policy_id"] == frozen_id
                       and e["verdict"] == "evaluated" and e["rule_sha256"] == policy["rule_sha256"]]
        problem = None
        if frozen.get("status") != "candidate" or not same_rule:
            problem = "no frozen candidate with the same rule"
        elif not policy.get("approval"):
            problem = "no recorded user approval"
        elif not policy.get("rule_sha256") or file_digest != policy["rule_sha256"]:
            problem = "frozen candidate file digest differs from rule_sha256, or the file is not trusted"
        elif not evaluations:
            problem = "no passing evaluation of the frozen rule"
        else:
            problem = _evaluation_ok(evaluations[0], history)
        effect, violations, unsupported = parse_effects(policy["effect"])
        if problem is None and violations:
            problem = "guard: " + "; ".join(violations)
        if problem is None and unsupported:
            problem = "effect not implemented by the lab adapter: " + ", ".join(unsupported)
        if problem:
            decisions[pid] = f"not applied: {problem}"
            continue
        decisions[pid] = "applied"
        executable.append({"id": pid, "version": policy["version"], "effect": effect,
                           "evidence": {"file": session.record_files[pid], "frozen": frozen_id,
                                        "rule_sha256": policy["rule_sha256"], "approval": policy["approval"],
                                        "evaluation": next(k for k, e in history.items() if e is evaluations[0])}})
    return executable, decisions


def build_memory(records: dict[str, dict], scope_root: str) -> Memory | None:
    by_type: dict[str, dict[str, dict]] = {}
    for record_id, fields in records.items():
        by_type.setdefault(fields["type"], {})[record_id] = fields
    scopes = [sid for sid, s in by_type.get("scope", {}).items() if s["real_root"] == scope_root]
    if len(scopes) != 1:
        return None
    scope_id = scopes[0]
    scope_record = by_type["scope"][scope_id]
    memory = Memory(scope_root=scope_record["real_root"], baseline_time=scope_record.get("newest_mtime") or 0,
                    scope_id=scope_id)
    for aid, a in by_type.get("asset", {}).items():
        if a["scope_id"] != scope_id:
            continue
        rel, _ = scope.relative_inside(a["recorded_path"], memory.scope_root)
        memory.assets[aid] = {"path": a["recorded_path"], "importance": a["importance"], "current": a["current_version"],
                              "mtime": a.get("recorded_mtime"), "size": a["recorded_size"], "name": a["name"], "rel": rel}
    for vid, v in by_type.get("version", {}).items():
        memory.versions[vid] = {"asset": v["asset_id"], "sha256": v["sha256"], "size": v["size_bytes"],
                                "approved_by": v.get("approved_by")}
    for sid, s in by_type.get("approved-set", {}).items():
        memory.sets[sid] = {"name": s["name"], "members": dict(s["members"]), "status": s["status"],
                            "approved_by": s["approved_by"]}
    for lid, loc in by_type.get("location", {}).items():
        memory.locations[lid] = {"root": loc["real_root"], "memberships": dict(loc["memberships"]),
                                 "unknown_kinds": list(loc["unknown_kinds"])}
        if loc["inventory"] != "complete":
            memory.incomplete_locations.add(lid)
    for did, d in by_type.get("domain", {}).items():
        memory.domains[did] = {"kind": d["kind"], "label": d["label"], "parent": d.get("parent")}
    memory.statements = {sid: s["text"] for sid, s in by_type.get("statement", {}).items()}
    memory.observations = set(by_type.get("observation", {}))
    for cid, c in sorted(by_type.get("copy", {}).items()):
        memory.copies.append({"id": cid, "version": c["version_id"], "path": c["real_path"], "location": c["location_id"],
                              "sha256": c.get("sha256"), "observation": c.get("observation"), "access": c["access"],
                              "status": c["status"]})
    for cid, c in sorted(by_type.get("claim", {}).items()):
        if c["kind"] == "asset-state":
            continue
        memory.claims.append({"id": cid, "kind": c["kind"], "subject": c["subject"], "statement": c["statement"],
                              "class": c["class"], "supports": list(c["supports"]), "contradicts": list(c["contradicts"]),
                              "depends_on": list(c["depends_on"]), "status": c["status"]})
    return memory
