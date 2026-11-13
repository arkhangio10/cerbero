"""Policy lifecycle and the trace grader."""
import copy
import hashlib
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from cerbero_lab import grader, pipeline, policy
from cerbero_lab import records as rec
from cerbero_lab.fixtures import FIXTURES, load, load_all
from cerbero_lab.persistence import load_memory
from cerbero_lab.variants import VariantC

CANDIDATES = {f"{p['id']}-{p['version']}": p for p in
              json.loads((FIXTURES / "policies.json").read_text(encoding="utf-8"))["candidates"]}
DEMO = Path(__file__).resolve().parents[1] / "tools" / "run_demo.py"
sys.path.insert(0, str(DEMO.parent))
import run_demo  # noqa: E402


class LearningAcrossSessions(unittest.TestCase):
    """Closed case -> candidate -> counterexample -> freeze -> holdout -> approval -> persistence -> a new process
    that loads only the saved files and changes its review -> retirement. No Python object crosses sessions."""

    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        cls.out = Path(cls.tmp.name) / "demo"
        done = subprocess.run([sys.executable, str(DEMO), "all", "--out", str(cls.out)], capture_output=True,
                              text=True, encoding="utf-8", env={**os.environ, "PYTHONIOENCODING": "utf-8"})
        assert done.returncode == 0, done.stdout + done.stderr
        cls.steps = {p.stem.split("-", 1)[1]: json.loads(p.read_text(encoding="utf-8"))
                     for p in (cls.out / "reports").glob("*.json")}

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def test_the_recovered_delivery_is_complete_and_pending_items_are_kept_apart(self):
        recover = self.steps["recover"]
        self.assertEqual((recover["overall"], recover["target_complete"]), ("verified", True))
        self.assertEqual(recover["outside"], ["raw/DSC_0142.ARW"])
        rebuild = self.steps["rebuild"]
        self.assertEqual(sorted(rebuild["entries"]), ["brief.pdf", "copy.docx", "cover.tif", "layout.indd", "logo.ai"])
        self.assertTrue(all(e["status"] == "verified" for e in rebuild["entries"].values()))
        self.assertTrue(rebuild["entries"]["brief.pdf"]["format"].startswith("opened by document-agent"))

    def test_the_overbroad_rule_is_refuted_and_the_frozen_revision_is_activated(self):
        rows = {r["version"]: r for r in self.steps["learn"]["learning"]["candidates"]}
        self.assertTrue(rows["v1"]["result"].startswith("rejected"))
        self.assertIn("counterexample", [r["kind"] for r in rows["v1"]["development"] if not r["passed"]])
        self.assertEqual(rows["v2"]["result"], "active")
        self.assertTrue(rows["v2"]["holdout_unseen_before_freeze"])
        self.assertEqual({r["split"] for r in rows["v2"]["holdout"]}, {"holdout"})
        frozen = self.out / "nas" / rows["v2"]["frozen_file"]
        self.assertEqual(hashlib.sha256(frozen.read_bytes()).hexdigest(), rows["v2"]["rule_sha256"])

    def test_a_new_process_applies_the_policy_loaded_from_files_and_explains_why(self):
        review = self.steps["review"]
        applied = [pid for pid, why in review["decisions"].items() if why == "applied"]
        self.assertEqual(len(applied), 1)
        self.assertEqual(sorted(review["at_risk"]), ["raw/DSC_0101.ARW", "raw/DSC_0142.ARW", "raw/DSC_0150.ARW"])
        evidence = next(iter(review["evidence"].values()))
        self.assertEqual(evidence["rule_sha256"], self.steps["learn"]["learning"]["candidates"][1]["rule_sha256"])
        self.assertTrue(evidence["approval"].startswith("Yes. I approve policy v2"))

    def test_the_retired_policy_stops_applying(self):
        after = self.steps["review-after-retire"]
        self.assertEqual(after["at_risk"], [])
        self.assertEqual(after["policy_effects"], [])
        self.assertTrue(any(why == "not applied: status retired" for why in after["decisions"].values()))


class UnprovenPoliciesNeverActivate(unittest.TestCase):
    """An attacker or a bug edits the saved policy chain; only a complete, verified chain is applied."""

    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        cls.out = Path(cls.tmp.name) / "demo"
        for step in run_demo.STEPS[:5]:
            run_demo.run_step(step, cls.out)
        cls.memory = {p.name: p.read_bytes() for p in (cls.out / "nas" / "cerbero-memory").glob("*.md")}

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def decisions(self, edit, reindex=True) -> dict:
        folder = self.out / "nas" / "cerbero-memory"
        files = dict(self.memory)
        files = edit(files)
        if reindex:
            newest = max(n for n in files if "IDX" in n)
            index = rec.parse(files[newest].decode())
            bundle = rec.Bundle(index["header"]["bundle_id"], case_id=index["header"]["case_id"],
                                scope_id=index["header"]["scope_id"])
            for rid, row in index["records"].items():
                name = Path(row["file"]).name
                if row["sha256"] and name in files:
                    row["sha256"] = hashlib.sha256(files[name]).hexdigest()
                bundle.add(rid, "index-entry", **{k: v for k, v in row.items() if k != "type"})
            files[newest] = bundle.render().encode()
        for name, data in files.items():
            (folder / name).write_bytes(data)
        try:
            sc = load(run_demo.FIXTURE)
            nas = run_demo.read_nas(self.out, sc)
            _, info = load_memory(nas, "cerbero-memory", sc.location_root(sc.request["scope"]))
            return info.policy_decisions
        finally:
            for name, data in self.memory.items():
                (folder / name).write_bytes(data)

    def holding(self, files, *markers):
        return next(n for n, d in files.items() if all(m.encode() in d for m in markers))

    def replace(self, marker, old, new):
        def edit(files):
            name = self.holding(files, marker)
            files[name] = files[name].replace(old.encode(), new.encode())
            return files
        return edit

    def test_the_untouched_chain_is_applied(self):
        self.assertIn("applied", self.decisions(lambda f: f).values())

    def test_an_edit_without_a_matching_index_makes_the_policy_file_untrusted(self):
        decisions = self.decisions(self.replace('- status: "active"', "promote-critical raw", "promote-critical raw2"),
                                   reindex=False)
        self.assertNotIn("applied", decisions.values())

    def test_missing_approval_wrong_rule_digest_or_no_holdout_are_refused(self):
        edits = {
            "no recorded user approval": self.replace('- status: "active"', '- approval: "Yes. I approve policy v2: raw/ '
                                                       'is critical; exports/previews/ is informational."', "- approval: null"),
            "frozen candidate file digest differs": self.replace(
                '- status: "active"', '- status: "active"', '- status: "active"\n- rule_sha256: "' + "0" * 64 + '"'),
            "holdout": self.replace("holdout similar pass", " holdout ", " development "),
            "status evaluated": self.replace('- status: "active"', '- status: "active"', '- status: "evaluated"'),
        }
        for reason, edit in edits.items():
            with self.subTest(reason):
                decisions = self.decisions(edit)
                self.assertNotIn("applied", decisions.values(), reason)

    def forge(self, effect_line: str) -> dict:
        """Rewrite the effect in the frozen candidate and the active record, and every digest that binds them."""
        def edit(files):
            old = '"promote-critical raw", "informational exports/previews"'
            new = f'"promote-critical raw", "{effect_line}"'
            frozen = self.holding(files, '- status: "candidate"', old)
            before = hashlib.sha256(files[frozen]).hexdigest()
            files[frozen] = files[frozen].replace(old.encode(), new.encode())
            after = hashlib.sha256(files[frozen]).hexdigest()
            for name in files:
                if name != frozen:
                    files[name] = files[name].replace(old.encode(), new.encode()).replace(before.encode(), after.encode())
            return files
        return self.decisions(edit)

    def test_a_fully_forged_chain_is_still_stopped_by_the_guard(self):
        decisions = self.forge("skip-destination-check all")
        self.assertTrue(any("guard: I5" in why for why in decisions.values()), decisions)

    def test_an_effect_the_lab_does_not_implement_is_reported_not_applied(self):
        decisions = self.forge("add-check five-missing")
        self.assertTrue(any("not implemented by the lab adapter: add-check" in why for why in decisions.values()), decisions)


class PolicyLifecycle(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.cases = load_all("policy_cases")
        cls.results = policy.run_learning()

    def test_expected_outcome_for_every_candidate(self):
        for name, status in self.results["expected"].items():
            self.assertEqual(self.results["candidates"][name]["final_status"], status, name)

    def test_overbroad_rule_is_refuted_by_the_counterexample(self):
        v1 = self.results["candidates"]["POL-0001-v1"]
        failed = {r["case"] for r in v1["development"] + v1["holdout"] if not r["passed"]}
        self.assertIn("P2-counterexample", failed)

    def test_revised_rule_passes_development_and_holdout_separately(self):
        v2 = self.results["candidates"]["POL-0001-v2"]
        self.assertTrue(all(r["passed"] for r in v2["development"]))
        self.assertTrue(all(r["passed"] for r in v2["holdout"]))
        self.assertEqual({r["split"] for r in v2["holdout"]}, {"holdout"})
        self.assertEqual(len(v2["rule_sha256"]), 64)

    def test_guard_names_the_invariant_each_unsafe_rule_breaks(self):
        expectations = {"POL-0001-v3": "I5", "POL-0002-v1": "I7", "POL-0003-v1": "I6", "POL-0004-v1": "I2"}
        for name, invariant in expectations.items():
            violations = self.results["candidates"][name]["guard"]
            self.assertTrue(any(v.startswith(invariant) for v in violations), f"{name}: {violations}")

    def test_without_the_policy_the_motivating_cases_fail(self):
        baseline = {r["case"]: r["passed"] for r in self.results["baseline_without_policy"]}
        self.assertFalse(baseline["P1-origin"])
        self.assertFalse(baseline["P3-similar-borealis"])

    def test_holdout_cases_cannot_be_used_for_drafting(self):
        leaky = copy.deepcopy(CANDIDATES["POL-0001-v2"])
        leaky["drafted_from"].append("P3-similar-borealis")
        with self.assertRaises(ValueError):
            policy.evaluate(leaky, self.cases)

    def test_a_rule_needs_all_four_case_kinds(self):
        partial = [c for c in self.cases if c.raw["case"]["kind"] != "insufficient"]
        result = policy.evaluate(CANDIDATES["POL-0001-v2"], partial)
        self.assertEqual(result["status"], "not-evaluable")
        self.assertEqual(result["missing_kinds"], ["insufficient"])

    def test_evaluation_needs_a_holdout_case(self):
        development = [c for c in self.cases if c.raw["case"]["split"] == "development"]
        result = policy.evaluate(CANDIDATES["POL-0001-v2"], development)
        self.assertEqual(result["status"], "not-evaluable")
        self.assertIn("holdout", result["missing_kinds"])

    def test_policy_loaded_from_memory_is_guarded_again(self):
        case = load("fixtures/policy_cases/P1-origin.json")
        report = VariantC(case, case.build_nas(), case.memory, policies=[CANDIDATES["POL-0001-v3"]]).run()
        self.assertEqual(report.rejected_policies, ["POL-0001-v3"])
        self.assertEqual(report.policy_effects, set())

    def test_active_policy_changes_the_next_review_and_says_so(self):
        case = load("fixtures/policy_cases/P1-origin.json")
        report = VariantC(case, case.build_nas(), case.memory, policies=[CANDIDATES["POL-0001-v2"]]).run()
        self.assertTrue({"A-raw0101", "A-raw0142", "A-raw0150"} <= set(report.at_risk))
        self.assertIn("A-raw0142:POL-0001-v2", report.policy_effects)


def export(nas, tmp, edit=lambda text: text):
    for path in nas.files:
        if path.startswith("cerbero-memory/"):
            Path(tmp, Path(path).name).write_bytes(edit(nas.content(path).decode("utf-8")).encode("utf-8"))


class TraceGrader(unittest.TestCase):
    """The grader reads memory exported from a two-session run (Baseline, then incident)."""

    def test_traces_of_the_reference_run_grade_clean(self):
        for name in ("S00-demo-aurora", "S05-shared-failure-domain", "S08-retry-after-partial-failure",
                     "S13-no-prior-reference", "S14-stale-memory-provenance", "S15-unknown-failure-domain"):
            sc = load(f"fixtures/scenarios/{name}.json")
            _, nas = pipeline.run("C", sc)
            with tempfile.TemporaryDirectory() as tmp:
                export(nas, tmp)
                result = grader.grade(Path(tmp), sc, read_file=nas.content)
            self.assertEqual((result["parse_errors"], result["integrity_problems"]), ([], []), name)
            self.assertEqual(result["passed"], result["total"], f"{name}: {[c for c in result['checks'] if not c['pass']]}")
            self.assertGreater(result["total"], 0)

    def test_every_scenario_exports_memory_without_integrity_problems(self):
        for sc in load_all():
            _, nas = pipeline.run("C", sc)
            with tempfile.TemporaryDirectory() as tmp:
                export(nas, tmp)
                result = grader.grade(Path(tmp), sc, read_file=nas.content)
            self.assertEqual((result["parse_errors"], result["integrity_problems"]), ([], []), sc.id)

    def test_grader_catches_a_receipt_that_overstates_the_result(self):
        sc = load("fixtures/scenarios/S04-incompatible-set-versions.json")
        _, nas = pipeline.run("C", sc)
        with tempfile.TemporaryDirectory() as tmp:
            export(nas, tmp, lambda text: text.replace('- set_complete: false', '- set_complete: true'))
            result = grader.grade(Path(tmp), sc)
        failing = [c["check"] for c in result["checks"] if not c["pass"]]
        self.assertEqual(failing, ["receipt target complete"])
        self.assertTrue(any("digest differs from the newest index" in p for p in result["integrity_problems"]))

    def test_grader_catches_a_receipt_that_drops_a_pending_member(self):
        sc = load("fixtures/scenarios/S04-incompatible-set-versions.json")
        _, nas = pipeline.run("C", sc)
        with tempfile.TemporaryDirectory() as tmp:
            export(nas, tmp, lambda text: text.replace('- pending: ["AST-0001-0006"]', '- pending: []'))
            result = grader.grade(Path(tmp), sc)
        failing = [c["check"] for c in result["checks"] if not c["pass"]]
        self.assertEqual(failing, ["receipt pending names every unfinished target member"])

    def test_receipt_claims_and_recovered_bytes_are_graded_separately(self):
        sc = load("fixtures/scenarios/S03-recent-wrong-copy.json")
        _, nas = pipeline.run("C", sc)
        dest = next(p for p in nas.files if p.startswith("recovered/") and p.endswith("layout.indd"))
        nas.files[dest] = type(nas.files[dest])(b"tampered after the receipt", 1)
        with tempfile.TemporaryDirectory() as tmp:
            export(nas, tmp)
            result = grader.grade(Path(tmp), sc, read_file=nas.content)
        failing = {(c["group"], c["check"]) for c in result["checks"] if not c["pass"]}
        self.assertEqual(failing, {("files", "recovered file digest A-layout")})

    def test_files_option_reads_a_copy_of_the_recovery_folder(self):
        sc = load("fixtures/scenarios/S03-recent-wrong-copy.json")
        report, nas = pipeline.run("C", sc)
        folder = report.final["folder"]
        with tempfile.TemporaryDirectory() as tmp, tempfile.TemporaryDirectory() as files:
            export(nas, tmp)
            for path in nas.files:
                if path.startswith(folder + "/"):
                    target = Path(files, path[len(folder) + 1:])
                    target.parent.mkdir(parents=True, exist_ok=True)
                    target.write_bytes(nas.content(path))
            result = grader.grade(Path(tmp), sc, files=Path(files))
        self.assertEqual(result["files_checked"], 1)
        self.assertEqual(result["passed"], result["total"])


if __name__ == "__main__":
    unittest.main()
