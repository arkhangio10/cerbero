"""Grade a Cerbero memory folder (exported from the NAS or from the simulator) against a scenario.

Usage: python -m cerbero_lab.grader <exported-memory-folder> <scenario.json> [--files DIR] [--map MAP.json]

The grader reads only cerbero-memory-2 bundles and reports three things separately:
- integrity: parse, validation and reference problems, and files that differ from the newest index;
- record checks: what the records claim (asset states, what-if verdicts, receipt statuses and the
  destination digests written in receipts), compared with the scenario expectations;
- file checks (only with --files DIR, a copy of the recovery folder named in the plan): the digest of
  each recovered file, compared with the receipt and with the expected version.
Records are matched to scenario keys explicitly: assets by their path relative to the scope real root,
sets by name, scenario rows by label (or through MAP.json), receipt entries through entry_id and
plan-entry. Generated ID shapes and real NAS prefixes do not matter.
"""
from __future__ import annotations

import hashlib
import json
import posixpath
import sys
from pathlib import Path

from . import fixtures, scope
from . import records as rec


def load_folder(folder: Path) -> dict:
    """Parse every CERBERO- file; return records with their file and case, plus integrity problems."""
    out = {"records": {}, "where": {}, "case_of": {}, "problems": [], "order": [], "parse_errors": []}
    bundles = {}
    for path in sorted(folder.glob("*CERBERO-*.md")):
        data = path.read_bytes()
        try:
            bundles[path.name] = (rec.parse(data.decode("utf-8")), hashlib.sha256(data).hexdigest())
        except (ValueError, UnicodeDecodeError) as exc:
            out["parse_errors"].append(f"{path.name}: {exc}")
    indexes = {name: b for name, (b, _) in bundles.items()
               if b["records"] and all(r["type"] == "index-entry" for r in b["records"].values())}
    newest = max(indexes, key=lambda n: indexes[n]["header"]["bundle_id"], default=None)
    listed = {}
    chain, parts = [newest] if newest else [], {newest}
    session_of = {n: b["header"]["bundle_id"].split("-")[1] for n, b in indexes.items()}
    while chain:
        for r in indexes[chain.pop()]["records"].values():
            name = posixpath.basename(r["file"])
            listed.setdefault(name, r)
            if name not in out["order"]:
                out["order"].append(name)
            # A part of the newest snapshot, bound by the digest the next part lists for it.
            if name in indexes and name not in parts and session_of[name] == session_of[newest] \
                    and r.get("sha256") == bundles[name][1]:
                parts.add(name)
                chain.append(name)
    for name, (bundle, digest) in bundles.items():
        if name in indexes:
            continue
        entry = listed.get(name)
        if entry is None:
            out["problems"].append(f"{name}: not listed in the newest index")
        elif entry.get("sha256") != digest:
            out["problems"].append(f"{name}: digest differs from the newest index")
        for record_id, fields in bundle["records"].items():
            if record_id in out["records"]:
                out["problems"].append(f"{name}: duplicate record {record_id}")
                continue
            out["records"][record_id] = fields
            out["where"][record_id] = name
            out["case_of"][record_id] = bundle["header"]["case_id"]
    out["problems"] += rec.validate(out["records"]) + rec.check_references(out["records"])
    return out


def _of_type(records: dict, kind: str) -> dict:
    return {rid: r for rid, r in records.items() if r.get("type") == kind}


def correspondence(records: dict, scenario, mapping: dict) -> dict:
    """Scenario keys -> record IDs, by explicit attributes only."""
    scopes = _of_type(records, "scope")
    if mapping.get("scope_root"):
        scopes = {k: s for k, s in scopes.items() if s.get("real_root") == mapping["scope_root"]}
    result = {"scope": None, "assets": {}, "sets": {}}
    if len(scopes) != 1 or scenario.memory is None:
        return result
    scope_id, scope_rec = next(iter(scopes.items()))
    result["scope"] = scope_id
    by_rel = {}
    for aid, a in _of_type(records, "asset").items():
        if a.get("scope_id") == scope_id:
            rel, _ = scope.relative_inside(a.get("recorded_path"), scope_rec.get("real_root"))
            if rel and not any(r.get("supersedes") == aid for r in records.values()):
                by_rel[rel] = aid
    for key, a in scenario.memory.assets.items():
        result["assets"][key] = by_rel.get(a["rel"])
    for key, s in scenario.memory.sets.items():
        found = [sid for sid, r in _of_type(records, "approved-set").items() if r.get("name") == s.get("name")]
        result["sets"][key] = found[0] if len(found) == 1 else None
    return result


def final_receipt(records: dict) -> tuple[str | None, dict | None]:
    """The receipt of the plan revision that no later plan supersedes."""
    plans = _of_type(records, "plan")
    superseded = {p["supersedes_plan"] for p in plans.values() if p.get("supersedes_plan")}
    receipts = {rid: r for rid, r in _of_type(records, "receipt").items() if r.get("plan_id") not in superseded}
    if len(receipts) != 1:
        return None, None
    return next(iter(receipts.items()))


def grade(folder: Path, scenario, files: Path | None = None, mapping: dict | None = None,
          read_file=None) -> dict:
    """read_file(real_path) -> bytes | None can replace --files (used with the simulator)."""
    mapping = mapping or {}
    loaded = load_folder(folder)
    records = loaded["records"]
    corr = correspondence(records, scenario, mapping)
    exp = scenario.expected
    checks = []

    def check(group, name, expected, got):
        checks.append({"group": group, "check": name, "expected": expected, "got": got, "pass": expected == got})

    receipt_id, receipt = final_receipt(records)
    plan = records.get(receipt.get("plan_id")) if receipt else None
    case = plan.get("case_id") if plan else None
    if case is None:
        cases = [loaded["case_of"][rid] for rid, r in records.items() if r.get("type") == "claim" and r.get("kind") == "asset-state"]
        case = cases[-1] if cases else None
    in_case = {rid: r for rid, r in records.items() if loaded["case_of"][rid] == case}
    states, located = {}, {}
    for r in _of_type(in_case, "claim").values():
        if r.get("kind") == "asset-state" and r.get("status") == "current":
            states[r.get("subject")] = r.get("asset_state")
            if r.get("located_at"):
                located[r.get("subject")] = r["located_at"]
    for key, state in exp.get("states", {}).items():
        got = states.get(corr["assets"].get(key))
        check("records", f"state {key}", state, "intact" if (state == "intact" and got == "intact-metadata") else got)
    scope_rec = records.get(corr["scope"]) if corr["scope"] else None
    for key, path in exp.get("located_at", {}).items():
        got = located.get(corr["assets"].get(key))
        rel_exp, _ = scope.relative_inside(path, scenario.memory.scope_root)
        rel_got, _ = scope.relative_inside(got, scope_rec.get("real_root")) if got and scope_rec else (None, "")
        check("records", f"location {key}", rel_exp, rel_got)
    labels = mapping.get("scenarios", {})
    verdicts = {r.get("scenario"): r.get("verdict") for r in _of_type(records, "map").values()}
    for row in exp.get("whatif", []):
        check("records", f"what-if {row['scenario']}", row["verdict"], verdicts.get(labels.get(row["scenario"], row["scenario"])))
    if "findings_min" in exp:
        check("records", "findings recorded", True, len(_of_type(in_case, "finding")) >= exp["findings_min"])

    file_checks = []
    if "recovery" in exp and exp["recovery"]["entries"]:
        check("records", "receipt overall", exp["recovery"]["overall"], receipt.get("overall") if receipt else None)
        if "set_complete" in exp["recovery"]:
            check("records", "receipt target complete", exp["recovery"]["set_complete"],
                  receipt.get("set_complete") if receipt else None)
        listed = set((receipt or {}).get("pending", []))
        want = sorted(k for k, s in exp["recovery"]["entries"].items() if s not in ("verified", "already-present-verified",
                                                                                   "fidelity-only"))
        got = sorted(k for k, a in corr["assets"].items() if a and a in listed)
        if corr["assets"]:
            check("records", "receipt pending names every unfinished target member", want, got)
        if "outside_target" in exp["recovery"]:
            outside = set((receipt or {}).get("outside_target", []))
            check("records", "receipt outside target", sorted(exp["recovery"]["outside_target"]),
                  sorted(k for k, a in corr["assets"].items() if a and a in outside))
        entries = {}
        for rid, r in _of_type(records, "receipt-entry").items():
            if r.get("receipt_id") != receipt_id:
                continue
            plan_entry = records.get(r["entry_id"]) if r.get("entry_id") else None
            key = next((k for k, a in corr["assets"].items() if a and a == r.get("asset_id")), None)
            if key is None and plan_entry:
                key = plan_entry.get("name")
            entries[key] = (r, plan_entry)
        blob_sha = scenario.blob_sha
        for key, status in exp["recovery"]["entries"].items():
            entry, plan_entry = entries.get(key, ({}, None))
            check("records", f"receipt entry {key}", status, entry.get("status"))
            if key not in exp["recovery"]["blobs"]:
                continue
            want = blob_sha[exp["recovery"]["blobs"][key]]
            check("records", f"receipt destination digest {key}", want, entry.get("destination_sha256"))
            dest = entry.get("destination_path")
            data = None
            if read_file and dest:
                data = read_file(dest)
            elif files and dest and plan:
                rel, _ = scope.relative_inside(dest, plan.get("recovery_folder"))
                local = files / rel if rel else None
                data = local.read_bytes() if local and local.is_file() else None
            if read_file or files:
                got = hashlib.sha256(data).hexdigest() if data is not None else None
                file_checks.append(key)
                check("files", f"recovered file digest {key}", want, got)
    return {"scenario": scenario.id, "records": len(records), "parse_errors": loaded["parse_errors"],
            "integrity_problems": loaded["problems"], "case": case, "receipt": receipt_id,
            "correspondence": corr, "passed": sum(c["pass"] for c in checks), "total": len(checks),
            "files_checked": len(file_checks), "checks": checks}


def main(argv: list[str]) -> int:
    args = argv[1:]
    options = {}
    for flag in ("--files", "--map"):
        if flag in args:
            i = args.index(flag)
            options[flag] = args[i + 1]
            del args[i:i + 2]
    if len(args) != 2:
        print(__doc__)
        return 2
    mapping = json.loads(Path(options["--map"]).read_text(encoding="utf-8")) if "--map" in options else {}
    files = Path(options["--files"]) if "--files" in options else None
    result = grade(Path(args[0]), fixtures.load(args[1]), files=files, mapping=mapping)
    print(json.dumps(result, indent=2, ensure_ascii=False))
    clean = not result["parse_errors"] and not result["integrity_problems"]
    return 0 if result["passed"] == result["total"] and clean else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
