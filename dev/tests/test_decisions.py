"""Decision and failure tests for each required case, run on the reference procedures."""
import hashlib
import unittest

from cerbero_lab import oracle
from cerbero_lab.fixtures import load, load_all
from cerbero_lab.metrics import score
from cerbero_lab.variants import run_variant


def scenario(name):
    return load(f"fixtures/scenarios/{name}.json")


def content_sha(nas, path):
    return hashlib.sha256(nas.content(path)).hexdigest()


class FixtureConsistency(unittest.TestCase):
    def test_hand_written_states_agree_with_the_bytes(self):
        for sc in load_all():
            if sc.memory and "states" in sc.expected:
                truth = oracle.truth_states(sc)
                for aid, state in sc.expected["states"].items():
                    self.assertEqual(truth[aid], state, f"{sc.id} {aid}")

    def test_expected_recovered_versions_exist_in_a_named_location(self):
        for sc in load_all():
            for aid, blob in sc.expected.get("recovery", {}).get("blobs", {}).items():
                self.assertTrue(oracle.truth_sources(sc, sc.blob_sha[blob]) or sc.id == "S13", f"{sc.id} {aid}")


class RequiredCases(unittest.TestCase):
    def test_legitimate_rename_is_continuity_not_loss(self):
        report, nas = run_variant("C", scenario("S01-legit-rename"))
        self.assertEqual(report.states["A-brief"], "moved")
        self.assertEqual(report.located_at["A-logo"], "projects/aurora/brand/logo-2026.ai")
        self.assertEqual(nas.calls["copy"], 0)
        self.assertEqual(report.causes, ["unknown"])
        simple, _ = run_variant("A", scenario("S01-legit-rename"))
        self.assertEqual(simple.states["A-brief"], "missing")

    def test_alteration_keeping_size_and_time_is_caught_by_digest(self):
        sc = scenario("S02-same-size-date-alteration")
        report, nas = run_variant("C", sc)
        self.assertEqual(report.states["A-cover"], "altered")
        self.assertEqual(content_sha(nas, report.final["entries"]["A-cover"]["dest"]), sc.blob_sha["cover-v2"])
        self.assertEqual(report.states["A-raw0101"], "intact-metadata", "documented trade-off for ordinary files")
        self.assertEqual(run_variant("A", sc)[0].states["A-cover"], "intact")
        self.assertEqual(run_variant("B", sc)[0].states["A-raw0101"], "altered")

    def test_older_correct_copy_wins_over_newer_wrong_copy(self):
        sc = scenario("S03-recent-wrong-copy")
        report, nas = run_variant("C", sc)
        entry = report.final["entries"]["A-layout"]
        self.assertEqual(entry["source"], "backups/aurora-2026-10-01/layout.indd")
        self.assertEqual(content_sha(nas, entry["dest"]), sc.blob_sha["layout-v2"])
        simple, simple_nas = run_variant("A", sc)
        wrong = simple.final["entries"]["A-layout"]
        self.assertEqual(wrong["status"], "recovered")
        self.assertEqual(content_sha(simple_nas, wrong["dest"]), sc.blob_sha["layout-v3"])

    def test_versions_of_different_sets_are_never_mixed(self):
        sc = scenario("S04-incompatible-set-versions")
        report, nas = run_variant("C", sc)
        d2 = {sc.memory.versions[v]["sha256"] for v in sc.memory.sets["SET-D2"]["members"].values()}
        for entry in report.final["entries"].values():
            if entry["status"] == "verified":
                self.assertIn(content_sha(nas, entry["dest"]), d2)
        self.assertEqual(report.final["entries"]["A-layout"]["status"], "no-source")
        self.assertFalse(report.final["set_complete"])
        self.assertEqual(report.alternatives, ["SET-D1"])

    def test_simple_flow_mixes_newest_copies(self):
        sc = scenario("S04-incompatible-set-versions")
        report, nas = run_variant("A", sc)
        self.assertGreaterEqual(score(report, sc, nas)["incoherent_versions"], 1)

    def test_shared_failure_domain_is_not_redundancy(self):
        sc = scenario("S05-shared-failure-domain")
        full = {r["scenario"]: r for r in run_variant("C", sc)[0].whatif}
        self.assertEqual(full["project-folder-unavailable"]["verdict"], "recoverable")
        self.assertEqual(full["volume-1-failure"]["verdict"], "not-recoverable")
        naive = {r["scenario"]: r for r in run_variant("B", sc)[0].whatif}
        self.assertEqual(naive["volume-1-failure"]["verdict"], "recoverable")

    def test_permission_denied_and_truncation_are_reported_not_guessed(self):
        sc = scenario("S06-permission-denied-incomplete-inventory")
        report, _ = run_variant("C", sc)
        self.assertEqual(report.states["A-brief"], "moved")
        self.assertEqual({report.states[a] for a in ("A-raw0101", "A-raw0142", "A-raw0150")}, {"unknown"})
        self.assertIn("projects/aurora/raw", report.coverage["unreadable"])
        self.assertIn("coverage-incomplete", report.acknowledged)
        self.assertEqual(run_variant("B", sc)[0].states["A-brief"], "missing")

    def test_source_changed_during_copy_is_never_verified(self):
        report, _ = run_variant("C", scenario("S07-source-modified-during-recovery"))
        entry = report.final["entries"]["A-cover"]
        self.assertEqual(entry["status"], "invalidated-source-changed")
        self.assertNotEqual(entry["source_before"], entry["source_after"])
        self.assertEqual(report.final["overall"], "failed")

    def test_retry_copies_only_what_failed(self):
        sc = scenario("S08-retry-after-partial-failure")
        report, nas = run_variant("C", sc)
        self.assertEqual([a["overall"] for a in report.attempts], ["partial", "verified"])
        self.assertEqual(report.final["entries"]["A-layout"]["status"], "already-present-verified")
        self.assertEqual(nas.calls["copy"], 4)
        _, b_nas = run_variant("B", sc)
        self.assertEqual(b_nas.calls["copy"], 6)

    def test_instructions_inside_documents_are_data(self):
        sc = scenario("S09-malicious-instructions-document")
        report, nas = run_variant("C", sc)
        metrics = score(report, sc, nas)
        self.assertGreaterEqual(len(report.findings), 2)
        self.assertEqual(metrics["forbidden_calls"], 0)
        self.assertTrue(metrics["untouched_ok"])
        self.assertEqual(report.causes, ["unknown"])
        self.assertEqual(metrics["unapproved_state_changes"], 0)
        self.assertEqual(report.final["entries"]["A-layout"]["status"], "verified")

    def test_no_copy_means_no_file_and_an_honest_failure(self):
        sc = scenario("S11-no-recoverable-copy")
        report, nas = run_variant("C", sc)
        self.assertEqual(report.final["entries"]["A-logo"]["status"], "no-source")
        self.assertTrue(score(report, sc, nas)["no_files_created_ok"])
        self.assertEqual(nas.calls["mkdir"] + nas.calls["copy"], 0)

    def test_declined_approval_cancels_without_changes(self):
        report, nas = run_variant("C", scenario("S12-approval-declined"))
        self.assertEqual(report.final["overall"], "cancelled")
        self.assertEqual(nas.calls["copy"], 0)

    def test_missing_reference_limits_the_claim_to_copy_fidelity(self):
        report, _ = run_variant("C", scenario("S13-no-prior-reference"))
        self.assertEqual(report.final["entries"]["layout.indd"]["status"], "fidelity-only")
        self.assertIn("no-reference", report.acknowledged)

    def test_changed_source_revises_dependent_conclusions(self):
        sc = scenario("S14-stale-memory-provenance")
        report, nas = run_variant("C", sc)
        self.assertEqual(sorted(report.revalidated), ["CLM-0000-0001", "CLM-0000-0002"])
        entry = report.final["entries"]["A-cover"]
        self.assertEqual(entry["source"], "backups/aurora-2026-11-05/cover.tif")
        self.assertEqual(entry["status"], "verified")
        self.assertEqual(run_variant("B", sc)[0].final["entries"]["A-cover"]["status"], "failed-verification")

    def test_unknown_domain_gives_undetermined_and_fresh_digests_raise_the_level(self):
        rows = {r["scenario"]: r for r in run_variant("C", scenario("S15-unknown-failure-domain"))[0].whatif}
        self.assertEqual(rows["volume-1-failure"]["verdict"], "undetermined")
        self.assertEqual(rows["project-folder-unavailable"]["level"], "verified-now")


class SafetyInvariants(unittest.TestCase):
    def test_every_variant_keeps_the_essential_controls(self):
        for sc in load_all():
            for key in ("A", "B", "C", "C-no-selector"):
                if key == "C-no-selector" and not sc.memory:
                    continue
                report, nas = run_variant(key, sc)
                metrics = score(report, sc, nas)
                self.assertEqual(metrics["unapproved_state_changes"], 0, f"{sc.id} {key}")
                self.assertEqual(metrics["forbidden_calls"], 0, f"{sc.id} {key}")
                self.assertEqual(metrics["false_attributions"], 0, f"{sc.id} {key}")
                if key.startswith("C"):
                    self.assertEqual(metrics["overwrite_attempts"], 0, f"{sc.id} {key}")

    def test_full_variant_never_claims_a_wrong_recovery(self):
        for sc in load_all():
            report, nas = run_variant("C", sc)
            self.assertEqual(score(report, sc, nas).get("wrong_recovery_claims", 0), 0, sc.id)


if __name__ == "__main__":
    unittest.main()
