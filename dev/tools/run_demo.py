"""Run the Cerbero demo as separate sessions, one Python process per session, on a simulated NAS kept on disk.

Usage (from dev/):
  python tools/run_demo.py all [--out DIR]        every step, each in its own process; writes DIR/reports
  python tools/run_demo.py step NAME --out DIR    one session (used by `all`)

Steps: baseline, incident (staged by the user, not by Cerbero), recover, rebuild, learn, review, retire,
review-after-retire. The NAS tree is DIR/nas, with times and folders in DIR/nas-meta.json. A session
starts from that tree only; Cerbero memory reaches it only through the files in DIR/nas/cerbero-memory.
No Python object or model context crosses from one process to the next. The experts are simulated: this
is the deterministic lab, not UGOS and not a device test.
"""
from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path

DEV = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(DEV))

from cerbero_lab import formats  # noqa: E402
from cerbero_lab.fixtures import apply_incident, load  # noqa: E402
from cerbero_lab.persistence import load_memory  # noqa: E402
from cerbero_lab.pipeline import declarations  # noqa: E402
from cerbero_lab.policy import test_case_bundles  # noqa: E402
from cerbero_lab.sim import SimFile  # noqa: E402
from cerbero_lab.variants import VariantC  # noqa: E402

FIXTURE = DEV / "fixtures" / "demo" / "S00V-demo-valid-formats.json"
DEFAULT_OUT = DEV / "out" / "demo-run"
ROOT = "cerbero-memory"
STEPS = ["baseline", "incident", "recover", "rebuild", "learn", "review", "retire", "review-after-retire"]
LEARN = {"case": "CAS-0002",
         "outcome": "3 copies verified, Delivery 2 complete, raw/DSC_0142.ARW lost with no copy in the named locations",
         "approval_words": "Yes. I approve policy v2: raw/ is critical; exports/previews/ is informational.",
         "candidates": [
             {"version": "v1", "condition": "every review of an authorized project", "scope": "project root",
              "effect": ["promote-critical ."]},
             {"version": "v2", "condition": "every review of an authorized project",
              "scope": "raw/ and exports/previews/ inside the project",
              "effect": ["promote-critical raw", "informational exports/previews"]}]}
RETIRE = "Retire policy v2: the raw originals now have a copy on another device."


def read_nas(out: Path, sc):
    meta = json.loads((out / "nas-meta.json").read_text(encoding="utf-8"))
    files = {p: SimFile((out / "nas" / p).read_bytes(), mtime) for p, mtime in meta["mtimes"].items()}
    nas = sc.build_nas(files=files)
    nas.dirs |= set(meta["dirs"])
    nas.clock = meta["clock"]
    return nas


def write_nas(out: Path, nas) -> None:
    tree = out / "nas"
    if tree.exists():
        shutil.rmtree(tree)
    for path, entry in nas.files.items():
        target = tree / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(entry.data)
    meta = {"mtimes": {p: f.mtime for p, f in sorted(nas.files.items())}, "dirs": sorted(nas.dirs), "clock": nas.clock}
    (out / "nas-meta.json").write_text(json.dumps(meta, indent=1), encoding="utf-8")


def local_open(path: Path) -> str:
    """A local check of the file written to disk by the demo; it is not a NAS capability."""
    data, suffix = path.read_bytes(), path.suffix.lower()
    try:
        if suffix == ".pdf":
            return "local check: PDF structure valid" if formats.check_pdf(data) else "local check: PDF invalid"
        if suffix == ".docx":
            return f"local check: DOCX opens, first line {formats.docx_text(data).splitlines()[0]!r}"
        if suffix == ".tif":
            return "local check: TIFF opens, %dx%d" % formats.check_tiff(data)
    except Exception as exc:  # noqa: BLE001 - report the failure as it is
        return f"local check failed: {exc}"
    return "no local check for this format"


def session(out: Path, sc, intent: str, extra: dict | None = None, **load_options):
    nas = read_nas(out, sc)
    scope_root = sc.location_root(sc.request["scope"])
    memory, info = load_memory(nas, ROOT, scope_root, **{k: v for k, v in load_options.items() if k != "on_freeze"})
    sc.request = {**sc.request, "intent": intent, **(extra or {})}
    variant = VariantC(sc, nas, memory, session=info, intent=intent, on_freeze=load_options.get("on_freeze"))
    report = variant.run()
    write_nas(out, nas)
    return variant, report, info


def name(variant, aid: str) -> str:
    asset = variant.mem.assets.get(aid, {}) if variant.mem else {}
    return asset.get("rel") or asset.get("name") or aid


def header(variant, report, info, title: str) -> list[str]:
    files = info.files.values()
    lines = [f"# {title}", "", f"Case {variant.case}. Simulated experts (lab), not UGOS.", "",
             f"- Memory loaded only from `{ROOT}/`: {sum(f['status'] == 'current' for f in files)} files current, "
             f"{sum(f['status'] == 'needs-review' for f in files)} need review, newest index "
             f"`{Path(info.index_file).name if info.index_file else 'none'}`."]
    if report.rehearsals:
        copies = sorted({r["copy"] for r in report.rehearsals})
        lines.append(f"- Recovery evidence rebuilt from saved receipts: {len(report.rehearsals)} verified entries were "
                     f"copied from {len(copies)} recorded copies ({', '.join(copies)}). Historical: it does not show "
                     "that those copies are still there or still correct.")
    for pid, decision in sorted(info.policy_decisions.items()):
        lines.append(f"- Policy {pid}: {decision}.")
    if not info.policy_decisions:
        lines.append("- Policies in memory: none.")
    return lines + [""]


def plain_result(variant, report) -> str:
    """The first line of a recovery report: the outcome in words, built only from the receipt."""
    final = report.final
    verified = sum(e["status"] in ("verified", "already-present-verified") for e in final["entries"].values())
    if final.get("target_kind") == "full-rebuild":
        text = f"{verified} of {len(final['target_members'])} delivery files rebuilt and verified"
    else:
        text = f"{verified} {'copy' if verified == 1 else 'copies'} verified"
    pending = [name(variant, a) for a in final.get("pending", [])]
    text += "; delivery complete" if final.get("set_complete") else f"; delivery incomplete: {', '.join(pending)}"
    lost = [name(variant, r["asset"]) for r in report.outside_target if not r["source"]]
    if lost:
        text += f"; outside the delivery, no copy of {', '.join(lost)}"
    return text + "."


def receipt_lines(variant, report, out: Path) -> list[str]:
    final = report.final
    lines = [f"Plan `{final['plan']}` ({final.get('target_kind')}), saved file digest `{(final.get('plan_sha256') or '')[:12]}…`, "
             f"approved by the user, re-hashed before the first change.", "",
             "| File | Status | Provenance | Bytes | Version | Format (NAS) | Local check of the file on disk |",
             "|---|---|---|---|---|---|---|"]
    for aid, entry in sorted(final["entries"].items(), key=lambda kv: kv[1]["name"]):
        checks = variant.entry_checks(final, entry)
        dest = entry.get("dest")
        local = local_open(out / "nas" / dest) if dest and (out / "nas" / dest).exists() and entry["status"] == "verified" else ""
        lines.append(f"| {name(variant, aid)} | {entry['status']} | {entry.get('provenance', '')} | {checks['bytes']} | "
                     f"{checks['version']} | {checks['format']} | {local} |")
    lines += ["", f"Operations: **{final['overall']}**. Requested target complete: **{final.get('set_complete')}**. "
              f"Pending in the target: {[name(variant, a) for a in final.get('pending', [])] or 'none'}."]
    if report.outside_target:
        lines.append("Outside the requested target (reported, not copied): " +
                     "; ".join(f"{name(variant, r['asset'])} {r['state']}, "
                               f"{'copy at ' + r['source'] if r['source'] else 'no copy in the named locations'}"
                               for r in report.outside_target) + ".")
    lines.append(f"Files written: `{final['folder']}/` under `{out.name}/nas/`.")
    return lines


def run_step(step: str, out: Path) -> dict:
    sc = load(FIXTURE)
    summary: dict = {"step": step}
    lines: list[str]
    if step == "baseline":
        if out.exists():
            shutil.rmtree(out)
        out.mkdir(parents=True)
        nas = sc.build_nas(files=sc.before)
        variant = VariantC(sc, nas, None, intent="baseline", declarations=declarations(sc))
        report = variant.run()
        write_nas(out, nas)
        lines = ["# Session 1: Baseline", "", "Delivery 2 recorded as an approved set with SHA-256 versions; "
                 f"saved {len(report.persisted)} memory files: " + ", ".join(Path(p).name for p in report.persisted) + "."]
        summary["persisted"] = [Path(p).name for p in report.persisted]
    elif step == "incident":
        nas = read_nas(out, sc)
        nas.files = apply_incident(nas.files, sc.raw["incident"], sc.blobs)
        for path in nas.files:
            nas._add_parents(path)
        write_nas(out, nas)
        lines = ["# Incident staged by the user (not by Cerbero)", ""] + \
                [f"- {op['op']} `{op['path']}`" + (f" to `{op['to']}`" if "to" in op else "") for op in sc.raw["incident"]]
    elif step in ("recover", "rebuild"):
        variant, report, info = session(out, sc, "investigate-recover" if step == "recover" else "rebuild")
        title = "Session 2: what happened, and recover Delivery 2" if step == "recover" else \
            "Session 3: rebuild the whole of Delivery 2 in a new folder"
        lines = header(variant, report, info, title)
        lines[1:1] = ["", f"**{plain_result(variant, report)}**"]
        if step == "recover":
            lines += ["| Asset | State |", "|---|---|"]
            lines += [f"| {name(variant, a)} | {s}" + (f", now at {report.located_at[a]}" if a in report.located_at else "")
                      + " |" for a, s in sorted(report.states.items(), key=lambda kv: name(variant, kv[0]))]
            lines += ["", f"Findings (quoted, not acted on): {len(report.findings)}. Cause: unknown.", ""]
        lines += receipt_lines(variant, report, out)
        final = report.final
        summary.update(case=variant.case, overall=final["overall"], target_complete=final.get("set_complete"),
                       folder=final["folder"], outside=[name(variant, r["asset"]) for r in report.outside_target],
                       entries={e["name"]: {"status": e["status"], **variant.entry_checks(final, e)}
                                for e in final["entries"].values()})
    elif step == "learn":
        seeds = test_case_bundles()
        nas = read_nas(out, sc)
        for seed, data in seeds.items():
            if "-TD-" in seed:
                nas.files[f"{ROOT}/{seed}"] = SimFile(data, nas.clock)
        write_nas(out, nas)

        def holdout_after_freeze(live):
            for seed, data in seeds.items():
                if "-TH-" in seed:
                    live.files[f"{ROOT}/{seed}"] = SimFile(data, live.clock)

        variant, report, info = session(out, sc, "learn", {"learn": LEARN}, confirmed=("CERBERO-TD-0000-01.md",),
                                        read_holdout=False, on_freeze=holdout_after_freeze)
        lines = header(variant, report, info, "Session 4: learn from the closed incident case")
        lines += [f"Closed case: {report.learning.get('case')} (outcome confirmed by the user).", "",
                  "| Version | Effect | Development cases | Holdout cases | Result |", "|---|---|---|---|---|"]
        for row in report.learning.get("candidates", []):
            dev = ", ".join(f"{r['case']} {r['kind']} {'pass' if r['passed'] else 'FAIL'}" for r in row.get("development", []))
            hold = ", ".join(f"{r['case']} {r['kind']} {'pass' if r['passed'] else 'FAIL'}" for r in row.get("holdout", []))
            lines.append(f"| {row['version']} | {'; '.join(row['effect'])} | {dev} | {hold or 'not reached'} | {row.get('result')} |")
        active = [r for r in report.learning.get("candidates", []) if r.get("result") == "active"]
        if active:
            lines += ["", f"Frozen rule digest (D7 of `{Path(active[0]['frozen_file']).name}`): `{active[0]['rule_sha256']}`. "
                      f"Holdout cases unseen before the freeze: {active[0]['holdout_unseen_before_freeze']}. "
                      f"Active record {active[0]['record']}, evaluation {active[0]['evaluation']}."]
        summary.update(case=variant.case, learning=report.learning)
    elif step in ("review", "review-after-retire"):
        variant, report, info = session(out, sc, "review")
        title = "Session 5: a new session reviews Aurora" if step == "review" else \
            "Session 7: the same review after the policy was retired"
        lines = header(variant, report, info, title)
        if report.policy_evidence:
            lines.append("## What Cerbero learned, and the evidence it loaded from memory")
            for key, evidence in report.policy_evidence.items():
                lines.append(f"- {key}: record in `{Path(evidence['file']).name}`; frozen candidate {evidence['frozen']} with "
                             f"rule digest `{evidence['rule_sha256'][:12]}…` equal to the D7 digest of its saved file; "
                             f"evaluation {evidence['evaluation']} (development and holdout cases passed); user approval: "
                             f"\"{evidence['approval']}\".")
            changed = sorted({name(variant, e.split(':', 1)[0]) for e in report.policy_effects})
            lines.append(f"- Effect in this review: {', '.join(changed)} reviewed under the policy (raw/ by digest and "
                         "in the map; exports/previews/ informational).")
        else:
            lines.append("No policy changed this review.")
        lines += ["", "At risk under a failure of the project volume (no copy outside it): "
                  + (", ".join(name(variant, a) for a in report.at_risk) or "none") + "."]
        summary.update(case=variant.case, at_risk=[name(variant, a) for a in report.at_risk],
                       policy_effects=sorted(report.policy_effects), decisions=info.policy_decisions,
                       evidence=report.policy_evidence)
    elif step == "retire":
        variant, report, info = session(out, sc, "retire-policy", {"policy": None, "decision": RETIRE})
        lines = header(variant, report, info, "Session 6: the user retires the policy")
        lines.append(f"Retired: {report.learning.get('retired')} with the recorded decision \"{RETIRE}\".")
        summary.update(case=variant.case, retired=report.learning.get("retired"))
    else:
        raise SystemExit(f"unknown step {step}")
    reports = out / "reports"
    reports.mkdir(exist_ok=True)
    number = STEPS.index(step) + 1
    (reports / f"{number:02d}-{step}.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    (reports / f"{number:02d}-{step}.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
    return summary


def main(argv: list[str]) -> int:
    sys.stdout.reconfigure(encoding="utf-8")
    out = Path(argv[argv.index("--out") + 1]) if "--out" in argv else DEFAULT_OUT
    if argv and argv[0] == "step":
        run_step(argv[1], out)
        return 0
    if argv and argv[0] == "all":
        for step in STEPS:
            done = subprocess.run([sys.executable, str(Path(__file__).resolve()), "step", step, "--out", str(out)],
                                  capture_output=True, text=True, encoding="utf-8")
            if done.returncode:
                print(done.stdout, done.stderr)
                return done.returncode
            print((out / "reports" / f"{STEPS.index(step) + 1:02d}-{step}.md").read_text(encoding="utf-8"))
        return 0
    print(__doc__)
    return 2


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
