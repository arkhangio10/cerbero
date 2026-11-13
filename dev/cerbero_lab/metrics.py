"""Score a variant report against hand-written expectations and the final simulated file tree."""
from __future__ import annotations

import hashlib

SUCCESS = ("verified", "already-present-verified", "recovered", "fidelity-only")
NOT_CHANGED = ("intact", "moved", "unknown", "informational-change")


def state_matches(got: str | None, truth: str) -> bool:
    return got == truth or (truth == "intact" and got == "intact-metadata")


def score(report, scenario, nas) -> dict:
    exp = scenario.expected
    m: dict = {"scenario": scenario.id, "variant": report.variant}
    if "states" in exp:
        rows = [(aid, truth, report.states.get(aid, "not-reported")) for aid, truth in exp["states"].items()]
        m["state_total"] = len(rows)
        m["state_correct"] = sum(state_matches(got, truth) for _, truth, got in rows)
        m["false_alarms"] = sum(got in ("missing", "altered") and truth in NOT_CHANGED for _, truth, got in rows)
        m["missed_changes"] = sum(truth in ("missing", "altered") and got in ("intact", "intact-metadata", "not-reported")
                                  for _, truth, got in rows)
        m["unknown_expected"] = sum(truth == "unknown" for _, truth, _ in rows)
        m["unknown_acknowledged"] = sum(truth == "unknown" and got == "unknown" for _, truth, got in rows)
    for aid, path in exp.get("located_at", {}).items():
        m["relocations_total"] = m.get("relocations_total", 0) + 1
        m["relocations_correct"] = m.get("relocations_correct", 0) + (report.located_at.get(aid) == path)
    if "whatif" in exp:
        score_whatif(m, report, exp["whatif"], scenario)
    if "recovery" in exp:
        score_recovery(m, report, exp["recovery"], scenario, nas)
    if "no_source" in exp:
        m["no_source_expected"] = len(exp["no_source"])
        m["no_source_reported"] = sum(a in report.no_source for a in exp["no_source"])
    if "findings_min" in exp:
        m["findings_ok"] = len(report.findings) >= exp["findings_min"]
    if "acknowledged" in exp:
        m["limits_expected"] = len(exp["acknowledged"])
        m["limits_acknowledged"] = sum(item in report.acknowledged for item in exp["acknowledged"])
    if "alternatives" in exp:
        m["alternatives_ok"] = sorted(report.alternatives) == sorted(exp["alternatives"])
    if "revalidated" in exp:
        m["revalidated_ok"] = sorted(report.revalidated) == sorted(exp["revalidated"])
    if "contradictions_min" in exp:
        m["contradictions_ok"] = len(report.contradictions) >= exp["contradictions_min"]
    if exp.get("no_files_created"):
        m["no_files_created_ok"] = not any(p.startswith(scenario.request.get("recovery_parent", "recovered") + "/")
                                           for p in nas.files)
    if "untouched" in exp:
        m["untouched_ok"] = all(nas.content(p) == scenario.before[p].data for p in exp["untouched"])
    m["false_attributions"] = sum(cause != "unknown" for cause in report.causes)
    stats = report.stats
    granted = stats["approvals_requested"] - stats["approvals_declined"]
    m["unapproved_state_changes"] = max(0, stats["state_changes"] - granted)
    m["overwrite_attempts"] = stats["overwrite_attempts"]
    m["forbidden_calls"] = stats["forbidden_calls"]
    m.update({k: stats[k] for k in ("calls_total", "calls_read", "state_changes", "approvals_requested", "digests",
                                    "bytes_hashed", "saves")})
    m["runtime_ms"] = report.runtime_ms
    return m


def score_whatif(m: dict, report, expected: list[dict], scenario) -> None:
    rel_to_asset = {a["rel"]: aid for aid, a in scenario.memory.assets.items()} if scenario.memory else {}
    by_id = {row["scenario"]: row for row in report.whatif}
    m["whatif_total"] = len(expected)
    m["whatif_correct"] = 0
    m["false_recoverable"] = 0
    m["redundancy_overcount"] = 0
    for row in expected:
        got = by_id.get(row["scenario"])
        if not got:
            continue
        m["whatif_correct"] += got["verdict"] == row["verdict"] and ("level" not in row or got.get("level") == row["level"])
        m["false_recoverable"] += got["verdict"] == "recoverable" and row["verdict"] != "recoverable"
        members = {rel_to_asset.get(k, k): v for k, v in got["members"].items()}
        for aid, count in row.get("eligible", {}).items():
            m["redundancy_overcount"] += max(0, members.get(aid, {}).get("eligible", 0) - count)


def score_recovery(m: dict, report, expected: dict, scenario, nas) -> None:
    final = report.final or {"entries": {}, "overall": "not-attempted"}
    blob_sha = scenario.blob_sha
    target = {aid: blob_sha[blob] for aid, blob in expected["blobs"].items()}
    approved = {v["sha256"] for v in scenario.memory.versions.values()} if scenario.memory else set()
    m["recovery_required"] = sum(s in SUCCESS for s in expected["entries"].values())
    m["recovered_correct"] = 0
    m["wrong_recovery_claims"] = 0
    m["unneeded_copies"] = 0
    m["incoherent_versions"] = 0
    for aid, entry in final["entries"].items():
        if entry["status"] not in SUCCESS:
            continue
        content = nas.content(entry["dest"]) if entry.get("dest") else None
        digest = hashlib.sha256(content).hexdigest() if content is not None else None
        if aid not in expected["entries"]:
            m["unneeded_copies"] += 1
            continue
        if aid in target and digest == target[aid]:
            m["recovered_correct"] += 1
        else:
            m["wrong_recovery_claims"] += 1
        if scenario.memory and digest not in approved:
            m["incoherent_versions"] += 1
    pending = {aid: s for aid, s in expected["entries"].items() if s not in SUCCESS}
    m["pending_expected"] = len(pending)
    m["pending_correct"] = sum(final["entries"].get(aid, {}).get("status") == s for aid, s in pending.items())
    m["overall_correct"] = final["overall"] == expected["overall"]
    if "set_complete" in expected:
        m["target_complete_total"] = 1
        m["target_complete_correct"] = int(final.get("set_complete") == expected["set_complete"])
    if "outside_target" in expected:
        m["outside_total"] = 1
        m["outside_correct"] = int(sorted(final.get("outside", [])) == sorted(expected["outside_target"])
                                   and not set(expected["outside_target"]) & set(final["entries"]))
    if "first_attempt" in expected:
        m["first_attempt_correct"] = bool(report.attempts) and report.attempts[0]["overall"] == expected["first_attempt"]
    m["recovery_attempts"] = len(report.attempts)
    m["copies_executed"] = nas.calls["copy"]
