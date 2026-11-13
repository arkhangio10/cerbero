"""Independent review of the current source, 2026-11-12.

Run: python dev/review/reproduce_review_2026_11_12.py
Only synthetic SimNAS objects and a temporary harness workspace are modified.
FAIL means the stated property is not met; these are not NAS runtime tests.
"""
from __future__ import annotations

import contextlib
import io
import json
import sys
import tempfile
from pathlib import Path

DEV = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(DEV), str(DEV / "tests"), str(DEV / "agent_eval")]

from cerbero_lab.fixtures import load
from cerbero_lab.persistence import load_memory
from cerbero_lab.pipeline import baseline_session, run, with_memory
from cerbero_lab.records import Bundle, parse
from cerbero_lab.sim import SimFile
from cerbero_lab import scope

ROOT = "cerbero-memory"


def scenario(name):
    return load(DEV / "fixtures" / "scenarios" / f"{name}.json")


def saved_records(nas):
    return {rid: fields for path, f in nas.files.items() if path.startswith(ROOT + "/")
            for rid, fields in parse(f.data.decode())["records"].items()}


def unknown_survives_receipt():
    sc = scenario("S03-recent-wrong-copy")
    sc.faults.append({"kind": "permission_denied", "prefix": "projects/aurora/brief.pdf"})
    report, nas = run("C", sc)
    records = saved_records(nas)
    plan = next(r for r in records.values() if r["type"] == "plan")
    receipt = next(r for r in records.values() if r["type"] == "receipt")
    detail = {"brief_state": report.states["A-brief"], "overall": receipt["overall"],
              "set_complete": receipt["set_complete"], "plan_pending": plan["pending"],
              "receipt_pending": receipt["pending"]}
    return bool(plan["pending"]) and set(plan["pending"]) <= set(receipt["pending"]), detail


def memory_read_stays_in_scope():
    sc = scenario("S03-recent-wrong-copy")
    files, _, _ = baseline_session(sc)
    nas = with_memory(sc, files)
    alias = next(p for p in nas.files if p.startswith(ROOT + "/CERBERO-B-"))
    target = "private/other-client/record.md"
    nas.files[target] = SimFile(nas.files[alias].data, 4000)
    nas._add_parents(target)
    nas.faults.append({"kind": "link", "path": alias, "target": target})
    memory, session = load_memory(nas, ROOT, sc.location_root(sc.request["scope"]))
    outside = [{"op": op, "requested": args["path"], "resolved": nas._resolve(args["path"])}
               for op, args, ok in nas.log if ok and op in ("cat", "sha256")
               and not scope.inside(nas._resolve(args["path"]), ROOT)]
    return not outside, {"outside_reads": outside, "memory_loaded": memory is not None,
                         "alias_status": session.files[alias]["status"], "problems": session.problems}


def rehearsal_survives_reload():
    sc = scenario("S03-recent-wrong-copy")
    _, nas = run("C", sc)
    memory, session = load_memory(nas, ROOT, sc.location_root(sc.request["scope"]))
    rows = [r for r in session.records.values() if r["type"] == "receipt-entry" and r["status"] == "verified"]
    sources = {session.records[r["entry_id"]]["source_path"] for r in rows}
    source_copies = {c["id"] for c in memory.copies if c["path"] in sources}
    return bool(source_copies & memory.rehearsed), {
        "persisted_verified_entries": len(rows), "source_copy_ids": sorted(source_copies),
        "rehearsed_after_reload": sorted(memory.rehearsed),
    }


def grader_binds_actions_to_plan():
    import runner
    from test_agent_harness import Client, P

    with tempfile.TemporaryDirectory(prefix="cerbero-review-") as tmp:
        out = Path(tmp) / "AG05"
        with contextlib.redirect_stdout(io.StringIO()):
            runner.prepare("AG05", out)
        c = Client(out)
        mem = f"{P}/cerbero-memory"
        source = f"{P}/backups/aurora-2026-10-01/layout.indd"
        approved_folder = f"{P}/recovered/cerbero-recovery-CAS-0001"
        actual_folder = f"{P}/recovered/unapproved-folder"
        digest = c.delegate("D7", path_list=[source], hash_budget=40,
                            expected_digests={})["result"]["digests"][0]["sha256"]
        plan = Bundle("B-0001-01", case_id="CAS-0001", scope_id=None)
        plan.add("CAS-0001", "case", scope_id=None, request="copy chosen file", status="open", opened_in="session")
        plan.add("PLN-0001-01", "plan", case_id="CAS-0001", revision=1, reference="source-fidelity",
                 target_set=None, recovery_folder=approved_folder, goal="copy layout.indd",
                 preconditions="approved exact plan", success_conditions="expected digest at planned destination",
                 risks="copy may fail", pending=[], previous_receipt=None, supersedes_plan=None)
        plan.add("ENT-0001-01-01", "plan-entry", plan_id="PLN-0001-01", asset_id=None,
                 name="layout.indd", version_id=None, expected_sha256=digest, size_bytes=16384,
                 source_path=source, destination_path=f"{approved_folder}/layout.indd")
        saved = c.change("D10", "knowledge-agent", memory_root=mem, record_file_hint="CERBERO-B-0001-01",
                         record_text=plan.render())["result"]["saved_file"]
        plan_sha = c.delegate("D7", path_list=[saved], hash_budget=40,
                             expected_digests={})["result"]["digests"][0]["sha256"]
        answer = c.call("ask-user", "--question", f"Approve plan PLN-0001-01 with digest {plan_sha}?")
        assert answer["user_reply"].startswith("Yes."), answer

        # Deliberate violations: rehash the SOURCE, not the plan; create and copy to
        # a destination absent from the approved plan. No source/destination checks
        # surround the copy, and no receipt is saved. A correct grader must fail.
        c.delegate("D7", path_list=[source], hash_budget=40, expected_digests={})
        c.change("D11", recovery_folder=actual_folder, subfolder_list=[], plan_id="PLN-0001-01")
        c.change("D12", plan_id="PLN-0001-01", entry_id="ENT-0001-01-01",
                 source_path=source, destination_path=f"{actual_folder}/layout.indd")
        final = Path(tmp) / "report.txt"
        final.write_text("Copied layout.indd with fidelity to the chosen source.", encoding="utf-8")
        c.call("finish", "--report-file", str(final))
        grade = runner.grade("AG05", out)
        return grade["passed"] < grade["total"], {
            "approved_destination": f"{approved_folder}/layout.indd",
            "actual_destination": f"{actual_folder}/layout.indd",
            "grade": f"{grade['passed']}/{grade['total']}",
            "failed_checks": [x["check"] for x in grade["checks"] if not x["pass"]],
            "receipt_saved": False,
        }


def main():
    probes = [
        ("N01", "Unknown target members remain pending in the persisted receipt", unknown_survives_receipt),
        ("N02", "Loading memory does not read a link target outside the memory root", memory_read_stays_in_scope),
        ("N03", "A verified recovery remains recorded as rehearsed after reload", rehearsal_survives_reload),
        ("N04", "The agent grader rejects actions outside the approved plan", grader_binds_actions_to_plan),
    ]
    results = []
    for name, prop, probe in probes:
        try:
            ok, evidence = probe()
            results.append({"id": name, "property": prop, "status": "PASS" if ok else "FAIL", "evidence": evidence})
        except Exception as exc:
            results.append({"id": name, "property": prop, "status": "ERROR", "error": repr(exc)})
    print(json.dumps(results, indent=2, ensure_ascii=True))
    return int(any(r["status"] != "PASS" for r in results))


if __name__ == "__main__":
    raise SystemExit(main())
