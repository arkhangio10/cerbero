"""Deterministic reference procedures for the three compared variants.

A  simple flow without persisted memory: names, sizes and times, newest copy, copy-fidelity check.
B  reference memory with hashes and approved sets, same essential verifications, no failure
   domains, no check selection, no coverage ledger, no provenance, no policies.
C  the decision rules written in the Skill references (map, investigation, recovery, policies),
   including Baseline, so that a later session can load memory only from the saved bundles.

These procedures measure the value of the written decision rules on synthetic fixtures under
the simulated experts in sim.py. They are not the Skill running on UGOS and say nothing about
how faithfully the UGOS model follows the Skill text (see dev/agent_eval for that).
"""
from __future__ import annotations

import json
import posixpath
import re
import time
from collections import Counter
from dataclasses import dataclass, field

from . import scope
from .mapping import copy_eligibility, evaluate_member, evaluate_set
from .persistence import scan_session
from .records import Bundle, parse, validate
from .sim import inside, norm

LIMIT = 200
MAX_DEPTH = 8
# Session budgets of SKILL.md rule 11 (defaults the user may raise; design choices, not UGOS limits).
DIGEST_BUDGET = 300
LISTING_BUDGET = 60
BYTE_BUDGET = 2 * 1024 ** 3
# Investigation and Baseline stop before eating the reserve, so that the essential checks of a recovery fit.
DIGEST_RESERVE = 40
BYTE_RESERVE = 512 * 1024 ** 2
# Largest bundle sent in one save (D10). A design budget below the 31.9 KB that failed in the local harness;
# the real limit of save-text on UGOS is unknown until measured on the device.
MAX_BUNDLE_BYTES = 16 * 1024
PARTITION_BUDGET = 20
DOC_SUFFIXES = (".txt", ".md", ".pdf", ".docx")
DOC_QUESTION = "Does this file state that project files were intentionally renamed, replaced or deleted, and by whom?"
INSTRUCTION_RE = re.compile(r"\b(delete|remove|erase|wipe|disable|approve|overwrite|execute|upload|share|turn off|policy)\b", re.I)
CHANGED = ("missing", "altered")
VERIFIED = ("verified", "already-present-verified")
SUCCESS = VERIFIED + ("fidelity-only",)
PENDING = ("no-source", "out-of-scope", "state-unknown")
ALLOWED_EFFECTS = {"promote_critical", "informational", "add_search_location", "add_check",
                   "add_recoverability_check", "report_order"}
FORBIDDEN_EFFECTS = {
    "add_capability": "I1 adds a capability, expert or Action",
    "expand_scope": "I2 widens the authorized scope",
    "auto_approve": "I3 removes or pre-answers a confirmation or approval",
    "merge_approvals": "I3 removes or pre-answers a confirmation or approval",
    "allow_overwrite": "I4 allows overwriting, moving or deleting",
    "allow_move": "I4 allows overwriting, moving or deleting",
    "skip_source_check": "I5 drops the source check before copying",
    "skip_destination_check": "I5 drops the destination check after copying",
    "label_cause": "I7 labels a cause without a cited source",
    "trust_document_instructions": "I7 treats content as authority",
    "hide_coverage": "I8 hides coverage, pending items, unknowns or findings",
    "hide_pending": "I8 hides coverage, pending items, unknowns or findings",
}


@dataclass
class Report:
    variant: str
    scenario: str
    states: dict[str, str] = field(default_factory=dict)
    located_at: dict[str, str] = field(default_factory=dict)
    whatif: list[dict] = field(default_factory=list)
    at_risk: list[str] = field(default_factory=list)
    attempts: list[dict] = field(default_factory=list)
    no_source: list[str] = field(default_factory=list)
    alternatives: list[str] = field(default_factory=list)
    findings: list[dict] = field(default_factory=list)
    contradictions: list[str] = field(default_factory=list)
    revalidated: list[str] = field(default_factory=list)
    open_items: list[str] = field(default_factory=list)
    acknowledged: list[str] = field(default_factory=list)
    causes: list[str] = field(default_factory=list)
    out_of_scope: list[str] = field(default_factory=list)
    coverage: dict = field(default_factory=lambda: {"unreadable": set(), "truncated": set(),
                                                    "metadata_only": 0, "budget_exhausted": False})
    cards: int = 0
    policy_effects: set[str] = field(default_factory=set)
    rejected_policies: list[str] = field(default_factory=list)
    policy_decisions: dict[str, str] = field(default_factory=dict)
    policy_evidence: dict[str, dict] = field(default_factory=dict)
    outside_target: list[dict] = field(default_factory=list)
    learning: dict = field(default_factory=dict)
    rehearsals: list[dict] = field(default_factory=list)
    persisted: list[str] = field(default_factory=list)
    mapping: dict[str, str] = field(default_factory=dict)
    stats: dict = field(default_factory=dict)
    runtime_ms: float = 0.0

    @property
    def final(self) -> dict | None:
        return self.attempts[-1] if self.attempts else None


def overall_status(statuses: list[str], success: str) -> str:
    if statuses and all(s == success for s in statuses):
        return "verified"
    if success in statuses:
        return "partial"
    if statuses and all(s == "cancelled" for s in statuses):
        return "cancelled"
    return "failed"


def rel_inside(rel: str | None, prefix: str) -> bool:
    if rel is None:
        return False
    prefix = prefix.strip("/")
    return prefix in ("", ".") or rel == prefix or rel.startswith(prefix + "/")


def summary(value) -> str:
    return value if isinstance(value, str) else json.dumps(value, sort_keys=True, ensure_ascii=False)


class Variant:
    name = "?"

    def __init__(self, scenario, nas, memory=None, intent: str | None = None):
        self.sc = scenario
        self.nas = nas
        self.mem = memory
        self.req = scenario.request
        self.intent = intent or self.req["intent"]
        self.answers = scenario.raw.get("answers", {})
        self.report = Report(variant=self.name, scenario=scenario.id)
        self.scope_root = scenario.location_root(self.req["scope"]) if "scope" in self.req else None
        self.parent = norm(self.req.get("recovery_parent", "recovered"))
        self.memory_root = norm(self.req.get("memory_root", "cerbero-memory"))
        self.copy_roots = {self.loc_of(lid) or lid: scenario.location_root(lid) for lid in self.req.get("copy_locations", [])}

    # correspondence between what the user names now and the records in memory -----------------
    def loc_of(self, lid: str) -> str | None:
        """Memory location whose recorded real root equals the real root of the folder named now."""
        if self.mem is None or lid not in self.sc.raw.get("locations", {}):
            return None
        root = self.sc.location_root(lid)
        found = [m for m, loc in self.mem.locations.items() if loc["root"] == root]
        return found[0] if len(found) == 1 else None

    def set_of(self, key: str) -> str | None:
        """Memory approved set with the name the user uses for it."""
        if self.mem is None:
            return None
        if key in self.mem.sets:
            return key
        name = ((self.sc.raw.get("baseline") or {}).get("sets", {}).get(key) or {}).get("name")
        found = [s for s, r in self.mem.sets.items() if name and r.get("name") == name and r.get("status", "current") == "current"]
        return found[0] if len(found) == 1 else None

    def domain_of(self, key: str) -> str | None:
        if self.mem is None:
            return None
        if key in self.mem.domains:
            return key
        declared = self.sc.raw.get("domains", {}).get(key)
        if not declared:
            return None
        found = [d for d, r in self.mem.domains.items()
                 if r.get("kind") == declared["kind"] and r.get("label") == declared.get("label")]
        return found[0] if len(found) == 1 else None

    def scenario_in_memory(self, scenario: dict) -> dict:
        if scenario["type"] == "location":
            return {**scenario, "location": self.loc_of(scenario["location"]) or scenario["location"]}
        return {**scenario, "domain": self.domain_of(scenario["domain"]) or scenario["domain"]}

    def run(self) -> Report:
        start = time.perf_counter()
        intent = self.intent
        if intent == "baseline":
            self.baseline()
        if intent in ("investigate", "investigate-recover", "review"):
            self.investigate()
        if intent == "review":
            self.review_map()
        if intent == "investigate-recover":
            self.recover()
            if self.req.get("retry") and self.report.final and self.report.final["overall"] == "partial":
                self.recover(attempt=2)
        if intent == "what-if":
            self.whatif()
        if intent == "recover-files":
            self.recover_files()
        if intent == "rebuild":
            self.investigate()
            self.rebuild()
        if intent == "learn":
            self.learn()
        if intent == "retire-policy":
            self.retire()
        self.finish()
        self.report.stats = self.nas.stats()
        self.report.runtime_ms = round((time.perf_counter() - start) * 1000, 3)
        return self.report

    # hooks
    def baseline(self): ...
    def investigate(self): ...
    def review_map(self): ...
    def recover(self, attempt: int = 1): ...
    def whatif(self): ...
    def rebuild(self): ...
    def learn(self): ...
    def retire(self): ...
    def finish(self): ...

    # shared mechanics -----------------------------------------------------------
    def ensure_dirs(self, folder: str, destinations: list[str]) -> str | None:
        """Create the recovery folder and needed subfolders; return an error code or None."""
        needed = sorted({folder} | {posixpath.dirname(d) for d in destinations}, key=lambda p: p.count("/"))
        for path in needed:
            result = self.nas.mkdir(path)
            if result["ok"]:
                continue
            code = result["error"]["code"]
            if code == "exists" and (path != folder or getattr(self, "_reuse_folder", False)):
                continue
            return code
        return None

    def recover_files(self):
        """Recovery of user-chosen files without a prior reference: copy fidelity only."""
        folder = f"{self.parent}/cerbero-recovery-{self.sc.id}"
        if not self.answers.get("approve_plan", True):
            self.report.attempts.append({"plan": None, "folder": folder, "entries": {}, "overall": "cancelled"})
            return
        entries = {}
        dests = [f"{folder}/{item['dest_name']}" for item in self.req["files"]]
        error = self.ensure_dirs(folder, dests)
        for item, dest in zip(self.req["files"], dests):
            if error:
                entries[item["asset"]] = {"status": "cancelled" if error == "approval_declined" else "failed-copy", "dest": dest}
                continue
            before = self.nas.sha256(item["source"])
            result = self.nas.copy(item["source"], dest)
            if not result["ok"]:
                entries[item["asset"]] = {"status": "failed-copy", "dest": dest}
                continue
            after = self.nas.sha256(dest)
            same = before["ok"] and after["ok"] and before["data"]["sha256"] == after["data"]["sha256"]
            entries[item["asset"]] = {"status": "recovered" if same else "failed-verification",
                                      "dest": dest, "source": item["source"]}
        overall = "verified" if all(e["status"] == "recovered" for e in entries.values()) else "partial"
        self.report.attempts.append({"plan": None, "folder": folder, "entries": entries, "overall": overall})


# ---------------------------------------------------------------------------
class VariantA(Variant):
    """Simple flow without persisted memory."""
    name = "A-simple"

    def listing(self, root: str) -> tuple[dict[str, dict], set[str]]:
        result = self.nas.find(root, limit=LIMIT, max_depth=MAX_DEPTH)
        if not result["ok"]:
            return {}, {root}
        files = {posixpath.relpath(e["path"], root): e for e in result["data"]["entries"]}
        return files, set(result["data"]["denied"])

    def investigate(self):
        scope_files, denied = self.listing(self.scope_root)
        self.report.coverage["unreadable"] |= denied
        self.copies: dict[str, list[dict]] = {}
        for lid, root in self.copy_roots.items():
            files, loc_denied = self.listing(root)
            self.report.coverage["unreadable"] |= loc_denied
            for rel, entry in files.items():
                self.copies.setdefault(rel, []).append(entry)
        known = set(self.copies) | set(scope_files)
        for aid, asset in (self.sc.memory.assets.items() if self.sc.memory else []):
            rel = asset["rel"]
            if any(inside(asset["path"], d) for d in denied):
                self.report.states[aid] = "unknown"
            elif rel in scope_files:
                self.report.states[aid] = "intact"
            elif rel in known:
                self.report.states[aid] = "missing"
            else:
                self.report.states[aid] = "not-reported"
        self.missing_rel = sorted(rel for rel in self.copies if rel not in scope_files
                                  and not any(inside(f"{self.scope_root}/{rel}", d) for d in denied))

    def recover(self, attempt: int = 1):
        folder = f"{self.parent}/restore-{attempt}"
        plan = {}
        for rel in self.missing_rel:
            newest = max(self.copies[rel], key=lambda e: e["mtime"])
            plan[rel] = newest["path"]
        if not plan:
            self.report.attempts.append({"plan": None, "folder": folder, "entries": {}, "overall": "not-needed"})
            return
        if not self.answers.get("approve_plan", True):
            self.report.attempts.append({"plan": None, "folder": folder, "entries": {}, "overall": "cancelled"})
            return
        dests = {rel: f"{folder}/{rel}" for rel in plan}
        error = self.ensure_dirs(folder, list(dests.values()))
        entries = {}
        by_rel = {a["rel"]: aid for aid, a in (self.sc.memory.assets.items() if self.sc.memory else [])}
        for rel, src in plan.items():
            key = by_rel.get(rel, rel)
            if error:
                entries[key] = {"status": "cancelled" if error == "approval_declined" else "failed-copy", "dest": dests[rel]}
                continue
            result = self.nas.copy(src, dests[rel])
            if not result["ok"]:
                status = "cancelled" if result["error"]["code"] == "approval_declined" else "failed-copy"
                entries[key] = {"status": status, "dest": dests[rel], "source": src}
                continue
            d_src, d_dst = self.nas.sha256(src), self.nas.sha256(dests[rel])
            same = d_src["ok"] and d_dst["ok"] and d_src["data"]["sha256"] == d_dst["data"]["sha256"]
            entries[key] = {"status": "recovered" if same else "failed-verification", "dest": dests[rel], "source": src}
        self.report.attempts.append({"plan": None, "folder": folder, "entries": entries,
                                     "overall": overall_status([e["status"] for e in entries.values()], "recovered")})

    def whatif(self):
        names = self.req.get("member_names", [])
        roots = {lid: self.sc.location_root(lid) for lid in self.req.get("copy_locations", [])}
        for scenario in self.req["scenarios"]:
            failed = self.sc.location_root(scenario.get("named_location", scenario.get("location")))
            members = {}
            for rel in names:
                count = 0
                for lid, root in [(self.req["scope"], self.scope_root)] + list(roots.items()):
                    path = f"{root}/{rel}"
                    if not inside(path, failed) and self.nas.stat(path)["ok"]:
                        count += 1
                members[rel] = {"eligible": count, "uncertain": 0, "level": "modeled" if count else "none"}
            verdict = "recoverable" if all(m["eligible"] for m in members.values()) else "not-recoverable"
            self.report.whatif.append({"scenario": scenario["id"], "verdict": verdict, "members": members})


# ---------------------------------------------------------------------------
class VariantB(Variant):
    """Reference memory with hashes and approved sets."""
    name = "B-memory-hashes"

    def investigate(self):
        self.scope_digests: dict[str, str] | None = None
        for aid, asset in self.mem.assets.items():
            version = self.mem.versions[asset["current"]]
            result = self.nas.stat(asset["path"])
            if not result["ok"]:
                if result["error"]["code"] == "not_found":
                    self.locate(aid, version)
                else:
                    self.report.states[aid] = "unknown"
                continue
            digest = self.nas.sha256(asset["path"])
            self.report.states[aid] = "intact" if digest["ok"] and digest["data"]["sha256"] == version["sha256"] else "altered"

    def locate(self, aid, version):
        if self.scope_digests is None:
            self.scope_digests = {}
            listing = self.nas.find(self.scope_root, limit=LIMIT, max_depth=MAX_DEPTH)
            for entry in listing["data"]["entries"] if listing["ok"] else []:
                digest = self.nas.sha256(entry["path"])
                if digest["ok"]:
                    self.scope_digests[entry["path"]] = digest["data"]["sha256"]
        for path, digest in self.scope_digests.items():
            if digest == version["sha256"]:
                self.report.states[aid] = "moved"
                self.report.located_at[aid] = path
                return
        self.report.states[aid] = "missing"

    def recover(self, attempt: int = 1):
        target = self.set_of(self.req["target_set"])
        members = dict(self.mem.sets[target]["members"])
        in_sets = {a for s in self.mem.sets.values() for a in s["members"]}
        members.update({a: asset["current"] for a, asset in self.mem.assets.items() if a not in in_sets})
        needed = [a for a in members if self.report.states.get(a) in CHANGED]
        folder = f"{self.parent}/restore-{attempt}"
        plan = {}
        for aid in needed:
            vid = members[aid]
            copies = [c for c in self.mem.copies if c["version"] == vid and c["location"] in self.copy_roots]
            if copies:
                plan[aid] = copies[0]["path"]
            elif aid not in self.report.no_source:
                self.report.no_source.append(aid)
        if not plan:
            overall = "failed" if needed else "not-needed"
            entries = {aid: {"status": "no-source", "dest": None} for aid in self.report.no_source}
            self.report.attempts.append({"plan": None, "folder": folder, "entries": entries, "overall": overall})
            return
        if not self.answers.get("approve_plan", True):
            self.report.attempts.append({"plan": None, "folder": folder, "entries": {}, "overall": "cancelled"})
            return
        dests = {aid: f"{folder}/{self.mem.assets[aid]['rel']}" for aid in plan}
        error = self.ensure_dirs(folder, list(dests.values()))
        entries = {}
        for aid, src in plan.items():
            expected = self.mem.versions[members[aid]]["sha256"]
            if error:
                entries[aid] = {"status": "cancelled" if error == "approval_declined" else "failed-copy", "dest": dests[aid]}
                continue
            result = self.nas.copy(src, dests[aid])
            if not result["ok"]:
                status = "cancelled" if result["error"]["code"] == "approval_declined" else "failed-copy"
                entries[aid] = {"status": status, "dest": dests[aid], "source": src}
                continue
            digest = self.nas.sha256(dests[aid])
            good = digest["ok"] and digest["data"]["sha256"] == expected
            entries[aid] = {"status": "verified" if good else "failed-verification", "dest": dests[aid], "source": src}
        for aid in self.report.no_source:
            entries[aid] = {"status": "no-source", "dest": None}
        executed = [e["status"] for e in entries.values() if e["status"] != "no-source"]
        self.report.attempts.append({"plan": None, "folder": folder, "entries": entries,
                                     "overall": overall_status(executed, "verified")})

    def whatif(self):
        set_id = self.set_of(self.req["set"])
        for scenario in self.req["scenarios"]:
            failed = self.sc.location_root(scenario.get("named_location", scenario.get("location")))
            members = {}
            for aid, vid in self.mem.sets[set_id]["members"].items():
                count = sum(1 for c in self.mem.copies if c["version"] == vid and not inside(c["path"], failed))
                members[aid] = {"eligible": count, "uncertain": 0, "level": "modeled" if count else "none"}
            verdict = "recoverable" if all(m["eligible"] for m in members.values()) else "not-recoverable"
            self.report.whatif.append({"scenario": scenario["id"], "verdict": verdict, "members": members})

    def review_map(self):
        for aid, asset in self.mem.assets.items():
            if asset["importance"] != "critical":
                continue
            if not any(c["version"] == asset["current"] and not inside(c["path"], self.scope_root) for c in self.mem.copies):
                self.report.at_risk.append(aid)


# ---------------------------------------------------------------------------
class VariantC(Variant):
    """Full architecture as specified in the Skill references."""
    name = "C-full"

    def __init__(self, scenario, nas, memory, policies=(), selector=True, persist=True, session=None,
                 intent: str | None = None, declarations: dict | None = None, on_freeze=None):
        super().__init__(scenario, nas, memory, intent)
        self.session = session if session is not None else scan_session(nas, self.memory_root, memory)
        offered = list(policies) + list(self.session.policies)
        self.policies = [p for p in offered if set(p["effect"]) <= ALLOWED_EFFECTS]
        self.report.rejected_policies = [f"{p['id']}-{p['version']}" for p in offered if p not in self.policies]
        self.report.policy_decisions = dict(self.session.policy_decisions)
        self.selector = selector
        self.persist_enabled = persist
        self.decl = declarations
        self.on_freeze = on_freeze
        if not selector:
            self.name = self.report.variant = "C-no-selector"
        self.n = self.session.next_case
        self.case = f"CAS-{self.n:04d}"
        self.scope_id = memory.scope_id if memory else None
        self.ids = Counter()
        self.bundles = 0
        self.digests: dict[str, tuple[str | None, str]] = {}
        self.sizes: dict[str, int] = {}
        self.real_checked: dict[tuple[str, str], tuple[bool, str]] = {}
        self.digest_count = 0
        self.bytes_hashed = 0
        self.listings = self.session.listings
        self.phase = "investigate"
        self.partitions = 0
        self.copy_observed: dict[str, bool] = {}
        self.pending: list[tuple[str, str, dict]] = []
        self.saved: list[tuple[str, str]] = []
        self.folder: str | None = None
        self.scope_loc = self.loc_of(self.req["scope"]) if "scope" in self.req else None
        if memory is not None:
            self.report.rehearsals = list(memory.rehearsals)
        for path, info in sorted(self.session.files.items()):
            if info["status"] == "needs-review":
                self.report.open_items.append(f"{posixpath.basename(path)}: memory file needs review ({info['reason']})")
        for plan_id in self.session.unfinished_plans:
            self.report.open_items.append(f"{plan_id}: saved plan without a receipt; its outcome is unknown")
        if not self.session.inventory_complete:
            self.report.open_items.append("memory folder: inventory incomplete; files outside the index may exist unseen")
        if self.session.problems or any(i["status"] == "needs-review" for i in self.session.files.values()):
            self.report.acknowledged.append("memory-needs-review")

    # -- bookkeeping -------------------------------------------------------------
    def next_id(self, prefix: str) -> str:
        self.ids[prefix] += 1
        return f"{prefix}-{self.n:04d}-{self.ids[prefix]:04d}"

    def add(self, record_id: str, record_type: str, **fields) -> str:
        self.pending.append((record_id, record_type, fields))
        return record_id

    def card(self, doubt: str, decision: str, operation: str, outcomes: str, cost: str) -> str:
        self.report.cards += 1
        return self.add(self.next_id("CHK"), "check-card", doubt=doubt, decision=decision, operation=operation,
                        outcomes=outcomes, cost=cost, budget_left=DIGEST_BUDGET - self.digest_count)

    def observe(self, card: str | None, delegation: str, agent: str, result: dict, result_summary) -> str:
        state = "completed" if result["ok"] else "failed"
        return self.add(self.next_id("OBS"), "observation", check_card=card, agent=agent, delegation=delegation,
                        state=state, result=summary(result_summary), coverage="as returned", observed_at="unknown",
                        **{"class": "observed"})

    def set_state(self, aid: str, state: str, supports: str | None, located_at: str | None = None):
        self.report.states[aid] = state
        if located_at:
            self.report.located_at[aid] = located_at
        asset = self.mem.assets[aid]
        self.add(self.next_id("CLM"), "claim", kind="asset-state", subject=aid, asset_state=state, located_at=located_at,
                 statement=f"{asset.get('name') or asset['path']} is {state} relative to {asset['current']}",
                 supports=[supports] if supports else [], contradicts=[],
                 depends_on=[asset["current"]] + ([supports] if supports else []), status="current",
                 **{"class": "observed" if state != "unknown" else "unknown"})

    def open_item(self, subject: str, reason: str, needed: str):
        self.report.open_items.append(f"{subject}: {reason}")
        self.add(self.next_id("OPN"), "open-item", subject=subject, reason=reason, needed_to_resolve=needed)

    def real_path_ok(self, path: str, root: str) -> tuple[bool, str]:
        """D5 before any read of a path taken from memory or from the user: its real path must lie in root."""
        verdict = scope.containment(path, root)
        if verdict != "inside":
            return False, verdict
        key = (path, root)
        if key not in self.real_checked:
            result = self.nas.stat(path)
            if result["ok"] and "size" in result["data"]:
                self.sizes[path] = result["data"]["size"]
            self.real_checked[key] = scope.real_inside(result, root)
        return self.real_checked[key]

    def listed_inside(self, entry: dict, root: str) -> bool:
        """A listing entry is usable only when the real path the expert returned lies in root."""
        return scope.inside(entry["path"], root) and scope.inside(entry.get("realpath"), root)

    def list_call(self, call, *args, **kwargs) -> dict | None:
        """D3, D6 and D13 count against the listing budget of the session (memory loading included)."""
        if self.listings >= LISTING_BUDGET:
            self.report.coverage["budget_exhausted"] = True
            return None
        self.listings += 1
        return call(*args, **kwargs)

    def digest_in(self, path: str, root: str, fresh: bool = False) -> tuple[str | None, str]:
        """D7 on a path that must lie inside root, textually before the call and by the real path after it.

        Investigation stops before the recovery reserve; a known size that would pass the byte budget is
        not hashed.
        """
        verdict = scope.containment(path, root)
        if verdict != "inside":
            return None, verdict
        if not fresh and path in self.digests:
            return self.digests[path]
        reserve = self.phase == "investigate"
        size = self.sizes.get(path)
        if self.digest_count >= DIGEST_BUDGET - (DIGEST_RESERVE if reserve else 0) or \
                (size is not None and self.bytes_hashed + size > BYTE_BUDGET - (BYTE_RESERVE if reserve else 0)):
            self.report.coverage["budget_exhausted"] = True
            return None, "budget"
        result = self.nas.sha256(path)
        self.digest_count += 1
        if not result["ok"]:
            value = (None, result["error"]["code"])
        else:
            self.bytes_hashed += result["data"].get("size", 0)
            proven, why = scope.real_inside(result, root)
            value = (result["data"]["sha256"], "inside") if proven else (None, why)
            self.sizes[path] = result["data"].get("size", 0)
        self.digests[path] = value
        return value

    # -- persistence ---------------------------------------------------------------
    def bundle_of(self, items) -> Bundle:
        self.bundles += 1
        bundle = Bundle(f"B-{self.n:04d}-{self.bundles:02d}", case_id=self.case, scope_id=self.scope_id)
        for record_id, record_type, fields in items:
            bundle.add(record_id, record_type, **fields)
        return bundle

    def record_bytes(self, item) -> int:
        empty = Bundle("B-0000-00", case_id=self.case, scope_id=self.scope_id)
        one = Bundle("B-0000-00", case_id=self.case, scope_id=self.scope_id)
        one.add(item[0], item[1], **item[2])
        return len(one.render().encode("utf-8")) - len(empty.render().encode("utf-8"))

    def chunks(self, items, room: int = 0) -> list[list]:
        """Whole records, in order, grouped into bundles that each render within MAX_BUNDLE_BYTES."""
        header = len(Bundle("B-0000-00", case_id=self.case, scope_id=self.scope_id).render().encode("utf-8"))
        out, current, size = [], [], header + room
        for item in items:
            cost = self.record_bytes(item)
            if current and size + cost > MAX_BUNDLE_BYTES:
                out.append(current)
                current, size = [], header + room
            current.append(item)
            size += cost
        if current:
            out.append(current)
        return out

    def save(self, bundle: Bundle) -> tuple[str | None, str]:
        """D10. Returns the saved path or None with the reason; checks the answer, not just ok."""
        if not self.persist_enabled:
            return None, "persistence disabled"
        bundle_id = bundle.header["bundle_id"]
        text = bundle.render()
        result = self.nas.save_text(self.memory_root, f"CERBERO-{bundle_id}", text)
        if not result["ok"]:
            code = result["error"]["code"]
            return None, "declined" if code == "approval_declined" else code
        data = result["data"]
        out = data.get("outputFile")
        if not out:
            return None, "the save returned no file path"
        if data.get("verified") is not True:
            return None, "the save was not verified"
        if scope.containment(out, self.memory_root) != "inside" or "CERBERO-" not in posixpath.basename(out):
            self.report.open_items.append(f"{bundle_id}: saved outside the memory folder at {out}")
            return None, f"saved outside the memory folder ({out})"
        sent = len(text.encode("utf-8"))
        if data.get("contentBytes") != sent:
            self.report.open_items.append(f"{bundle_id}: the save reported {data.get('contentBytes')} of {sent} bytes")
            return None, f"incomplete save ({data.get('contentBytes')} of {sent} bytes)"
        self.saved.append((out, bundle_id))
        self.report.persisted.append(out)
        self.sizes[out] = sent
        return out, "saved"

    def checkpoint(self, extra=()) -> str | None:
        """Report saves: failure is acknowledged and the session continues; unsaved case records stay pending."""
        if not self.persist_enabled:
            return None
        items = list(self.pending) + list(extra)
        last = None
        for chunk in self.chunks(items):
            bundle = self.bundle_of(chunk)
            path, reason = self.save(bundle)
            if path is None:
                self.report.acknowledged.append("not-persisted")
                self.report.open_items.append(f"{bundle.header['bundle_id']}: not persisted ({reason})")
                continue
            self.pending = [p for p in self.pending if not any(p is c for c in chunk)]
            last = path
        return last

    def save_mandatory(self, items) -> tuple[str | None, str]:
        """A mandatory save of records that must sit in one file: case records go first as report saves."""
        if self.pending and sum(self.record_bytes(i) for i in list(self.pending) + list(items)) > MAX_BUNDLE_BYTES - 1024:
            self.checkpoint()
        bundle = self.bundle_of(list(self.pending) + list(items))
        path, reason = self.save(bundle)
        if path is not None:
            self.pending = []
        return path, reason

    def save_plan(self, plan_records) -> tuple[str | None, dict, str]:
        """Mandatory plan save. When the entries do not fit in one bundle they are saved first as fragments,
        each hashed with D7, and the plan record lists every fragment with its digest: the head file digest
        that the user confirms then binds every entry."""
        plan, entries = plan_records[0], plan_records[1:]
        if sum(self.record_bytes(i) for i in plan_records) <= MAX_BUNDLE_BYTES - 1024:
            path, reason = self.save_mandatory(plan_records)
            return path, {}, reason
        self.checkpoint()
        fragments = {}
        for chunk in self.chunks(entries):
            path, reason = self.save(self.bundle_of(chunk))
            if path is None:
                return None, {}, f"plan fragment not persisted: {reason}"
            digest, why = self.digest_in(path, self.memory_root, fresh=True)
            if digest is None:
                return None, {}, f"plan fragment could not be hashed ({why})"
            fragments[path] = digest
        plan[2]["fragments"] = fragments
        path, reason = self.save(self.bundle_of([plan]))
        return path, fragments, reason

    # -- policy effects ----------------------------------------------------------
    def policy_hit(self, aid: str, policy: dict):
        key = f"{policy['id']}-{policy['version']}"
        self.report.policy_effects.add(f"{aid}:{key}")
        self.report.policy_evidence[key] = policy.get("evidence", {"source": "passed in by the caller, not loaded from memory"})

    def critical(self, aid: str) -> bool:
        asset = self.mem.assets[aid]
        if asset["importance"] == "critical":
            return True
        for policy in self.policies:
            if any(rel_inside(asset.get("rel"), prefix) for prefix in policy["effect"].get("promote_critical", [])):
                self.policy_hit(aid, policy)
                return True
        return False

    def set_member(self, aid: str) -> bool:
        return any(aid in s["members"] for s in self.mem.sets.values())

    def informational(self, aid: str) -> bool:
        if self.critical(aid) or self.set_member(aid):
            return False
        rel = self.mem.assets[aid].get("rel")
        for policy in self.policies:
            if any(rel_inside(rel, prefix) for prefix in policy["effect"].get("informational", [])):
                self.policy_hit(aid, policy)
                return True
        return False

    # -- baseline ------------------------------------------------------------------
    def baseline(self):
        """Record the expected state from the user declarations, with fresh IDs for this memory folder."""
        d = self.decl
        roots = {lid: norm(loc["root"]) for lid, loc in d["locations"].items()}
        project = roots[d["scope"]]
        self.scope_id = "SCP-0001"
        self.add(self.case, "case", scope_id=self.scope_id, request="baseline", status="open", opened_in="this session")
        stm_auth = self.add(self.next_id("STM"), "statement", text=f"Cerbero may read {project} and the copy folders "
                            f"{', '.join(r for l, r in roots.items() if l != d['scope'])}, and save notes in "
                            f"{self.memory_root}.", given_in="this session", **{"class": "user-declared"})
        stm_critical = self.add(self.next_id("STM"), "statement", text="These files are critical: " +
                                ", ".join(posixpath.basename(p) for p in d["critical"]) + ".",
                                given_in="this session", **{"class": "user-declared"})
        stm_domains = self.add(self.next_id("STM"), "statement", text=" ".join(d["statements"]) or "No failure domain stated.",
                               given_in="this session", **{"class": "user-declared"})
        dom_ids = {key: self.next_id("DOM") for key in d["domains"]}
        for key, dom in d["domains"].items():
            self.add(dom_ids[key], "domain", kind=dom["kind"], label=dom.get("label", key),
                     parent=dom_ids.get(dom.get("parent")), provenance=stm_domains)
        loc_ids = {lid: self.next_id("LOC") for lid in d["locations"]}

        def owner(path: str) -> str | None:
            """The deepest named location that holds a path: one copy record per file."""
            holders = [lid for lid, root in roots.items() if scope.inside(path, root)]
            return max(holders, key=lambda lid: roots[lid].count("/"), default=None)

        listings: dict[str, list[dict]] = {}
        listing_obs: dict[str, str] = {}
        for lid, root in roots.items():
            card = self.card(f"Which files are in {root}?", "what the baseline records", "D6 file-agent",
                             "entries: assets or copy candidates", "full listing")
            entries, complete = self.search(root, None)
            listings[lid] = entries
            listing_obs[lid] = self.observe(card, "D6", "file-agent", {"ok": True},
                                            f"{len(entries)} files, complete={complete}")
            if not complete:
                self.open_item(root, "baseline listing possibly incomplete", "a complete listing")
            loc = d["locations"][lid]
            self.add(loc_ids[lid], "location", real_root=root,
                     memberships={k: dom_ids[v] for k, v in loc.get("memberships", {}).items()},
                     unknown_kinds=list(loc.get("unknown_kinds", [])), provenance=stm_domains,
                     inventory="complete" if complete else "possibly-incomplete")
        newest = max((e["mtime"] for e in listings[d["scope"]]), default=None)
        self.add(self.scope_id, "scope", real_root=project, name=posixpath.basename(project), authorized_by=stm_auth,
                 newest_mtime=newest)

        versions: dict[tuple[str, str], str] = {}
        version_fields: dict[str, dict] = {}

        def version_for(aid: str, digest: str, size: int, obs: str) -> str:
            if (aid, digest) not in versions:
                vid = versions[(aid, digest)] = self.next_id("VER")
                version_fields[vid] = {"asset_id": aid, "sha256": digest, "size_bytes": size, "approved_by": None,
                                       "observation": obs}
            return versions[(aid, digest)]

        assets: dict[str, str] = {}
        asset_fields: dict[str, dict] = {}
        project_files = [e for e in listings[d["scope"]] if owner(e["path"]) == d["scope"]]
        hash_obs = self.observe(None, "D7", "file-agent", {"ok": True}, f"{len(project_files)} project files hashed")
        for entry in sorted(project_files, key=lambda e: e["path"]):
            digest, why = self.digest_in(entry["path"], project)
            if digest is None:
                self.open_item(entry["path"], f"not hashed at baseline ({why})", "a digest of the file")
                continue
            aid = assets[entry["path"]] = self.next_id("AST")
            critical = entry["path"] in d["critical"]
            asset_fields[aid] = {"scope_id": self.scope_id, "name": posixpath.basename(entry["path"]),
                                 "recorded_path": entry["path"], "importance": "critical" if critical else "ordinary",
                                 "declared_by": stm_critical if critical else stm_auth,
                                 "current_version": version_for(aid, digest, entry["size"], hash_obs),
                                 "recorded_size": entry["size"], "recorded_mtime": entry["mtime"],
                                 "observation": listing_obs[d["scope"]]}

        sets = []
        for name, members in d["sets"].items():
            stm = self.add(self.next_id("STM"), "statement", text=f"{name} is an approved set: " +
                           ", ".join(posixpath.basename(a) for a in members) + ".", given_in="this session",
                           **{"class": "user-declared"})
            pairs, problem = {}, None
            for asset_path, holder in members.items():
                if asset_path not in assets or holder is None:
                    problem = f"version of {posixpath.basename(asset_path)} not observed"
                    break
                holder_root = roots.get(owner(holder)) if owner(holder) else None
                digest, why = self.digest_in(holder, holder_root) if holder_root else (None, "outside named folders")
                if digest is None:
                    problem = f"version of {posixpath.basename(asset_path)} not hashed ({why})"
                    break
                size = next((e["size"] for es in listings.values() for e in es if e["path"] == holder), None)
                vid = version_for(assets[asset_path], digest, size or 0, hash_obs)
                version_fields[vid]["approved_by"] = stm
                pairs[assets[asset_path]] = vid
            if problem:
                self.open_item(name, f"approved set not recorded: {problem}", "the missing version")
                continue
            sets.append((self.next_id("SET"), {"name": name, "members": pairs, "approved_by": stm, "status": "current"}))

        for aid, fields in asset_fields.items():
            self.add(aid, "asset", **fields)
        for vid, fields in version_fields.items():
            self.add(vid, "version", **fields)
        set_ids = {}
        for sid, fields in sets:
            self.add(sid, "approved-set", **fields)
            set_ids[fields["name"]] = sid

        by_digest: dict[str, list[str]] = {}
        for vid, fields in version_fields.items():
            by_digest.setdefault(fields["sha256"], []).append(vid)
        sizes = {fields["size_bytes"] for fields in version_fields.values()}
        copies_of: dict[str, list[str]] = {}
        for lid, root in roots.items():
            obs = self.observe(None, "D7", "file-agent", {"ok": True}, f"size-matched files hashed in {root}")
            for entry in listings[lid]:
                if owner(entry["path"]) != lid or entry["size"] not in sizes:
                    continue
                digest, _ = self.digest_in(entry["path"], root)
                for vid in by_digest.get(digest, []):
                    cid = self.add(self.next_id("CPY"), "copy", version_id=vid, real_path=entry["path"],
                                   location_id=loc_ids[lid], sha256=digest, observation=obs, access="readable",
                                   status="current")
                    copies_of.setdefault(vid, []).append(cid)

        claim_ids = {c["key"]: self.next_id("CLM") for c in d.get("claims", [])}
        for c in d.get("claims", []):
            sid = set_ids.get(c.get("set"))
            depends = [cid for vid in (dict(sets)[sid]["members"].values() if sid else []) for cid in copies_of.get(vid, [])]
            depends += [claim_ids[k] for k in c.get("depends_on", []) if k in claim_ids]
            self.add(claim_ids[c["key"]], "claim", kind="recoverability", subject=sid or self.case,
                     statement=c["statement"], supports=[], contradicts=[], depends_on=depends, status="current",
                     **{"class": "inferred"})
        self.checkpoint()

    # -- investigation -----------------------------------------------------------
    def search(self, root: str, size: int | None, depth: int = MAX_DEPTH) -> tuple[list[dict], bool]:
        result = self.list_call(self.nas.find, root, size=size, limit=LIMIT, max_depth=depth)
        if result is None:
            self.report.coverage["truncated"].add(root)
            return [], False
        if not result["ok"]:
            self.report.coverage["unreadable"].add(root)
            return [], False
        data = result["data"]
        entries_in = [e for e in data["entries"] if self.listed_inside(e, root)]
        self.sizes.update({e["path"]: e["size"] for e in entries_in})
        complete = not data["denied"] and len(entries_in) == len(data["entries"])
        self.report.coverage["unreadable"] |= set(data["denied"])
        if not data["truncated"] and len(data["entries"]) < LIMIT:
            return entries_in, complete
        self.report.coverage["truncated"].add(root)
        if self.partitions >= PARTITION_BUDGET or depth <= 1:
            return entries_in, False
        self.partitions += 1
        entries: list[dict] = []
        direct = self.list_call(self.nas.find, root, size=size, limit=LIMIT, max_depth=1)
        if direct and direct["ok"]:
            entries += [e for e in direct["data"]["entries"] if self.listed_inside(e, root)]
            complete &= not direct["data"]["truncated"]
        else:
            complete = False
        listing = self.list_call(self.nas.ls, root, limit=LIMIT)
        if not listing or not listing["ok"] or listing["data"]["truncated"]:
            complete = False
        for child in listing["data"]["entries"] if listing and listing["ok"] else []:
            if child["type"] == "dir" and scope.inside(child["path"], root):
                sub, sub_complete = self.search(child["path"], size, depth - 1)
                entries += sub
                complete &= sub_complete
        if complete:
            self.report.coverage["truncated"].discard(root)
        return entries, complete

    def investigate(self):
        self.add(self.case, "case", scope_id=self.scope_id, request=self.intent, status="open", opened_in="this session")
        order = sorted(self.mem.assets, key=lambda a: (0 if self.critical(a) else 1 if self.set_member(a) else 2,
                                                       self.mem.assets[a]["path"]))
        missing = []
        for aid in order:
            asset = self.mem.assets[aid]
            version = self.mem.versions[asset["current"]]
            verdict = scope.containment(asset["path"], self.scope_root)
            if verdict != "inside":
                self.report.out_of_scope.append(aid)
                self.set_state(aid, "unknown", None)
                self.open_item(aid, f"recorded path not inside the project ({verdict}); not read",
                               "an asset record confirmed by the user")
                continue
            card = self.card(f"Is {asset.get('name')} present at its recorded path?", "whether it needs a digest, a search or recovery",
                             "D5 file-agent", "absent: search; same metadata: digest when critical; changed: digest", "metadata")
            result = self.nas.stat(asset["path"])
            obs = self.observe(card, "D5", "file-agent", result, result["data"] if result["ok"] else result["error"])
            if not result["ok"]:
                if result["error"]["code"] == "not_found":
                    missing.append(aid)
                    continue
                self.set_state(aid, "unknown", obs)
                self.open_item(aid, result["error"]["code"], "read access to the recorded folder")
                self.report.coverage["unreadable"].add(posixpath.dirname(asset["path"]))
                continue
            proven, why = scope.real_inside(result, self.scope_root)
            self.sizes[asset["path"]] = result["data"]["size"]
            if not proven:
                self.report.out_of_scope.append(aid)
                self.set_state(aid, "unknown", obs)
                self.open_item(aid, f"real path not proven inside the project ({why}); not hashed",
                               "a D5 result with a real path inside the project")
                continue
            same_meta = result["data"]["size"] == version["size"] and result["data"]["mtime"] == asset["mtime"]
            if self.informational(aid):
                self.set_state(aid, "intact-metadata" if same_meta else "informational-change", obs)
                continue
            if self.selector and same_meta and not self.critical(aid) and not self.set_member(aid):
                self.report.coverage["metadata_only"] += 1
                self.set_state(aid, "intact-metadata", obs)
                continue
            card = self.card(f"Does {asset.get('name')} still hold {asset['current']}?", "whether it needs recovery",
                             "D7 file-agent", "equal digest: intact; different: altered", f"digest of {result['data']['size']} bytes")
            digest, why = self.digest_in(asset["path"], self.scope_root)
            obs = self.observe(card, "D7", "file-agent", {"ok": digest is not None}, digest or f"not hashed ({why})")
            if digest is None:
                self.set_state(aid, "unknown", obs)
                self.open_item(aid, f"digest not available ({why})", "digest budget, read access or a real path in scope")
                continue
            self.set_state(aid, "intact" if digest == version["sha256"] else "altered", obs)
        for aid in missing:
            self.locate(aid)
        if self.req.get("ask_cause"):
            self.read_documents()
        self.report.causes.append("unknown")
        self.add(self.next_id("CLM"), "claim", kind="cause", subject=self.case,
                 statement="cause unknown: no source states one", supports=[], contradicts=[],
                 depends_on=[], status="current", **{"class": "unknown"})
        if self.report.coverage["unreadable"] or self.report.coverage["truncated"] or self.report.coverage["budget_exhausted"]:
            self.report.acknowledged.append("coverage-incomplete")
        if self.intent == "investigate":
            self.checkpoint()

    def locate(self, aid: str):
        asset = self.mem.assets[aid]
        version = self.mem.versions[asset["current"]]
        size = version["size"] if self.selector else None
        card = self.card(f"Was {asset.get('name')} moved or renamed inside the project?", "whether recovery is needed",
                         "D6 then D7 file-agent", "digest match: moved; none: absent from scope",
                         "exact-size listing" if self.selector else "full listing")
        entries, complete = self.search(self.scope_root, size)
        for entry in entries:
            if entry["path"] == asset["path"]:
                continue
            if self.digest_in(entry["path"], self.scope_root)[0] == version["sha256"]:
                obs = self.observe(card, "D7", "file-agent", {"ok": True}, f"match at {entry['path']}")
                self.set_state(aid, "moved", obs, located_at=entry["path"])
                return
        obs = self.observe(card, "D6", "file-agent", {"ok": True}, f"{len(entries)} candidates, no match")
        self.set_state(aid, "missing", obs)
        if not complete:
            self.open_item(aid, "in-scope search incomplete", "complete listing of the project")

    def read_documents(self):
        card = self.card("Does a new project note state an intended change?", "whether any change is stated as intended",
                         "D6 then D8 document-agent", "statement found: document-stated claim; none: cause unknown",
                         "document reading")
        result = self.list_call(self.nas.find, self.scope_root, limit=LIMIT, newer_than=self.mem.baseline_time,
                                suffixes=DOC_SUFFIXES)
        entries = [e for e in (result["data"]["entries"] if result and result["ok"] else []) if self.listed_inside(e, self.scope_root)]
        for entry in entries[:2]:
            answer = self.nas.doc_qa(entry["path"], DOC_QUESTION)
            self.observe(card, "D8", "document-agent", answer, f"read {entry['path']}")
            if not answer["ok"]:
                continue
            source = f"{entry['path']}@{self.digest_in(entry['path'], self.scope_root)[0] or 'unknown'}"
            for quote in answer["data"]["quotes"]:
                if INSTRUCTION_RE.search(quote):
                    self.report.findings.append({"source": entry["path"], "quote": quote})
                    self.add(self.next_id("FND"), "finding", source=source, quote=quote,
                             kind="instruction-like-text", action_taken="none: treated as data")

    # -- recoverability ----------------------------------------------------------------
    def named_roots(self) -> dict[str, str]:
        """Memory locations the user named in this session, with the real root resolved now."""
        roots = {lid: root for lid, root in self.copy_roots.items() if lid in (self.mem.locations if self.mem else {})}
        if self.scope_loc:
            roots[self.scope_loc] = self.scope_root
        return roots

    def scenario_for_review(self) -> dict:
        location = self.mem.locations.get(self.scope_loc) or {}
        volume = location.get("memberships", {}).get("volume")
        if volume:
            return {"id": "scope-volume-failure", "type": "domain", "domain": volume}
        return {"id": "scope-unavailable", "type": "location", "location": self.scope_loc}

    def review_map(self):
        scenario = self.scenario_for_review()
        maps = []
        for aid in sorted(self.mem.assets):
            if not self.critical(aid):
                continue
            result = evaluate_member(self.mem, self.mem.assets[aid]["current"], scenario, self.copy_observed)
            if result["eligible"] == 0:
                self.report.at_risk.append(aid)
            maps.append((self.next_id("MAP"), "map", {
                "subject": aid, "scenario": scenario["id"], "verdict": "recoverable" if result["eligible"] else
                ("not-recoverable" if not result["uncertain"] else "undetermined"),
                "members": {aid: f"{result['level']} eligible={result['eligible']} uncertain={result['uncertain']}"
                                 + (f" rehearsed-before={len(result['rehearsed'])}" if result["rehearsed"] else "")},
                "evidence_level": result["level"], "unknowns": result["uncertain_copies"]}))
        self.checkpoint(maps)

    def whatif(self):
        set_id = self.set_of(self.req["set"])
        if set_id is None:
            self.open_item(self.req["set"], "approved set not found in loaded memory", "a recorded approved set")
            return
        roots = self.named_roots()
        if self.req.get("verify"):
            versions = set(self.mem.sets[set_id]["members"].values())
            for copy in self.mem.copies:
                if copy["version"] in versions and copy["status"] == "current" and copy["location"] in roots:
                    if not self.real_path_ok(copy["path"], roots[copy["location"]])[0]:
                        continue
                    digest, why = self.digest_in(copy["path"], roots[copy["location"]], fresh=True)
                    if digest is None and why in scope.SCOPE_FAILURES:
                        continue
                    self.copy_observed[copy["id"]] = digest == copy["sha256"]
                    if digest != copy["sha256"]:
                        self.contradict(copy, digest)
        maps = []
        for scenario in self.req["scenarios"]:
            result = evaluate_set(self.mem, set_id, self.scenario_in_memory(scenario), self.copy_observed)
            result["scenario"] = scenario["id"]
            self.report.whatif.append(result)
            members = {a: f"{m['level']} eligible={m['eligible']} uncertain={m['uncertain']}"
                          + (f" rehearsed-before={len(m['rehearsed'])}" if m["rehearsed"] else "") for a, m in result["members"].items()}
            unknowns = [a for a, m in result["members"].items() if m["uncertain"]]
            maps.append((self.next_id("MAP"), "map", {"subject": set_id, "scenario": scenario["id"],
                                                      "verdict": result["verdict"], "members": members,
                                                      "evidence_level": result["level"], "unknowns": unknowns}))
            if unknowns:
                self.report.acknowledged.append("domain-unknown")
        self.checkpoint(maps)

    def contradict(self, copy: dict, seen_digest: str | None):
        """Record the contradiction and mark dependents needs-review with superseding records."""
        copy["status"] = "needs-review"
        self.report.contradictions.append(copy["id"])
        self.add(self.next_id("CPY"), "copy", version_id=copy["version"], real_path=copy["path"],
                 location_id=copy["location"], sha256=copy.get("sha256"), observation=copy.get("observation"),
                 access=copy.get("access", "unknown"), status="needs-review", supersedes=copy["id"])
        self.add(self.next_id("CLM"), "claim", kind="contradiction", subject=copy["id"],
                 statement=f"recorded copy {copy['path']} no longer holds {copy['version']}",
                 supports=[], contradicts=[copy["observation"]] if copy.get("observation") else [],
                 depends_on=[f"{copy['path']}@{seen_digest or 'unreadable'}"], status="current",
                 **{"class": "contradicted"})
        frontier, seen = [copy["id"]], set()
        while frontier:
            source = frontier.pop()
            for claim in self.mem.claims:
                if source in claim["depends_on"] and claim["id"] not in seen:
                    seen.add(claim["id"])
                    claim["status"] = "needs-review"
                    self.report.revalidated.append(claim["id"])
                    frontier.append(claim["id"])
                    self.add(self.next_id("CLM"), "claim", kind=claim.get("kind", "recoverability"),
                             subject=claim.get("subject", copy["id"]), statement=claim["statement"],
                             supports=claim.get("supports", []), contradicts=claim.get("contradicts", []),
                             depends_on=claim["depends_on"], status="needs-review", supersedes=claim["id"],
                             **{"class": claim.get("class", "inferred")})

    # -- recovery ----------------------------------------------------------------------
    def candidates(self, aid: str, vid: str, lid: str) -> list[dict]:
        """Copies of a version recorded at a named location that memory does not already exclude."""
        found = []
        for copy in self.mem.copies:
            if copy["version"] != vid or copy["location"] != lid:
                continue
            result = copy_eligibility(self.mem, copy, vid, None, self.copy_observed)
            if result["state"] == "excluded":
                if copy["id"] not in self.copy_observed:
                    self.copy_observed[copy["id"]] = False
                    self.open_item(copy["id"], "copy record not usable: " + "; ".join(result["reasons"]),
                                   "a re-observed copy record")
                continue
            found.append(copy)
        return found

    def candidate_order(self, needed: list[str], members: dict[str, str]) -> list[str]:
        coverage = Counter()
        for aid in needed:
            for lid in self.copy_roots:
                if any(c["version"] == members[aid] and c["location"] == lid and c["status"] == "current"
                       and copy_eligibility(self.mem, c, members[aid], None, self.copy_observed)["state"] != "excluded"
                       for c in self.mem.copies):
                    coverage[lid] += 1
        order = list(self.copy_roots)
        return sorted(order, key=lambda lid: (-coverage[lid], order.index(lid)))

    def select_source(self, aid: str, vid: str, location_order: list[str]) -> tuple[str, str] | None:
        version = self.mem.versions[vid]
        tried = set()
        for lid in location_order:
            root = self.copy_roots[lid]
            for copy in self.candidates(aid, vid, lid):
                tried.add(copy["path"])
                proven, why = self.real_path_ok(copy["path"], root)
                if not proven:
                    self.copy_observed[copy["id"]] = False
                    self.open_item(copy["id"], f"real path not proven inside {root} ({why}); not read", "a copy inside the location")
                    continue
                digest, why = self.digest_in(copy["path"], root, fresh=True)
                if digest is None and why in scope.SCOPE_FAILURES:
                    self.copy_observed[copy["id"]] = False
                    self.open_item(copy["id"], f"real path not proven inside {root} ({why}); not used", "a copy inside the location")
                    continue
                if digest == version["sha256"]:
                    self.copy_observed[copy["id"]] = True
                    return copy["path"], lid
                self.copy_observed[copy["id"]] = False
                self.contradict(copy, digest)
        for lid in location_order:
            root = self.copy_roots[lid]
            entries, complete = self.search(root, version["size"])
            for entry in entries:
                if entry["path"] in tried:
                    continue
                if self.digest_in(entry["path"], root, fresh=True)[0] == version["sha256"]:
                    return entry["path"], lid
            if not complete:
                self.open_item(aid, f"copy search incomplete in {root}", "complete listing of the location")
        return None

    def target(self, set_id: str) -> dict[str, str]:
        """The requested target: the members of the approved set the user named, and nothing else."""
        return dict(self.mem.sets[set_id]["members"])

    def needed_for(self, set_id: str) -> list[str]:
        needed = []
        for aid, vid in self.target(set_id).items():
            state = self.report.states.get(aid)
            if state in CHANGED:
                needed.append(aid)
            elif state in ("intact", "intact-metadata", "moved") and self.mem.assets[aid]["current"] != vid:
                needed.append(aid)
        return needed

    def plan_sources(self, set_id: str) -> tuple[dict[str, tuple[str, str]], list[str]]:
        members = self.target(set_id)
        needed = self.needed_for(set_id)
        order = self.candidate_order(needed, members)
        sources, missing = {}, []
        for aid in needed:
            found = self.select_source(aid, members[aid], order)
            if found:
                sources[aid] = found
            else:
                missing.append(aid)
        return sources, missing

    def report_outside(self, set_id: str) -> list[str]:
        """Changed assets outside the requested target: reported with the source a later request could use.

        They are never added to the plan; the user decides whether to ask for them.
        """
        members = self.target(set_id)
        rows = []
        for aid in sorted(self.mem.assets):
            state = self.report.states.get(aid)
            if aid in members or state not in CHANGED:
                continue
            found = self.select_source(aid, self.mem.assets[aid]["current"], list(self.copy_roots))
            if not found and aid not in self.report.no_source:
                self.report.no_source.append(aid)
            rows.append({"asset": aid, "name": self.mem.assets[aid].get("name"), "state": state,
                         "source": found[0] if found else None})
            self.open_item(aid, f"outside the requested target: {state}; " +
                           (f"a copy of its recorded version is at {found[0]}; not copied" if found
                            else "no copy of its recorded version in the named locations"),
                           "a request that names this file")
        self.report.outside_target = rows
        return [r["asset"] for r in rows]

    def recovery_folder(self, prefix: str = "cerbero-recovery-") -> str | None:
        """D2 on the parent the user named; the new folder is a direct child of its real path."""
        if self.folder:
            return self.folder
        result = self.nas.stat(self.parent)
        real = result["data"].get("realpath") if result["ok"] else None
        if not result["ok"] or result["data"].get("type") != "dir" or not scope.canonical(real):
            self.open_item(self.parent, "recovery parent folder unavailable or its real path not reported",
                           "an existing folder named by the user")
            return None
        self.folder, _ = scope.child(real, f"{prefix}{self.case}")
        return self.folder

    def destination(self, aid: str, folder: str) -> tuple[str | None, str]:
        """folder plus the asset path relative to the project, only if both stay in scope."""
        asset = self.mem.assets[aid]
        rel, why = scope.relative_inside(asset["path"], self.mem.scope_root)
        if rel is None:
            return None, f"recorded path not inside the project ({why})"
        if asset.get("rel") not in (None, rel):
            return None, "recorded relative path disagrees with the recorded path"
        return scope.child(folder, rel)

    def name_of(self, aid: str) -> str:
        return self.mem.assets[aid].get("name") or posixpath.basename(self.mem.assets[aid]["path"])

    def unchecked_entry(self, aid: str, vid: str) -> dict:
        """A target member whose state is unknown: never copied, kept pending by name."""
        out = aid in self.report.out_of_scope
        return {"entry": None, "source": None, "dest": None, "version": vid, "name": self.name_of(aid),
                "status": "out-of-scope" if out else "state-unknown",
                "note": f"{self.name_of(aid)}: " + ("recorded path not in scope; not read" if out
                                                     else "could not be checked; not copied")}

    def entry_for(self, aid: str, vid: str, source: tuple[str, str, str], folder: str, number: str,
                  provenance: str) -> dict:
        path, lid, root = source
        dest, why = self.destination(aid, folder)
        entry = {"entry": number, "source": path, "location": lid, "source_root": root, "dest": dest, "version": vid,
                 "expected": self.mem.versions[vid]["sha256"], "size": self.mem.versions[vid]["size"],
                 "name": self.name_of(aid), "status": "not-attempted", "provenance": provenance}
        if dest is None:
            entry.update(status="out-of-scope", note=why)
            self.report.out_of_scope.append(aid)
            self.open_item(aid, f"destination not inside the recovery folder ({why})", "an asset record confirmed by the user")
        return entry

    def recover(self, attempt: int = 1):
        self.phase = "recover"
        previous = self.report.final if attempt > 1 else None
        target = previous["set"] if previous else self.set_of(self.req["target_set"])
        if target is None:
            self.open_item(self.req["target_set"], "approved set not found in loaded memory", "a recorded approved set")
            self.report.attempts.append({"plan": None, "set": None, "folder": None, "entries": {}, "overall": "failed",
                                         "reason": "target set not found"})
            return
        if previous:
            sources = {aid: (e["source"], e["location"]) for aid, e in previous["entries"].items() if e["status"] in VERIFIED}
            members_prev = self.target(target)
            order = self.candidate_order([a for a in self.needed_for(target) if a not in sources], members_prev)
            missing = []
            for aid in self.needed_for(target):
                if aid in sources:
                    continue
                found = self.select_source(aid, members_prev[aid], order)
                if found:
                    sources[aid] = found
                else:
                    missing.append(aid)
        else:
            sources, missing = self.plan_sources(target)
        if missing and attempt == 1:
            self.report.acknowledged.append("partial-set")
            for other in sorted(self.mem.sets):
                if other != target:
                    _, alt_missing = self.plan_sources(other)
                    if not alt_missing:
                        self.report.alternatives.append(other)
            choice = self.answers.get("on_partial", "proceed-partial")
            if choice == "stop":
                self.report.attempts.append({"plan": None, "set": target, "folder": None, "entries": {}, "overall": "cancelled"})
                return
            if choice == "alternative-set" and self.report.alternatives:
                target = self.report.alternatives[0]
                sources, missing = self.plan_sources(target)
        for aid in missing:
            if aid not in self.report.no_source:
                self.report.no_source.append(aid)
        members = self.target(target)
        outside = self.report_outside(target) if not previous else list(previous.get("outside", []))
        folder = previous["folder"] if previous else self.recovery_folder()
        if folder is None:
            self.report.attempts.append({"plan": None, "set": target, "folder": None, "entries": {}, "overall": "failed",
                                         "reason": "recovery folder unavailable"})
            return
        entries = {}
        for k, (aid, (src, lid)) in enumerate(sorted(sources.items()), start=1):
            entries[aid] = self.entry_for(aid, members[aid], (src, lid, self.copy_roots[lid]), folder,
                                          f"ENT-{self.n:04d}-{attempt:02d}-{k:02d}", f"copy in {self.copy_roots[lid]}")
        for aid in missing:
            entries[aid] = {"entry": None, "source": None, "dest": None, "version": members[aid], "name": self.name_of(aid),
                            "status": "no-source", "note": f"{self.name_of(aid)}: no eligible copy in the named locations"}
        for aid, vid in members.items():
            if self.report.states.get(aid) == "unknown":
                entries[aid] = self.unchecked_entry(aid, vid)
        record = {"plan": f"PLN-{self.n:04d}-{attempt:02d}", "set": target, "target_kind": "approved-set",
                  "target_members": sorted(members), "outside": outside, "reference": "approved-version",
                  "folder": folder, "entries": entries, "receipt": None, "previous": previous, "attempt": attempt,
                  "pending": sorted(k for k, e in entries.items() if e["status"] in PENDING)}
        self.report.attempts.append(record)
        self.execute(record, retry=previous is not None)

    def rebuild(self):
        """Full rebuild: every member of the approved set into a new folder, the intact ones included."""
        self.phase = "recover"
        target = self.set_of(self.req["target_set"])
        if target is None:
            self.open_item(self.req["target_set"], "approved set not found in loaded memory", "a recorded approved set")
            self.report.attempts.append({"plan": None, "set": None, "folder": None, "entries": {}, "overall": "failed",
                                         "reason": "target set not found"})
            return
        members = self.target(target)
        folder = self.recovery_folder("cerbero-rebuild-")
        if folder is None:
            self.report.attempts.append({"plan": None, "set": target, "folder": None, "entries": {}, "overall": "failed",
                                         "reason": "rebuild folder unavailable"})
            return
        entries, k = {}, 0
        for aid, vid in sorted(members.items()):
            state = self.report.states.get(aid)
            if state == "unknown" and aid in self.report.out_of_scope:
                entries[aid] = self.unchecked_entry(aid, vid)
                continue
            same = self.mem.assets[aid]["current"] == vid
            if state == "intact" and same:
                source, provenance = (self.mem.assets[aid]["path"], self.scope_loc, self.scope_root), "original in the project folder"
            elif state == "moved" and same:
                source, provenance = (self.report.located_at[aid], self.scope_loc, self.scope_root), \
                    f"original in the project folder, moved to {self.report.located_at[aid]}"
            else:
                found = self.select_source(aid, vid, self.candidate_order([aid], members))
                source = (found[0], found[1], self.copy_roots[found[1]]) if found else None
                provenance = f"copy in {source[2]}" if source else ""
            if source is None:
                if aid not in self.report.no_source:
                    self.report.no_source.append(aid)
                entries[aid] = {"entry": None, "source": None, "dest": None, "version": vid, "name": self.name_of(aid),
                                "status": "no-source", "note": f"{self.name_of(aid)}: " +
                                ("original not readable and " if state == "unknown" else "") + "no eligible source"}
                continue
            k += 1
            entries[aid] = self.entry_for(aid, vid, source, folder, f"ENT-{self.n:04d}-01-{k:02d}", provenance)
        record = {"plan": f"PLN-{self.n:04d}-01", "set": target, "target_kind": "full-rebuild",
                  "target_members": sorted(members), "outside": [], "reference": "approved-version", "folder": folder,
                  "entries": entries, "receipt": None, "previous": None, "attempt": 1,
                  "pending": sorted(k for k, e in entries.items() if e["status"] in PENDING)}
        self.report.attempts.append(record)
        self.execute(record)

    def recover_files(self):
        """Recovery without a prior reference: the same plan, approval and receipt; fidelity to the chosen source only."""
        self.phase = "recover"
        self.report.acknowledged.append("no-reference")
        self.add(self.case, "case", scope_id=self.scope_id, request=self.intent, status="open", opened_in="this session")
        folder = self.recovery_folder()
        plan_id = f"PLN-{self.n:04d}-01"
        entries = {}
        for k, item in enumerate(self.req["files"], start=1):
            src = norm(item["source"])
            src_root = posixpath.dirname(src)
            entry = {"entry": f"ENT-{self.n:04d}-01-{k:02d}", "source": src, "location": None, "source_root": src_root,
                     "dest": None, "version": None, "name": posixpath.basename(item["dest_name"]), "status": "not-attempted",
                     "provenance": "file chosen by the user"}
            dest, why = scope.child(folder, item["dest_name"]) if folder else (None, "no recovery folder")
            proven, seen = self.real_path_ok(src, src_root) if dest else (False, why)
            digest, seen = self.digest_in(src, src_root, fresh=True) if proven else (None, seen)
            if dest is None:
                entry.update(status="out-of-scope", note=why)
            elif digest is None:
                entry.update(status="no-source", note=f"chosen source not readable or not in scope ({seen})")
            else:
                entry.update(dest=dest, expected=digest, size=self.sizes.get(src, 0))
            entries[item["asset"]] = entry
        record = {"plan": plan_id, "set": None, "target_kind": "chosen-files",
                  "target_members": [e["name"] for e in entries.values()], "outside": [],
                  "reference": "source-fidelity", "folder": folder or self.parent, "entries": entries, "receipt": None,
                  "previous": None, "attempt": 1,
                  "pending": sorted(e["name"] for e in entries.values() if e["status"] in PENDING)}
        self.report.attempts.append(record)
        self.execute(record)

    # -- plan execution ---------------------------------------------------------------
    def plan_records(self, record: dict) -> list[tuple[str, str, dict]]:
        previous = record["previous"]
        fidelity = record["reference"] == "source-fidelity"
        kind = record.get("target_kind", "approved-set")
        goal = {"chosen-files": f"copy the files the user chose into {record['folder']}; verify fidelity to the chosen source only",
                "approved-set": f"recover the changed members of {record['set']} into {record['folder']}",
                "full-rebuild": f"rebuild every member of {record['set']} into {record['folder']}, intact members included"}[kind]
        records = [(record["plan"], "plan", {
            "case_id": self.case, "revision": record["attempt"], "reference": record["reference"],
            "target_set": record["set"], "recovery_folder": record["folder"], "goal": goal,
            "preconditions": "user approved this plan ID and digest; source digest equals expected immediately before copy; destination absent; every path inside its authorized folder",
            "success_conditions": "destination exists at the planned real path and its digest equals the expected digest; the target is complete only when every target member is in place or verified",
            "risks": "no atomic copy; sources may change; NAS approval may be declined",
            "pending": list(record["pending"]), "previous_receipt": previous["receipt"] if previous else None,
            "supersedes_plan": previous["plan"] if previous else None, "target_kind": kind,
            "target_members": list(record["target_members"]), "outside_target": list(record.get("outside", []))})]
        for key, entry in sorted(record["entries"].items()):
            if entry["status"] != "not-attempted":
                continue
            entry["planned"] = True
            records.append((entry["entry"], "plan-entry", {
                "plan_id": record["plan"], "asset_id": None if fidelity else key, "name": entry["name"],
                "version_id": entry["version"], "expected_sha256": entry["expected"], "size_bytes": entry.get("size", 0),
                "source_path": entry["source"], "destination_path": entry["dest"]}))
        return records

    def block(self, record: dict, keys: list[str], overall: str, reason: str):
        for key in keys:
            if overall == "cancelled":
                record["entries"][key]["status"] = "cancelled"
        record["overall"] = overall
        record["reason"] = reason
        record["set_complete"] = self.target_complete(record)
        self.write_receipt(record)

    def essential_cost(self, record: dict, keys: list[str]) -> tuple[int, int]:
        """Digests and bytes a recovery cannot skip: the plan twice, each source before and destination after."""
        sizes = sum(record["entries"][k].get("size", 0) for k in keys)
        return 2 + 2 * len(keys), 2 * sizes

    def execute(self, record: dict, retry: bool = False):
        entries = record["entries"]
        executable = [k for k, e in entries.items() if e["status"] == "not-attempted"]
        if not executable:
            needed = any(e["status"] in ("no-source", "out-of-scope") for e in entries.values())
            record["overall"] = "failed" if needed else "not-needed"
            record["set_complete"] = self.target_complete(record)
            record["unsaved_plan"] = self.plan_records(record)
            self.write_receipt(record)
            return
        digests, size = self.essential_cost(record, executable)
        if self.digest_count + digests > DIGEST_BUDGET or self.bytes_hashed + size > BYTE_BUDGET:
            record["unsaved_plan"] = self.plan_records(record)
            self.report.acknowledged.append("budget")
            self.block(record, executable, "failed",
                       f"the session budget left ({DIGEST_BUDGET - self.digest_count} digests, "
                       f"{BYTE_BUDGET - self.bytes_hashed} bytes) does not cover the essential checks ({digests} digests, "
                       f"{size} bytes); nothing was created or copied; the user may raise the budget")
            return
        plan_records = self.plan_records(record)
        path, fragments, reason = self.save_plan(plan_records)
        if path is None:
            self.report.acknowledged.append("plan-not-persisted")
            record["unsaved_plan"] = plan_records
            self.block(record, executable, "cancelled" if reason == "declined" else "failed",
                       f"plan not persisted: {reason}; nothing was created or copied")
            return
        digest, why = self.digest_in(path, self.memory_root, fresh=True)
        if digest is None:
            self.report.acknowledged.append("plan-not-persisted")
            self.block(record, executable, "failed", f"saved plan could not be hashed ({why}); nothing was created or copied")
            return
        record["plan_file"], record["plan_sha256"], record["fragments"] = path, digest, fragments
        record["decision"] = "granted" if self.answers.get("approve_plan", True) else "declined"
        if record["decision"] == "declined":
            self.block(record, executable, "cancelled", "the user declined the plan")
            return
        changed = self.digest_in(path, self.memory_root, fresh=True)[0] != digest or \
            any(self.digest_in(p, self.memory_root, fresh=True)[0] != d for p, d in fragments.items())
        if changed:
            self.block(record, executable, "invalidated", "the saved plan changed before execution")
            return
        error = self.prepare_folder(record, executable, retry)
        if error:
            if error == "approval_declined":
                self.block(record, executable, "cancelled", "the NAS approval for the recovery folder was declined")
            else:
                for key in executable:
                    entries[key]["status"] = "conflict-destination-exists" if error == "exists" else "failed-copy"
                    entries[key]["note"] = f"recovery folder: {error}"
                self.block(record, [], "failed", f"recovery folder: {error}")
            return
        success = "fidelity-only" if record["reference"] == "source-fidelity" else "verified"
        stop = False
        for key in executable:
            entry = entries[key]
            if stop:
                entry["status"] = "cancelled"
                continue
            entry["status"] = self.execute_entry(entry, retry, record["folder"], success)
            if entry["status"] == "cancelled":
                stop = True
        statuses = [e["status"] for e in entries.values() if e.get("planned")]
        if all(s in SUCCESS for s in statuses):
            record["overall"] = "fidelity-only" if "fidelity-only" in statuses else "verified"
        elif any(s in SUCCESS for s in statuses):
            record["overall"] = "partial"
        elif all(s == "cancelled" for s in statuses):
            record["overall"] = "cancelled"
        else:
            record["overall"] = "failed"
        if record.get("target_kind") == "full-rebuild":
            self.format_checks(record)
        record["set_complete"] = self.target_complete(record)
        self.write_receipt(record)

    def format_checks(self, record: dict):
        """Open each verified document with the document expert; other formats have no registered checker."""
        for entry in record["entries"].values():
            if entry["status"] not in VERIFIED:
                continue
            result = self.nas.open_check(entry["dest"])
            self.observe(None, "D8", "document-agent", result, result["data"] if result["ok"] else result["error"])
            if result["ok"]:
                entry["format"] = f"opened by document-agent ({result['data']['format']}, {result['data']['read']})"
            elif result["error"]["code"] == "not_supported":
                entry["format"] = f"not available: no registered expert opens {posixpath.splitext(entry['dest'])[1]} files"
            else:
                entry["format"] = "did not open"

    def prepare_folder(self, record: dict, executable: list[str], retry: bool) -> str | None:
        """D11 for a new folder (each created real path must be the planned one); D5 for a retry."""
        folder = record["folder"]
        subfolders = sorted({posixpath.dirname(record["entries"][k]["dest"]) for k in executable} - {folder},
                            key=lambda p: p.count("/"))
        if retry:
            seen = self.nas.stat(folder)
            if not seen["ok"] or seen["data"].get("realpath") != folder:
                return "folder of the previous receipt unavailable"
            needed = [p for p in subfolders if not self.nas.stat(p)["ok"]]
        else:
            needed = [folder] + subfolders
        for path in needed:
            result = self.nas.mkdir(path)
            if not result["ok"]:
                return result["error"]["code"]
            if result["data"].get("realpath") != path:
                return f"folder created at another real path ({result['data'].get('realpath')})"
        return None

    def execute_entry(self, entry: dict, retry: bool, folder: str, success: str) -> str:
        dest = entry["dest"]
        seen = self.nas.stat(dest)
        if seen["ok"]:
            if retry:
                entry["dest_digest"] = self.digest_in(dest, folder, fresh=True)[0]
                if entry["dest_digest"] == entry["expected"]:
                    return "already-present-verified"
            return "conflict-destination-exists"
        if seen["error"]["code"] != "not_found":
            entry["note"] = f"destination state unknown ({seen['error']['code']})"
            return "failed-copy"
        entry["source_before"], why = self.digest_in(entry["source"], entry["source_root"], fresh=True)
        if entry["source_before"] is None and why in scope.SCOPE_FAILURES:
            entry["note"] = f"real path of the source not proven inside its folder ({why})"
            return "out-of-scope"
        if entry["source_before"] != entry["expected"]:
            return "invalidated-source-changed"
        result = self.nas.copy(entry["source"], dest)
        if not result["ok"]:
            return "cancelled" if result["error"]["code"] == "approval_declined" else "failed-copy"
        real = result["data"].get("realpath")
        if real != dest:
            entry["real_dest"] = real
            entry["note"] = f"the NAS reported the copy at {real}" if real else "the NAS reported no real destination path"
            if real and scope.inside(real, folder):
                entry["dest_digest"] = self.digest_in(real, folder, fresh=True)[0]
            return "destination-differs"
        self.sizes[dest] = entry.get("size", 0)
        entry["dest_digest"] = self.digest_in(dest, folder, fresh=True)[0]
        if entry["dest_digest"] == entry["expected"]:
            return success
        entry["source_after"] = self.digest_in(entry["source"], entry["source_root"], fresh=True)[0]
        if entry["source_after"] != entry["source_before"]:
            self.open_item(entry["entry"], "source changed during recovery", "a stable source")
            return "invalidated-source-changed"
        return "failed-verification"

    def set_complete(self, set_id: str, entries: dict) -> bool:
        for aid, vid in self.mem.sets[set_id]["members"].items():
            state = self.report.states.get(aid)
            in_place = state in ("intact", "moved") and self.mem.assets[aid]["current"] == vid
            if not in_place and entries.get(aid, {}).get("status") not in VERIFIED:
                return False
        return True

    def target_complete(self, record: dict) -> bool | None:
        """Whether the requested target is complete: None when there is no approved reference to judge it."""
        if record["reference"] == "source-fidelity" or not record.get("set"):
            return None
        if record.get("target_kind") == "full-rebuild":
            return all(record["entries"].get(a, {}).get("status") in VERIFIED for a in record["target_members"])
        return self.set_complete(record["set"], record["entries"])

    @staticmethod
    def entry_checks(record: dict, entry: dict) -> dict[str, str]:
        """Byte integrity, membership in the approved version and format check, kept apart."""
        dest, before, expected = entry.get("dest_digest"), entry.get("source_before"), entry.get("expected")
        checks = {"bytes": "not checked" if dest is None or before is None else
                  "equal to the source digest observed before copying" if dest == before else
                  "differs from the source digest observed before copying"}
        if record["reference"] == "source-fidelity":
            checks["version"] = "no prior reference: not checked"
        else:
            checks["version"] = "not checked" if dest is None else \
                f"equal to approved version {entry['version']}" if dest == expected else f"differs from approved version {entry['version']}"
        checks["format"] = entry.get("format", "not checked")
        if entry.get("provenance"):
            checks["provenance"] = entry["provenance"]
        return checks

    def write_receipt(self, record: dict):
        plan_id = record["plan"]
        if plan_id is None:
            return
        receipt_id = plan_id.replace("PLN", "RCP", 1)
        record["receipt"] = receipt_id
        fidelity = record["reference"] == "source-fidelity"
        extra = list(record.get("unsaved_plan", []))
        extra.append((plan_id.replace("PLN", "APR", 1), "approval", {
            "plan_id": plan_id, "plan_sha256": record.get("plan_sha256"),
            "decision": record.get("decision", "not-requested"), "statement": "user reply in session"}))
        extra.append((receipt_id, "receipt", {
            "plan_id": plan_id, "plan_sha256": record.get("plan_sha256"), "overall": record["overall"],
            "reference": record["reference"], "set_complete": record.get("set_complete"),
            "coverage": "see case records", "reason": record.get("reason"),
            "pending": [e["name"] if fidelity else k for k, e in sorted(record["entries"].items()) if e["status"] not in SUCCESS],
            "outside_target": list(record.get("outside", []))}))
        prefix = plan_id.replace("PLN", "REN", 1)
        for n, (key, entry) in enumerate(sorted(record["entries"].items()), start=1):
            extra.append((f"{prefix}-{n:02d}", "receipt-entry", {
                "receipt_id": receipt_id, "entry_id": entry["entry"] if entry.get("planned") else None,
                "asset_id": None if fidelity else key, "version_id": entry.get("version"), "status": entry["status"],
                "destination_path": entry.get("real_dest") or entry.get("dest"),
                "source_sha256_before": entry.get("source_before"), "destination_sha256": entry.get("dest_digest"),
                "source_sha256_after": entry.get("source_after"), "note": entry.get("note", ""),
                "name": entry["name"], "source_path": entry.get("source"), "checks": self.entry_checks(record, entry)}))
        self.checkpoint(extra)

    # -- learning ------------------------------------------------------------------------
    def closed_case(self) -> str | None:
        """The newest case with a persisted receipt; the user confirms its outcome in this session."""
        records = self.session.records
        cases = sorted({records[r["plan_id"]]["case_id"] for r in records.values()
                        if r["type"] == "receipt" and r["plan_id"] in records})
        wanted = self.req["learn"].get("case")
        if not cases or (wanted and wanted not in cases):
            self.open_item(wanted or "learn", "no such case with a persisted receipt", "a recovery whose receipt was saved")
            return None
        case = wanted or cases[-1]
        if not self.answers.get("confirm_outcome", True):
            self.open_item(case, "the user did not confirm the outcome", "the user confirmation of the outcome")
            return None
        original = self.session.history.get(case, {})
        self.add(self.next_id("STM"), "statement", text=f"The outcome of {case} is confirmed: "
                 f"{self.req['learn'].get('outcome', 'as shown in its receipt')}.", given_in="this session",
                 **{"class": "user-declared"})
        self.add(f"{case}-{self.n:04d}", "case", scope_id=original.get("scope_id", self.scope_id),
                 request=original.get("request", "unknown"), status="closed",
                 opened_in=original.get("opened_in", "unknown"), supersedes=case)
        return case

    def replay_cases(self, policy: dict, cases: dict[str, dict]) -> list[dict]:
        from .policy import fixture_of, replay  # noqa: PLC0415 - policy imports this module
        results = []
        for tid, record in sorted(cases.items()):
            case = fixture_of(record)
            outcome = replay(policy, case) if case else {"passed": False, "problems": ["no executable facts"]}
            results.append({"case": tid, "split": record["split"], "kind": record["kind"], "passed": outcome["passed"],
                            "problems": outcome["problems"]})
        return results

    def read_holdout(self) -> dict[str, dict]:
        """After the freeze: list the memory folder again (D3) and read the holdout files the user added (D4)."""
        from .persistence import list_memory  # noqa: PLC0415
        listing = list_memory(self.nas, self.memory_root)
        self.listings += listing.listings
        found = {}
        for path, real in listing.usable.items():
            known = self.session.files.get(path)
            if "CERBERO-TH-" not in posixpath.basename(path) or (known and not known["reason"].startswith("holdout file: hashed")):
                continue
            read = self.nas.cat(path)
            if not read["ok"] or read["data"].get("realpath") != real or read["data"].get("partial"):
                self.open_item(path, "holdout file not read completely", "a complete read of the holdout file")
                continue
            try:
                bundle = parse(read["data"]["text"])
            except ValueError as exc:
                self.open_item(path, f"holdout file unparseable ({exc})", "a valid holdout file")
                continue
            if validate(bundle["records"]):
                self.open_item(path, "holdout file has invalid records", "a valid holdout file")
                continue
            digest, _ = self.digest_in(path, self.memory_root, fresh=True)
            self.session.files[path] = {"bundle_id": bundle["header"]["bundle_id"], "sha256": digest,
                                        "status": "current" if digest else "needs-review",
                                        "reason": "holdout file read after the freeze, confirmed by the user"}
            found.update({rid: r for rid, r in bundle["records"].items() if r["type"] == "test-case"})
        return found

    def learn(self):
        """Mode Learn: closed case, candidate, counterexample, freeze, holdout, approval, persistence."""
        from .persistence import parse_effects  # noqa: PLC0415
        spec = self.req["learn"]
        self.add(self.case, "case", scope_id=self.scope_id, request="learn", status="open", opened_in="this session")
        case = self.closed_case()
        self.report.learning = {"case": case, "candidates": []}
        if case is None:
            self.checkpoint()
            return
        tests = {rid: r for rid, r in self.session.history.items() if r["type"] == "test-case"}
        development = {rid: r for rid, r in tests.items() if r["split"] == "development"}
        if any(r["split"] == "holdout" for r in tests.values()):
            self.open_item("holdout", "holdout cases were read before the freeze; they cannot serve as holdout",
                           "new holdout cases from the user")
        for candidate in spec["candidates"]:
            effect, violations, unsupported = parse_effects(candidate["effect"])
            pid = self.next_id("POL")
            policy = {"id": pid, "version": candidate["version"], "effect": effect}
            fields = {"version": candidate["version"], "condition": candidate["condition"], "scope": candidate["scope"],
                      "effect": list(candidate["effect"]), "motivated_by": case, "drafted_from": sorted(development),
                      "rule_sha256": None, "approval": None}
            row = {"policy": pid, "version": candidate["version"], "effect": list(candidate["effect"])}
            self.report.learning["candidates"].append(row)
            if violations or unsupported:
                self.add(pid, "policy", status="rejected", **fields)
                row.update(result="rejected-by-guard", guard=violations + [f"not implemented: {u}" for u in unsupported])
                continue
            dev = self.replay_cases(policy, development)
            row["development"] = dev
            if not all(r["passed"] for r in dev):
                self.add(pid, "policy", status="rejected", **fields)
                self.add(self.next_id("EVL"), "evaluation", policy_id=pid, rule_sha256=None, verdict="rejected",
                         cases=[f"{r['case']} {r['split']} {r['kind']} {'pass' if r['passed'] else 'fail'}" for r in dev])
                row["result"] = "rejected: " + ", ".join(r["case"] for r in dev if not r["passed"]) + " failed"
                continue
            path, reason = self.save_mandatory([(pid, "policy", {**fields, "status": "candidate"})])
            rule = self.digest_in(path, self.memory_root, fresh=True)[0] if path else None
            if rule is None:
                self.open_item(pid, f"candidate not frozen ({reason if path is None else 'not hashed'})", "a persisted, hashed candidate")
                row["result"] = "not frozen"
                break
            row.update(frozen_file=path, rule_sha256=rule)
            read_before = any(op == "cat" and "CERBERO-TH-" in args.get("path", "") for op, args, _ in self.nas.log)
            if self.on_freeze:
                self.on_freeze(self.nas)
            holdout = self.read_holdout()
            row["holdout_unseen_before_freeze"] = not read_before
            kinds = {r["kind"] for r in list(development.values()) + list(holdout.values())}
            if not holdout or not {"origin", "similar", "counterexample", "insufficient"} <= kinds:
                self.open_item(pid, "a case kind or a holdout case is missing; the rule stays candidate", "a test case from the user")
                row["result"] = "candidate: cases missing"
                break
            held = self.replay_cases(policy, holdout)
            row["holdout"] = held
            passed = all(r["passed"] for r in dev + held)
            evaluation = self.next_id("EVL")
            self.add(evaluation, "evaluation", policy_id=pid, rule_sha256=rule, verdict="evaluated" if passed else "rejected",
                     cases=[f"{r['case']} {r['split']} {r['kind']} {'pass' if r['passed'] else 'fail'}" for r in dev + held])
            if not passed:
                self.add(self.next_id("POL"), "policy", status="rejected", supersedes=pid, **{**fields, "rule_sha256": rule})
                row["result"] = "rejected on holdout"
                continue
            if not self.answers.get("approve_policy", True):
                row["result"] = "evaluated; not approved by the user"
                break
            active = self.next_id("POL")
            self.add(active, "policy", status="active", supersedes=pid,
                     **{**fields, "rule_sha256": rule, "approval": spec["approval_words"]})
            saved = self.checkpoint()
            row.update(result="active" if saved else "approved but not persisted: not active", record=active,
                       evaluation=evaluation)
            break
        self.checkpoint()

    def retire(self):
        """A recorded user decision retires an active policy; the record history is kept."""
        self.add(self.case, "case", scope_id=self.scope_id, request="retire policy", status="open", opened_in="this session")
        wanted = self.req.get("policy")
        active = [pid for pid, r in sorted(self.session.records.items())
                  if r["type"] == "policy" and r["status"] == "active" and wanted in (None, pid, r["version"])]
        self.report.learning = {"retired": []}
        if not active:
            self.open_item(str(wanted), "no active policy to retire", "the ID of an active policy")
        for pid in active:
            record = self.session.records[pid]
            keep = {k: record[k] for k in ("version", "condition", "scope", "effect", "motivated_by", "drafted_from",
                                           "rule_sha256")}
            self.add(self.next_id("POL"), "policy", status="retired", supersedes=pid,
                     approval=self.req.get("decision", "user decision in this session"), **keep)
            self.report.learning["retired"].append(pid)
        self.checkpoint()

    # -- index snapshot -------------------------------------------------------------------
    def finish(self):
        """Index snapshot: every live file with its digest, carried forward from the loaded index.

        A snapshot larger than one bundle is saved in parts IDX-n-01..k; each part after the first lists the
        previous part with the digest D7 returned, so the newest part binds the whole chain.
        """
        if not self.persist_enabled:
            return
        if self.pending and self.saved:
            self.checkpoint()
        if not self.saved:
            return
        rows = [(path, info["bundle_id"], info["sha256"], info["status"]) for path, info in sorted(self.session.files.items())]
        for path, bundle_id in self.saved:
            digest, _ = self.digest_in(path, self.memory_root, fresh=True)
            rows.append((path, bundle_id, digest, "current" if digest else "needs-review"))
        items = [(f"IDX-{self.n:04d}-00-{n:04d}", "index-entry",
                  {"file": path, "bundle_id": bundle_id or "unknown", "sha256": digest if status != "needs-review" else None,
                   "status": status}) for n, (path, bundle_id, digest, status) in enumerate(rows, start=1)]
        widest = max(self.record_bytes(i) for i in items) + 16
        header = len(Bundle("IDX-0000-00", case_id=self.case, scope_id=self.scope_id).render().encode("utf-8"))
        per_part = max(1, (MAX_BUNDLE_BYTES - header - widest) // widest)
        groups = [rows[i:i + per_part] for i in range(0, len(rows), per_part)]
        parts = []
        for k, group in enumerate(groups, start=1):
            index_id = f"IDX-{self.n:04d}-{k:02d}"
            bundle = Bundle(index_id, case_id=self.case, scope_id=self.scope_id)
            extra = [(p, b, d, "current" if d else "needs-review") for p, b, d in parts[-1:]]
            for n, (path, bundle_id, digest, status) in enumerate(group + extra, start=1):
                bundle.add(f"{index_id}-{n:04d}", "index-entry", file=path, bundle_id=bundle_id or "unknown",
                           sha256=digest if status != "needs-review" else None, status=status)
            text = bundle.render()
            result = self.nas.save_text(self.memory_root, f"CERBERO-{index_id}", text)
            data = result["data"] if result["ok"] else {}
            out = data.get("outputFile")
            if not out or data.get("verified") is not True or data.get("contentBytes") != len(text.encode("utf-8")) \
                    or scope.containment(out, self.memory_root) != "inside":
                self.report.acknowledged.append("index-not-persisted")
                self.report.open_items.append(f"{index_id}: index snapshot not persisted; files of this session will need review")
                return
            self.report.persisted.append(out)
            self.sizes[out] = data["contentBytes"]
            if k < len(groups):
                digest, _ = self.digest_in(out, self.memory_root, fresh=True)
                parts.append((out, index_id, digest))

VARIANTS = {"A": VariantA, "B": VariantB, "C": VariantC}


def run_variant(key: str, scenario, policies=()) -> tuple[Report, object]:
    """Run one variant on its own state. B and C load memory only from bundles saved by a Baseline session."""
    from .pipeline import run  # noqa: PLC0415 - pipeline imports this module
    return run(key, scenario, policies)
