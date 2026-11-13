"""Policy lifecycle from references/policy-learning.md: guard, replay, holdout freeze, approval.

run_learning() checks the lifecycle mechanics on the fixture policies in one process. The persisted lifecycle
(closed case, freeze, holdout, approval, reload in a new session, retirement) is VariantC.learn and .retire,
with activation decided only from saved records by persistence.active_policies.
"""
from __future__ import annotations

import hashlib
import json
import re

from .fixtures import FIXTURES, Scenario, load, load_all
from .variants import ALLOWED_EFFECTS, FORBIDDEN_EFFECTS, VariantC, rel_inside
REQUIRED_KINDS = {"origin", "similar", "counterexample", "insufficient"}


def rule_digest(policy: dict) -> str:
    frozen = {k: policy[k] for k in ("id", "version", "condition", "scope", "text", "effect")}
    return hashlib.sha256(json.dumps(frozen, sort_keys=True).encode()).hexdigest()


def guard(policy: dict, cases: list[Scenario]) -> list[str]:
    violations = []
    for key in policy["effect"]:
        if key in FORBIDDEN_EFFECTS:
            violations.append(FORBIDDEN_EFFECTS[key])
        elif key not in ALLOWED_EFFECTS:
            violations.append(f"I1 unknown effect {key}")
    lowered: set[str] = set()
    for case in cases:
        memory = case.memory
        named = set(case.request.get("copy_locations", []))
        location = policy["effect"].get("add_search_location")
        if location and location not in named:
            violations.append(f"I2 searches a location the user did not name ({location})")
        protected = {a for s in memory.sets.values() for a in s["members"]}
        protected |= {a for a, asset in memory.assets.items() if asset["importance"] == "critical"}
        for prefix in policy["effect"].get("informational", []):
            lowered |= {a for a in protected if rel_inside(memory.assets[a]["rel"], prefix)}
    if lowered:
        violations.append(f"I6 lowers review of critical or set-member assets ({len(lowered)} across the cases)")
    return sorted(set(violations))


def check_expected(report, expected: dict) -> list[str]:
    problems = []
    for aid, state in expected.get("states", {}).items():
        got = report.states.get(aid)
        if got != state and not (state == "intact" and got == "intact-metadata"):
            problems.append(f"{aid}: expected {state}, got {got}")
    for aid in expected.get("at_risk_includes", []):
        if aid not in report.at_risk:
            problems.append(f"{aid} should be at risk")
    for aid in expected.get("at_risk_excludes", []):
        if aid in report.at_risk:
            problems.append(f"{aid} should not be at risk")
    if len(report.open_items) < expected.get("open_items_min", 0):
        problems.append("missing open items")
    for item in expected.get("acknowledged", []):
        if item not in report.acknowledged:
            problems.append(f"limit not acknowledged: {item}")
    return problems


def replay(policy: dict | None, case: Scenario) -> dict:
    from .pipeline import run  # noqa: PLC0415 - avoids a cycle through variants
    report, _ = run("C", case, policies=[policy] if policy else ())
    problems = check_expected(report, case.expected)
    return {"case": case.id, "split": case.raw["case"]["split"], "kind": case.raw["case"]["kind"],
            "passed": not problems, "problems": problems, "policy_effects": sorted(report.policy_effects)}


def evaluate(policy: dict, cases: list[Scenario]) -> dict:
    result = {"policy": f"{policy['id']}-{policy['version']}", "guard": guard(policy, cases)}
    if result["guard"]:
        result["status"] = "rejected-by-guard"
        return result
    development = [c for c in cases if c.raw["case"]["split"] == "development"]
    holdout = [c for c in cases if c.raw["case"]["split"] == "holdout"]
    dev_ids = {c.id for c in development}
    leaked = set(policy.get("drafted_from", [])) - dev_ids
    if leaked:
        raise ValueError(f"policy drafted from non-development cases: {sorted(leaked)}")
    kinds = {c.raw["case"]["kind"] for c in cases}
    if not REQUIRED_KINDS <= kinds or not holdout:
        result["status"] = "not-evaluable"
        result["missing_kinds"] = sorted(REQUIRED_KINDS - kinds) + ([] if holdout else ["holdout"])
        return result
    result["development"] = [replay(policy, c) for c in development]
    result["rule_sha256"] = rule_digest(policy)
    result["holdout"] = [replay(policy, c) for c in holdout]
    if rule_digest(policy) != result["rule_sha256"]:
        raise ValueError("rule changed after freeze")
    passed = all(r["passed"] for r in result["development"] + result["holdout"])
    result["status"] = "evaluated" if passed else "rejected"
    return result


def approve(evaluation: dict, user_approves: bool) -> str:
    if evaluation["status"] != "evaluated":
        return evaluation["status"]
    return "active" if user_approves else "evaluated"


def fixture_of(test_record: dict) -> Scenario | None:
    """The executable facts of a test-case record: the synthetic fixture its source names, if any."""
    match = re.search(r"\bfixture (\S+)$", test_record.get("source", ""))
    paths = [FIXTURES / folder / f"{match.group(1)}.json" for folder in ("policy_cases", "policy_cases_holdout2")] if match else []
    return next((load(path) for path in paths if path.exists()), None)


def test_case_bundles() -> dict[str, bytes]:
    """Synthetic policy test cases as two bundles, one per split, so holdout files can stay unread."""
    from .records import Bundle  # noqa: PLC0415
    bundles = {"development": Bundle("TD-0000-01", case_id=None, scope_id=None),
               "holdout": Bundle("TH-0000-01", case_id=None, scope_id=None)}
    for n, case in enumerate(load_all("policy_cases"), start=1):
        meta = case.raw["case"]
        bundles[meta["split"]].add(f"TST-0000-{n:04d}", "test-case", kind=meta["kind"], split=meta["split"],
                                   facts=meta["facts"], expected=meta["expected_text"],
                                   source=f"synthetic test data authorized by the user; fixture {case.id}")
    return {f"CERBERO-{b.header['bundle_id']}.md": b.render().encode("utf-8") for b in bundles.values()}


def second_holdout_bundle() -> dict[str, bytes]:
    """New holdout cases for a revision drafted after the first holdout was read: never shown before that freeze."""
    from .records import Bundle  # noqa: PLC0415
    bundle = Bundle("TH-0000-02", case_id=None, scope_id=None)
    for n, case in enumerate(load_all("policy_cases_holdout2"), start=len(load_all("policy_cases")) + 1):
        meta = case.raw["case"]
        bundle.add(f"TST-0000-{n:04d}", "test-case", kind=meta["kind"], split=meta["split"], facts=meta["facts"],
                   expected=meta["expected_text"], source=f"synthetic test data authorized by the user; fixture {case.id}")
    return {"CERBERO-TH-0000-02.md": bundle.render().encode("utf-8")}


def run_learning() -> dict:
    data = json.loads((FIXTURES / "policies.json").read_text(encoding="utf-8"))
    cases = load_all("policy_cases")
    baseline = [replay(None, c) for c in cases]
    outcomes = {}
    for policy in data["candidates"]:
        evaluation = evaluate(policy, cases)
        evaluation["final_status"] = approve(evaluation, user_approves=True)
        outcomes[evaluation["policy"]] = evaluation
    return {"baseline_without_policy": baseline, "candidates": outcomes, "expected": data["expected"]}
