"""Run the A/B/C comparison, the selector ablation, the policy evaluation and the memory cost.

Usage: python tools/run_evaluation.py
Writes dev/out/evaluation.json and submission/EVALUATION_REPORT.md.
"""
from __future__ import annotations

import json
import os
import platform
import subprocess
import sys
import tempfile
from collections import defaultdict
from pathlib import Path

DEV = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(DEV))

from cerbero_lab.fixtures import load_all  # noqa: E402
from cerbero_lab.metrics import score  # noqa: E402
from cerbero_lab.pipeline import measure_baseline  # noqa: E402
from cerbero_lab.policy import run_learning  # noqa: E402
from cerbero_lab.variants import run_variant  # noqa: E402

ROOT = DEV.parent
VARIANTS = ["A", "B", "C", "C-no-selector"]
LABELS = {"A": "A simple, no memory", "B": "B memory + hashes", "C": "C full", "C-no-selector": "C without check selector"}
SUMS = ["state_correct", "state_total", "relocations_correct", "relocations_total", "false_alarms", "missed_changes",
        "unknown_acknowledged", "unknown_expected", "whatif_correct", "whatif_total", "false_recoverable",
        "redundancy_overcount", "recovered_correct", "recovery_required", "wrong_recovery_claims",
        "incoherent_versions", "unneeded_copies", "pending_correct", "pending_expected", "limits_acknowledged",
        "limits_expected", "no_source_reported", "no_source_expected", "calls_total", "digests", "bytes_hashed",
        "state_changes", "approvals_requested", "saves", "copies_executed", "unapproved_state_changes",
        "overwrite_attempts", "forbidden_calls", "false_attributions", "runtime_ms", "target_complete_correct",
        "target_complete_total", "outside_correct", "outside_total"]


def ratio(a, b):
    return f"{a}/{b}" if b else "n/a"


DENOMINATORS = {"states": "state_total", "relocations": "relocations_total", "what-if": "whatif_total",
                "recoveries": "recovery_required", "pending": "pending_expected", "limits": "limits_expected",
                "receipts": "overall_total"}


def evaluate(order: list[str] | None = None) -> dict:
    """Every variant runs every scenario on its own state (fresh NAS, memory loaded from saved bundles)."""
    order = order or VARIANTS
    scenarios = load_all()
    rows, totals = [], {v: defaultdict(float) for v in VARIANTS}
    included = {v: defaultdict(list) for v in VARIANTS}
    budget_hit = []
    for sc in scenarios:
        for key in order:
            report, nas = run_variant(key, sc)
            metrics = score(report, sc, nas)
            metrics["variant_key"] = key
            metrics["overall"] = report.final["overall"] if report.final else None
            rows.append(metrics)
            if report.coverage.get("budget_exhausted"):
                budget_hit.append(f"{sc.id}:{key}")
            for name in SUMS:
                totals[key][name] += float(metrics.get(name, 0) or 0)
            totals[key]["overall_correct"] += bool(metrics.get("overall_correct"))
            totals[key]["overall_total"] += "overall_correct" in metrics
            metrics["overall_total"] = int("overall_correct" in metrics)
            included[key]["scenarios"].append(sc.id)
            for label, denominator in DENOMINATORS.items():
                if metrics.get(denominator):
                    included[key][label].append(sc.id)
    rows.sort(key=lambda r: (r["scenario"], VARIANTS.index(r["variant_key"])))
    memory_cost = {key: measure_baseline(next(s for s in scenarios if s.id == "S00"), key) for key in ("B", "C")}
    return {"scenarios": [{"id": s.id, "title": s.title, "covers": s.covers} for s in scenarios],
            "rows": rows, "totals": {k: dict(v) for k, v in totals.items()},
            "included": {k: dict(v) for k, v in included.items()}, "budget_exhausted": budget_hit,
            "memory_cost_S00": memory_cost, "learning": run_learning(), "sessions": demo_sessions(),
            "environment": {"python": platform.python_version(), "platform": platform.platform()}}


def demo_sessions() -> dict:
    """tools/run_demo.py all: every session in its own Python process, memory only from the files on disk."""
    with tempfile.TemporaryDirectory() as tmp:
        out = Path(tmp) / "demo-run"
        done = subprocess.run([sys.executable, str(DEV / "tools" / "run_demo.py"), "all", "--out", str(out)],
                              capture_output=True, text=True, encoding="utf-8", env={**os.environ, "PYTHONIOENCODING": "utf-8"})
        if done.returncode:
            raise RuntimeError(done.stdout + done.stderr)
        return {p.stem: {"summary": json.loads(p.with_suffix(".json").read_text(encoding="utf-8")),
                         "report": p.read_text(encoding="utf-8")}
                for p in sorted((out / "reports").glob("*.md"))}


def markdown(result: dict) -> str:
    t = result["totals"]
    head = "| Metric | " + " | ".join(LABELS[v] for v in VARIANTS) + " |\n|---|" + "---|" * len(VARIANTS)

    def line(label, fn):
        return f"| {label} | " + " | ".join(fn(t[v]) for v in VARIANTS) + " |"

    i = lambda name: (lambda x: str(int(x.get(name, 0))))  # noqa: E731
    r = lambda a, b: (lambda x: ratio(int(x.get(a, 0)), int(x.get(b, 0))))  # noqa: E731
    table = "\n".join([head,
        line("Asset states correct", r("state_correct", "state_total")),
        line("Moved/renamed files located", r("relocations_correct", "relocations_total")),
        line("False alarms (intact or moved reported as lost/altered)", i("false_alarms")),
        line("Missed changes (lost/altered reported as fine)", i("missed_changes")),
        line("Unknowns correctly reported as unknown", r("unknown_acknowledged", "unknown_expected")),
        line("What-if verdicts correct", r("whatif_correct", "whatif_total")),
        line("Unwarranted 'recoverable' verdicts", i("false_recoverable")),
        line("Copies over-counted as redundancy", i("redundancy_overcount")),
        line("Required recoveries verified with the right version", r("recovered_correct", "recovery_required")),
        line("Recoveries claimed with the wrong version", i("wrong_recovery_claims")),
        line("Recovered files outside every approved version", i("incoherent_versions")),
        line("Unneeded copies made", i("unneeded_copies")),
        line("Pending entries reported with the right status", r("pending_correct", "pending_expected")),
        line("Limits acknowledged (partial set, no reference, unknown domain, coverage)", r("limits_acknowledged", "limits_expected")),
        line("Receipt overall status correct", r("overall_correct", "overall_total")),
        line("Requested target reported complete or incomplete correctly", r("target_complete_correct", "target_complete_total")),
        line("Changed files outside the requested target reported apart, not planned", r("outside_correct", "outside_total")),
        line("Expert calls (simulated)", i("calls_total")),
        line("Digests computed", i("digests")),
        line("Bytes hashed", i("bytes_hashed")),
        line("Copies executed", i("copies_executed")),
        line("Approvals requested", i("approvals_requested")),
        line("Memory saves", i("saves")),
        line("State changes without approval", i("unapproved_state_changes")),
        line("Overwrite attempts", i("overwrite_attempts")),
        line("Delete/move calls", i("forbidden_calls")),
        line("Cause attributions without a source", i("false_attributions")),
        line("Local runtime of the procedures, ms (not NAS latency)", lambda x: f"{x.get('runtime_ms', 0):.1f}"),
    ])
    per = defaultdict(dict)
    for row in result["rows"]:
        per[row["scenario"]][row["variant_key"]] = row
    scen_lines = ["| Scenario | Covers | " + " | ".join(VARIANTS) + " |", "|---|---|" + "---|" * len(VARIANTS)]
    for s in result["scenarios"]:
        cells = []
        for v in VARIANTS:
            row = per[s["id"]].get(v)
            if not row:
                cells.append("n/a")
                continue
            parts = []
            if "state_total" in row:
                parts.append(f"states {row['state_correct']}/{row['state_total']}")
            if "whatif_total" in row:
                parts.append(f"what-if {row['whatif_correct']}/{row['whatif_total']}")
            if "recovery_required" in row:
                parts.append(f"recovered {row['recovered_correct']}/{row['recovery_required']}")
                if row["wrong_recovery_claims"]:
                    parts.append(f"wrong {row['wrong_recovery_claims']}")
                parts.append(f"receipt {row['overall']}")
            parts.append(f"{row['calls_total']} calls")
            cells.append(", ".join(parts))
        scen_lines.append(f"| {s['id']} {s['title']} | {', '.join(s['covers'])} | " + " | ".join(cells) + " |")
    learning = result["learning"]
    learn_lines = ["| Candidate | Guard | Development | Holdout | Final status |", "|---|---|---|---|---|"]
    for name, ev in learning["candidates"].items():
        dev = ", ".join(f"{r['case']} {'pass' if r['passed'] else 'FAIL'}" for r in ev.get("development", [])) or "not run"
        hold = ", ".join(f"{r['case']} {'pass' if r['passed'] else 'FAIL'}" for r in ev.get("holdout", [])) or "not run"
        guard = "; ".join(ev["guard"]) or "ok"
        learn_lines.append(f"| {name} | {guard} | {dev} | {hold} | {ev['final_status']} |")
    base = ", ".join(f"{r['case']} {'pass' if r['passed'] else 'FAIL'}" for r in learning["baseline_without_policy"])
    cost = result["memory_cost_S00"]
    inc = result["included"]
    cov_lines = ["| Denominator | " + " | ".join(VARIANTS) + " |", "|---|" + "---|" * len(VARIANTS)]
    for label in ["scenarios"] + list(DENOMINATORS):
        cov_lines.append(f"| {label} | " + " | ".join(f"{len(inc[v].get(label, []))}: {' '.join(inc[v].get(label, []))}"
                                                       for v in VARIANTS) + " |")
    same = all(inc[v].get("scenarios", []) == inc["C"].get("scenarios", []) for v in VARIANTS)
    incident = [s for s, v in per.items() if "state_total" in v["C"]]
    more_calls = sum(per[s]["C"]["calls_total"] > per[s]["B"]["calls_total"] for s in incident)
    fewer_bytes = sum(per[s]["C"]["bytes_hashed"] < per[s]["B"]["bytes_hashed"] for s in incident)
    tc, tb, tn = t["C"], t["B"], t["C-no-selector"]
    shown = ("03-recover", "04-rebuild", "05-learn", "06-review", "08-review-after-retire")
    sessions = "\n".join(result["sessions"][k]["report"].replace("\n# ", "\n### ").replace("# ", "### ", 1)
                         for k in shown if k in result["sessions"])

    def where(variant, test):
        return [s for s in sorted(per) if test(per[s][variant])] or ["none"]

    c_missed = where("C", lambda m: m.get("missed_changes", 0) > 0)
    nosel_lost = where("C-no-selector", lambda m: m.get("relocations_correct", 0) < m.get("relocations_total", 0))
    b_wrong = where("B", lambda m: m.get("whatif_correct", 0) < m.get("whatif_total", 0)
                    or m.get("recovered_correct", 0) < m.get("recovery_required", 0)
                    or m.get("state_correct", 0) < m.get("state_total", 0))
    a_wrong = where("A", lambda m: m.get("wrong_recovery_claims", 0) > 0 or m.get("state_correct", 0) < m.get("state_total", 0))
    receipt_wrong = {v: where(v, lambda m: "overall_correct" in m and not m["overall_correct"]) for v in VARIANTS}
    return f"""# Cerbero evaluation report

Generated by `python dev/tools/run_evaluation.py` on Python {result['environment']['python']}. Every number below comes from that run.

## What this measures, and what it does not

- The three variants are deterministic reference procedures in `dev/cerbero_lab/variants.py`, run against simulated NAS experts (`dev/cerbero_lab/sim.py`) on {len(result['scenarios'])} synthetic scenarios with hand-written expected outcomes.
- **A**: simple flow without persisted memory. It works by names, sizes and times, takes the newest copy and checks copy fidelity.
- **B**: reference memory with hashes and approved sets, with the same approvals, new-folder recovery, no overwrite and destination check as C.
- **C**: the decision rules written in the Skill references.
- **State isolation.** Each variant runs each scenario on a fresh simulated NAS. B and C never receive the fixture memory: a Baseline session of C records the pre-incident state with its own IDs, its saved files are exported, and the incident session loads memory only from those files (`dev/cerbero_lab/pipeline.py`). B loads the same files without index verification. `dev/tests/test_evaluation.py` runs the variants in two orders and requires identical functional results and counters.
- The comparison measures the value of the written decision rules under identical fixtures, listing limits, faults, approvals and essential verifications. It does not measure the Skill on UGOS, the UGOS model, NAS latency, token use or tool cost. Token and NAS cost figures are not available and are not estimated.
- These are deterministic procedures, not a model following the Skill. Agent runs against the real `SKILL.md` are reported separately in `submission/AGENT_EVALUATION.md`.
- The simulator implements assumed semantics for catalog Actions whose permissions, prerequisites and error codes are published as unknown. Device validation is pending.
- The digest budget was reached in these runs: {', '.join(result['budget_exhausted']) or 'never'}.
- **Definition changed in version 1.2.0.** The receipt overall status is now the result of the plan operations only, and whether the requested target is complete is a separate field with its own metric. Changed files outside the approved set the user named are reported apart and never planned. The expectations of S00, S02 and S04 were updated to this definition (S00 and S02 had counted a raw file outside Delivery 2 as a `no-source` entry, and S04 a member without source in the overall); A and B are scored against the same expectations. A and B have no notion of a requested target, so they score 0 on the two target metrics by construction.

## Aggregate results

{table}

## Which scenarios each total includes

Every variant runs all {len(result['scenarios'])} scenarios{'' if same else ' (NOT the same set for every variant)'}. A scenario contributes to a ratio only when its fixture defines that expectation; the lists below are the scenarios behind each denominator.

{chr(10).join(cov_lines)}

## Per scenario

{chr(10).join(scen_lines)}

## Learning: policy candidates replayed on development and holdout cases

Without any policy, the full procedure gives: {base}.

{chr(10).join(learn_lines)}

This is a replay over visible fixtures: the procedure is deterministic and was written with these cases in view, so it is a consistency check of the lifecycle, not a measure of generalization. The blind-holdout protocol for agent runs is in `dev/agent_eval/`.

## Sessions on disk: recover, rebuild, learn, restart, apply, retire

`python dev/tools/run_demo.py all` runs eight steps of the demo dataset (S00V), each Cerbero session in its own Python process. The simulated NAS is a folder on disk; a session receives nothing from the previous one except the files of the memory folder. The reports below are the output of that run, reproduced unchanged.

{sessions}

## Cost of creating the reference memory (S00 baseline, simulated)

| | Calls | Digests | Bytes hashed | Saves |
|---|---|---|---|---|
| B memory + hashes (modeled: one listing and digest of every file, one save) | {cost['B']['calls_total']} | {cost['B']['digests']} | {cost['B']['bytes_hashed']} | {cost['B']['saves']} |
| C full (the Baseline session actually run) | {cost['C']['calls_total']} | {cost['C']['digests']} | {cost['C']['bytes_hashed']} | {cost['C']['saves']} |

## Reading the results honestly

- C pays for its memory. It makes more expert calls than B in {more_calls} of {len(incident)} incident scenarios ({int(tc['calls_total'])} against {int(tb['calls_total'])} in total). The extra calls come from loading and verifying memory files against the index, metadata checks per asset, real-path checks before reading recorded copies, re-checking each source before copying, and saving the plan, receipt and index.
- C hashes fewer bytes than B in {fewer_bytes} of {len(incident)} incident scenarios ({int(tc['bytes_hashed'])} against {int(tb['bytes_hashed'])} bytes in total), because exact size filters exclude files.
- C requests {int(tc['approvals_requested'])} approvals against {int(tb['approvals_requested'])} for B. {int(tc['saves'])} of them are memory saves, each assumed to need a `save-text` confirmation. Records are grouped up to the 16 KB save budget, so the S00 recovery session made {per['S00']['C']['saves']} saves (case records, plan, receipt and index). Whether the device confirms every save, and its real size limit, are unknown.
- Without the check selector, C hashes {int(tn['bytes_hashed'])} bytes instead of {int(tc['bytes_hashed'])}. Scenarios where it fails to locate a moved file: {', '.join(nosel_lost)}.
- Scenarios where C misses a change: {', '.join(c_missed)}. C checks ordinary files by metadata unless a policy raises them; this is the trade-off that policy POL-0001 v2 addresses, shown in the learning table.
- Scenarios where B gets a state, what-if verdict or recovery wrong: {', '.join(b_wrong)}.
- Scenarios where A gets a state wrong or claims a wrong-version recovery: {', '.join(a_wrong)}.
- Receipt overall status wrong: A {', '.join(receipt_wrong['A'])}; B {', '.join(receipt_wrong['B'])}; C {', '.join(receipt_wrong['C'])}. In S13 (no prior reference) the right status is `fidelity-only`; a variant that reports `verified` there overstates what was checked.
- These comparisons are against the baseline procedures implemented here, not against any other product or assistant.
- None of these results is evidence of behaviour on a UGREEN NAS.
"""


def main() -> int:
    result = evaluate()
    out = DEV / "out"
    out.mkdir(exist_ok=True)
    (out / "evaluation.json").write_text(json.dumps(result, indent=2, default=list), encoding="utf-8")
    (ROOT / "submission").mkdir(exist_ok=True)
    (ROOT / "submission" / "EVALUATION_REPORT.md").write_text(markdown(result), encoding="utf-8")
    print(markdown(result).split("## Per scenario")[0])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
