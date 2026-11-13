"""Independent review probes. Only synthetic SimNAS objects are modified.

Run from the repository root: python dev/review/reproduce_review.py
FAIL means the stated safety/correctness property does not hold in the current lab.
This is not a NAS exploit or a UGOS runtime test. No production source or fixture is edited.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

DEV = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(DEV))

from cerbero_lab.fixtures import load
from cerbero_lab.mapping import evaluate_set
from cerbero_lab.records import Bundle, parse
from cerbero_lab.sim import SimFile, inside
from cerbero_lab.variants import VariantC, run_variant

SCENARIOS = DEV / "fixtures" / "scenarios"


def plan_save_declined():
    sc = load(SCENARIOS / "S03-recent-wrong-copy.json")
    nas = sc.build_nas()
    nas.approve = lambda op, args: op != "save_text"
    report = VariantC(sc, nas, sc.memory).run()
    detail = {"overall": (report.final or {}).get("overall"),
              "copies": nas.calls["copy"], "mkdir": nas.calls["mkdir"],
              "persisted": report.persisted}
    return nas.calls["copy"] == 0 and nas.calls["mkdir"] == 0, detail


def no_reference_rejected_plan():
    sc = load(SCENARIOS / "S13-no-prior-reference.json")
    sc.raw.setdefault("answers", {})["approve_plan"] = False
    report, nas = run_variant("C", sc)
    detail = {"overall": (report.final or {}).get("overall"),
              "copies": nas.calls["copy"], "plan": (report.final or {}).get("plan")}
    return nas.calls["copy"] == 0 and nas.calls["mkdir"] == 0, detail


def destination_scope():
    sc = load(SCENARIOS / "S03-recent-wrong-copy.json")
    sc.memory.assets["A-layout"]["rel"] = "../../outside/escaped-layout.indd"
    nas = sc.build_nas()
    report = VariantC(sc, nas, sc.memory).run()
    root = (report.final or {}).get("folder") or "recovered"
    calls = [{"args": args, "success": success} for op, args, success in nas.log if op == "copy"]
    escaped = [item for item in calls if not inside(item["args"]["dst"], root)]
    return not escaped, {"overall": (report.final or {}).get("overall"),
                         "copy_calls": calls, "escaped_exists": nas.exists("outside/escaped-layout.indd")}


def source_scope():
    sc = load(SCENARIOS / "S03-recent-wrong-copy.json")
    nas = sc.build_nas()
    private_path = "private/other-client/layout.indd"
    nas.files[private_path] = SimFile(sc.blobs["layout-v2"], 1200)
    nas._add_parents(private_path)
    for copy in sc.memory.copies:
        if copy["version"] == sc.memory.assets["A-layout"]["current"] and copy["location"] == "L-bk-old":
            copy["path"] = private_path
    report = VariantC(sc, nas, sc.memory).run()
    outside = [{"op": op, "args": args, "success": success}
               for op, args, success in nas.log
               if args.get("path") == private_path or args.get("src") == private_path]
    return not outside, {"overall": (report.final or {}).get("overall"), "out_of_scope_calls": outside}


def lossless_paths():
    original = "/nas/Cliente O'Neil/foto, final.tif"
    bundle = Bundle("B-REVIEW")
    bundle.add("CPY-REVIEW", "copy", real_path=original)
    result = parse(bundle.render())["records"]["CPY-REVIEW"]["real_path"]
    return original == result, {"original": original, "roundtrip": result}


def invalid_copy_eligibility():
    sc = load(SCENARIOS / "S03-recent-wrong-copy.json")
    for copy in sc.memory.copies:
        copy["sha256"] = "0" * 64
        copy["access"] = "denied"
    result = evaluate_set(sc.memory, "SET-D2", {"id": "review", "type": "location", "location": "L-proj"})
    counts = {asset: row["eligible"] for asset, row in result["members"].items()}
    return result["verdict"] != "recoverable" and not any(counts.values()), {
        "verdict": result["verdict"], "eligible": counts}


def variant_isolation():
    sc = load(SCENARIOS / "S14-stale-memory-provenance.json")
    run_variant("C", sc)
    shared, shared_nas = run_variant("C-no-selector", sc)
    fresh, fresh_nas = run_variant("C-no-selector", load(SCENARIOS / "S14-stale-memory-provenance.json"))
    detail = {"shared_calls": shared_nas.stats()["calls_total"],
              "fresh_calls": fresh_nas.stats()["calls_total"],
              "shared_revalidated": shared.revalidated, "fresh_revalidated": fresh.revalidated}
    return detail["shared_calls"] == detail["fresh_calls"] and shared.revalidated == fresh.revalidated, detail


PROBES = [
    ("R01", "No recovery when the mandatory plan could not be persisted", plan_save_declined),
    ("R02", "An explicit plan refusal also stops recovery without a prior reference", no_reference_rejected_plan),
    ("R03", "Memory paths cannot escape the approved recovery directory", destination_scope),
    ("R04", "A location label cannot authorize an unrelated source path", source_scope),
    ("R05", "Memory serialization preserves file paths exactly", lossless_paths),
    ("R06", "A wrong-hash or denied copy is not eligible", invalid_copy_eligibility),
    ("R07", "Evaluation results do not depend on which variant ran first", variant_isolation),
]


def main():
    results = []
    for key, property_text, probe in PROBES:
        try:
            passed, detail = probe()
        except Exception as exc:
            passed, detail = False, {"exception": f"{type(exc).__name__}: {exc}"}
        results.append({"id": key, "property": property_text,
                        "status": "PASS" if passed else "FAIL", "evidence": detail})
    print(json.dumps(results, indent=2, ensure_ascii=False))
    failures = sum(result["status"] == "FAIL" for result in results)
    print(f"Review probes: {len(results) - failures} passed, {failures} failed.")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
