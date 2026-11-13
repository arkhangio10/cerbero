"""Regressions for R01-R04: mandatory plan persistence, one plan protocol, and path scope."""
import copy
import hashlib
import unittest

from cerbero_lab import scope
from cerbero_lab.fixtures import load
from cerbero_lab.pipeline import baseline_session, run, with_memory
from cerbero_lab.persistence import load_memory
from cerbero_lab.sim import SimFile, inside
from cerbero_lab.variants import VariantC, run_variant


def scenario(name):
    return load(f"fixtures/scenarios/{name}.json")


def changes(nas):
    return nas.calls["mkdir"], nas.calls["copy"]


def tamper(files: dict, old: str, new: str) -> dict:
    """An attacker who can write the memory folder edits a bundle and rewrites the index digest."""
    files = dict(files)
    name = next(n for n, data in files.items() if old.encode() in data and "IDX" not in n)
    before = hashlib.sha256(files[name]).hexdigest()
    files[name] = files[name].replace(old.encode(), new.encode())
    after = hashlib.sha256(files[name]).hexdigest()
    index = next(n for n in files if "IDX" in n)
    files[index] = files[index].replace(before.encode(), after.encode())
    return files


def run_with_files(sc, files, nas=None):
    nas = with_memory(sc, files, nas)
    memory, session = load_memory(nas, "cerbero-memory", sc.location_root(sc.request["scope"]))
    return VariantC(sc, nas, memory, session=session).run(), nas


class MandatoryPlan(unittest.TestCase):
    """R01: no folder or copy unless the plan was saved, verified and hashed."""

    def assert_blocked(self, sc, reason_part):
        report, nas = run_variant("C", sc)
        self.assertEqual(changes(nas), (0, 0), sc.faults)
        self.assertIn(reason_part, report.final.get("reason", ""))
        self.assertIn("plan-not-persisted", report.acknowledged)
        return report, nas

    def test_every_kind_of_failed_plan_save_blocks_the_recovery(self):
        for kind, reason in [("save_fail", "plan not persisted"), ("save_unverified", "not verified"),
                             ("save_incomplete", "no file path"), ("save_elsewhere", "outside the memory folder")]:
            sc = scenario("S03-recent-wrong-copy")
            sc.faults.append({"kind": kind, "record_type": "plan"})
            report, _ = self.assert_blocked(sc, reason)
            self.assertEqual(report.final["overall"], "failed", kind)

    def test_a_declined_plan_save_is_a_cancellation(self):
        sc = scenario("S03-recent-wrong-copy")
        sc.raw["declined_approvals"] = [{"op": "save_text"}]
        report, _ = self.assert_blocked(sc, "declined")
        self.assertEqual(report.final["overall"], "cancelled")
        self.assertEqual(report.persisted, [])

    def test_a_plan_whose_saved_file_cannot_be_hashed_blocks_the_recovery(self):
        sc = scenario("S03-recent-wrong-copy")
        sc.faults.append({"kind": "omit_realpath", "op": "sha256", "prefix": "cerbero-memory",
                          "name_prefix": "CERBERO-B-0002"})
        self.assert_blocked(sc, "could not be hashed")

    def test_an_optional_report_that_cannot_be_saved_does_not_stop_the_mode(self):
        sc = scenario("S15-unknown-failure-domain")
        sc.raw["declined_approvals"] = [{"op": "save_text"}]
        report, _ = run_variant("C", sc)
        self.assertEqual({r["scenario"]: r["verdict"] for r in report.whatif},
                         {"project-folder-unavailable": "recoverable", "volume-1-failure": "undetermined"})
        self.assertIn("not-persisted", report.acknowledged)

    def test_a_receipt_that_cannot_be_saved_after_copies_is_reported(self):
        sc = scenario("S03-recent-wrong-copy")
        sc.faults.append({"kind": "save_fail", "record_type": "receipt"})
        report, nas = run_variant("C", sc)
        self.assertEqual(report.final["overall"], "verified")
        self.assertEqual(nas.calls["copy"], 1)
        self.assertTrue(any(item.endswith("not persisted (save_failed)") for item in report.open_items), report.open_items)
        self.assertFalse([p for p in nas.files if p.startswith("cerbero-memory/") and b'- type: "receipt"' in nas.content(p)])


class OnePlanProtocol(unittest.TestCase):
    """R02: recovery without a reference uses the same plan, approval and receipt."""

    def test_refusal_stops_everything_and_is_recorded(self):
        sc = scenario("S13-no-prior-reference")
        sc.raw.setdefault("answers", {})["approve_plan"] = False
        report, nas = run_variant("C", sc)
        self.assertEqual(changes(nas), (0, 0))
        self.assertEqual(report.final["overall"], "cancelled")
        self.assertEqual(report.final["reference"], "source-fidelity")
        receipt = [p for p in report.persisted if "B-0001-02" in p]
        self.assertTrue(receipt, report.persisted)
        self.assertIn('- decision: "declined"', nas.content(receipt[0]).decode())

    def test_approval_gives_fidelity_only_never_verified(self):
        report, nas = run_variant("C", scenario("S13-no-prior-reference"))
        self.assertEqual(report.final["overall"], "fidelity-only")
        self.assertEqual(report.final["entries"]["layout.indd"]["status"], "fidelity-only")
        self.assertTrue(report.final.get("plan_sha256"))
        texts = "".join(nas.content(p).decode() for p in report.persisted)
        self.assertIn('- reference: "source-fidelity"', texts)

    def test_a_manipulated_destination_name_creates_nothing(self):
        sc = scenario("S13-no-prior-reference")
        sc.request["files"][0]["dest_name"] = "../../outside/layout.indd"
        report, nas = run_variant("C", sc)
        self.assertEqual(changes(nas), (0, 0))
        self.assertEqual(report.final["entries"]["layout.indd"]["status"], "out-of-scope")


class PathScope(unittest.TestCase):
    """R03/R04: memory and user input never authorize a path outside the approved folders."""

    def assert_contained(self, nas, folder_prefix="recovered/"):
        for op, args, ok in nas.log:
            if op == "copy":
                self.assertTrue(inside(args["dst"], "recovered"), args)
            if op == "mkdir":
                self.assertTrue(args["path"].startswith(folder_prefix), args)

    def test_rules_on_paths(self):
        cases = [("p/a/b", "p/a", "inside"), ("p/a", "p/a", "inside"), ("p/ab", "p/a", "outside"),
                 ("p/a/../b", "p/a", "non-canonical path"), ("p//a/x", "p", "non-canonical path"),
                 ("/etc/x", "p", "unexpected absolute path"), ("p\\a\\x", "p", "non-canonical path"),
                 ("P/A/x", "p/a", "case-alias"), ("Café/x", "Café", "unicode-alias"),
                 ("p/a/./x", "p/a", "non-canonical path"), ("p/a/x\n", "p/a", "non-canonical path")]
        for path, root, expected in cases:
            self.assertEqual(scope.containment(path, root), expected, (path, root))
        self.assertEqual(scope.child("r/f", "../x"), (None, "non-canonical path"))
        self.assertEqual(scope.child("r/f", "/x"), (None, "unexpected absolute path"))
        self.assertEqual(scope.real_inside({"ok": True, "data": {}}, "r"), (False, "real path not reported"))

    def test_injected_traversal_in_asset_records(self):
        for field, value in [("rel", "../../outside/escaped-layout.indd"),
                             ("path", "projects/aurora/../../outside/escaped-layout.indd"),
                             ("path", "/outside/escaped-layout.indd"), ("path", "projects/aurora\\..\\x.indd")]:
            sc = scenario("S03-recent-wrong-copy")
            sc.memory.assets["A-layout"][field] = value
            nas = sc.build_nas()
            report = VariantC(sc, nas, sc.memory).run()
            self.assert_contained(nas)
            self.assertFalse(any("outside" in (args.get("path") or args.get("dst") or "") for _, args, _ in nas.log),
                             (field, value))
            self.assertIn("A-layout", report.out_of_scope, (field, value))

    def test_traversal_planted_in_persisted_memory_with_a_rewritten_index(self):
        sc = scenario("S03-recent-wrong-copy")
        files, _, _ = baseline_session(sc)
        files = tamper(files, '- recorded_path: "projects/aurora/layout.indd"',
                       '- recorded_path: "projects/aurora/../../outside/escaped-layout.indd"')
        report, nas = run_with_files(sc, files)
        self.assert_contained(nas)
        self.assertFalse(any("outside" in str(args) for _, args, _ in nas.log))
        self.assertEqual(nas.calls["copy"], 0)

    def test_location_label_does_not_authorize_a_foreign_source(self):
        sc = scenario("S03-recent-wrong-copy")
        files, _, _ = baseline_session(sc)
        files = tamper(files, '- real_path: "backups/aurora-2026-10-01/layout.indd"',
                       '- real_path: "private/other-client/layout.indd"')
        nas = sc.build_nas()
        nas.files["private/other-client/layout.indd"] = SimFile(sc.blobs["layout-v2"], 1200)
        report, nas = run_with_files(sc, files, nas)
        self.assertFalse(any("private" in str(args) for _, args, _ in nas.log))
        self.assertEqual(next(iter(report.final["entries"].values()))["status"],
                         "verified", "the real copy is found by searching the named location instead")

    def test_a_link_inside_a_location_that_resolves_outside_is_never_read(self):
        sc = scenario("S03-recent-wrong-copy")
        link = "backups/aurora-2026-10-01/layout.indd"
        sc.faults.append({"kind": "link", "path": link, "target": "private/other-client/layout.indd"})
        nas = sc.build_nas()
        nas.files["private/other-client/layout.indd"] = SimFile(sc.blobs["layout-v2"], 1200)
        report, nas = run_with_files(sc, baseline_session(scenario("S03-recent-wrong-copy"))[0], nas)
        reads = [(op, args) for op, args, _ in nas.log if args.get("path") == link or args.get("src") == link]
        self.assertTrue(all(op == "stat" for op, _ in reads), reads)
        self.assertEqual(nas.calls["copy"], 0)
        self.assertEqual(next(iter(report.final["entries"].values()))["status"], "no-source")

    def test_unreported_real_paths_block_the_dependent_operation(self):
        sc = scenario("S03-recent-wrong-copy")
        sc.faults.append({"kind": "omit_realpath", "op": "stat", "prefix": "backups"})
        sc.faults.append({"kind": "omit_realpath", "op": "sha256", "prefix": "backups"})
        report, nas = run_variant("C", sc)
        self.assertEqual(nas.calls["copy"], 0)
        self.assertEqual(report.final["entries"]["A-layout"]["status"], "no-source")

    def test_review_probe_inputs_still_hold(self):
        sc = scenario("S03-recent-wrong-copy")
        memory = copy.deepcopy(sc.memory)
        memory.assets["A-layout"]["rel"] = "../../outside/escaped-layout.indd"
        nas = sc.build_nas()
        VariantC(sc, nas, memory).run()
        self.assertFalse(nas.exists("outside/escaped-layout.indd"))


class MemoryRealPaths(unittest.TestCase):
    """N02: memory files, index snapshots and the memory root are read or hashed only by proven real paths."""

    def linked(self, link_kind: str):
        sc = scenario("S03-recent-wrong-copy")
        files, _, _ = baseline_session(sc)
        nas = with_memory(sc, files)
        target = "private/other-client/record.md"
        if link_kind == "root":
            nas.faults.append({"kind": "link", "path": "cerbero-memory", "target": "private/other-client"})
            for name, data in files.items():
                nas.files[f"private/other-client/{name}"] = SimFile(data, 4000)
        else:
            alias = next(p for p in nas.files if p.startswith("cerbero-memory/CERBERO-" + link_kind))
            nas.files[target] = SimFile(nas.files[alias].data, 4000)
            nas.faults.append({"kind": "link", "path": alias, "target": target})
        nas._add_parents(target)
        memory, session = load_memory(nas, "cerbero-memory", sc.location_root("L-proj"))
        outside = [(op, args["path"]) for op, args, ok in nas.log if ok and op in ("cat", "sha256")
                   and not scope.inside(nas._resolve(args["path"]), "cerbero-memory")]
        return memory, session, outside

    def test_a_linked_bundle_is_never_read_and_its_records_are_not_evidence(self):
        memory, session, outside = self.linked("B-")
        self.assertEqual(outside, [])
        linked = [i for p, i in session.files.items() if "outside the memory folder" in i["reason"]]
        self.assertEqual(len(linked), 1)
        self.assertEqual(linked[0]["status"], "needs-review")

    def test_a_linked_index_is_never_read_and_no_newest_index_is_taken_from_it(self):
        memory, session, outside = self.linked("IDX-")
        self.assertEqual(outside, [])
        self.assertIsNone(session.index_file)
        self.assertIsNone(memory, "without a trusted index no bundle is evidence")

    def test_a_linked_memory_root_reads_nothing(self):
        memory, session, outside = self.linked("root")
        self.assertEqual(outside, [])
        self.assertIsNone(memory)
        self.assertTrue(any("resolves to private/other-client" in p for p in session.problems), session.problems)

    def test_answers_without_real_paths_stop_the_reads_that_depend_on_them(self):
        sc = scenario("S03-recent-wrong-copy")
        files, _, _ = baseline_session(sc)
        nas = with_memory(sc, files)
        nas.faults += [{"kind": "omit_realpath", "op": "ls", "prefix": "cerbero-memory"},
                       {"kind": "omit_realpath", "op": "stat", "prefix": "cerbero-memory/CERBERO-B-0001-01.md"}]
        memory, session = load_memory(nas, "cerbero-memory", sc.location_root("L-proj"))
        unread = [p for p, i in session.files.items() if i["reason"] == "real path not reported: not read"]
        self.assertEqual(unread, ["cerbero-memory/CERBERO-B-0001-01.md"])
        self.assertFalse([a for op, a, _ in nas.log if op in ("cat", "sha256") and a["path"] in unread])
        self.assertTrue(any(op == "cat" and a["path"].endswith("CERBERO-B-0001-02.md") for op, a, _ in nas.log),
                        "a file whose real path D5 reports is still read")

        nas = with_memory(sc, files)
        nas.faults.append({"kind": "omit_realpath", "op": "stat", "prefix": "cerbero-memory"})
        memory, session = load_memory(nas, "cerbero-memory", sc.location_root("L-proj"))
        self.assertIsNone(memory)
        self.assertIn("memory folder real path not reported", session.problems[0])
        self.assertFalse([op for op, a, _ in nas.log if op in ("cat", "sha256")])


class TargetPending(unittest.TestCase):
    """N01: every member of the requested target stays visible until it is satisfied."""

    def test_an_unknown_member_stays_pending_by_name_after_a_reload(self):
        sc = scenario("S03-recent-wrong-copy")
        sc.faults.append({"kind": "permission_denied", "prefix": "projects/aurora/brief.pdf"})
        report, nas = run_variant("C", sc)
        final = report.final
        self.assertEqual((final["overall"], final["set_complete"]), ("verified", False))
        self.assertEqual(final["entries"]["A-brief"]["status"], "state-unknown")
        memory, session = load_memory(nas, "cerbero-memory", sc.location_root("L-proj"))
        receipt = next(r for r in session.records.values() if r["type"] == "receipt")
        rows = {r["name"]: r for r in session.records.values() if r["type"] == "receipt-entry"}
        brief = next(a for a, x in memory.assets.items() if x["name"] == "brief.pdf")
        self.assertEqual(receipt["pending"], [brief])
        self.assertEqual(rows["brief.pdf"]["status"], "state-unknown")
        self.assertIsNone(rows["brief.pdf"]["entry_id"], "nothing was planned or copied for it")
        self.assertFalse(receipt["set_complete"], "one verified copy is not a complete delivery")
        plan = next(r for r in session.records.values() if r["type"] == "plan")
        self.assertEqual((plan["target_kind"], plan["pending"]), ("approved-set", [brief]))

    def test_changed_files_outside_the_target_are_reported_not_planned(self):
        sc = scenario("S00-demo-aurora")
        report, nas = run_variant("C", sc)
        self.assertEqual(report.final["outside"], ["A-raw0142"])
        self.assertNotIn("A-raw0142", report.final["entries"])
        self.assertEqual([r["asset"] for r in report.outside_target], ["A-raw0142"])
        self.assertIn("A-raw0142", report.no_source, "Cerbero still says whether a source exists")
        self.assertTrue(any(i.startswith("A-raw0142: outside the requested target") or "outside the requested target" in i
                            for i in report.open_items))


class Rebuild(unittest.TestCase):
    """A full rebuild copies every member of the approved set into a new folder, intact members included."""

    def rebuild(self, faults=()):
        sc = load("fixtures/demo/S00V-demo-valid-formats.json")
        files, _, _ = baseline_session(sc)
        nas = with_memory(sc, files)
        nas.faults += list(faults)
        memory, session = load_memory(nas, "cerbero-memory", sc.location_root("L-proj"))
        before = {p: f.data for p, f in nas.files.items() if not p.startswith(("recovered/", "cerbero-memory/"))}
        report = VariantC(sc, nas, memory, session=session, intent="rebuild").run()
        return sc, nas, memory, report, before

    def test_every_member_is_copied_with_three_separate_checks(self):
        sc, nas, memory, report, before = self.rebuild()
        final = report.final
        self.assertEqual((final["target_kind"], final["overall"], final["set_complete"]), ("full-rebuild", "verified", True))
        self.assertTrue(final["folder"].startswith("recovered/cerbero-rebuild-"))
        names = {e["name"]: e for e in final["entries"].values()}
        self.assertEqual(sorted(names), ["brief.pdf", "copy.docx", "cover.tif", "layout.indd", "logo.ai"])
        self.assertEqual(names["logo.ai"]["provenance"], "original in the project folder")
        self.assertTrue(names["brief.pdf"]["provenance"].startswith("original in the project folder, moved to"))
        for entry in names.values():
            version = memory.versions[entry["version"]]["sha256"]
            self.assertEqual(hashlib.sha256(nas.content(entry["dest"])).hexdigest(), version)
            checks = VariantC.entry_checks(final, entry)
            self.assertEqual(checks["bytes"], "equal to the source digest observed before copying")
            self.assertEqual(checks["version"], f"equal to approved version {entry['version']}")
        self.assertTrue(names["brief.pdf"]["format"].startswith("opened by document-agent (pdf"))
        self.assertTrue(names["copy.docx"]["format"].startswith("opened by document-agent (docx"))
        self.assertTrue(names["cover.tif"]["format"].startswith("not available"), "no NAS expert opens images")
        self.assertEqual({p: f.data for p, f in nas.files.items() if p in before}, before, "sources only read")

    def test_an_unreadable_original_is_taken_from_an_eligible_copy(self):
        _, nas, _, report, _ = self.rebuild([{"kind": "permission_denied", "prefix": "projects/aurora/logo.ai"}])
        logo = next(e for e in report.final["entries"].values() if e["name"] == "logo.ai")
        self.assertEqual((logo["status"], report.final["set_complete"]), ("verified", True))
        self.assertTrue(logo["provenance"].startswith("copy in "))

    def test_a_member_without_any_readable_source_stays_pending_and_the_rebuild_is_not_complete(self):
        denied = [{"kind": "permission_denied", "prefix": p} for p in
                  ("projects/aurora/logo.ai", "backups/aurora-2026-10-01/logo.ai", "backups/aurora-2026-11-05/logo.ai",
                   "usb-archive/aurora/logo.ai")]
        _, nas, _, report, _ = self.rebuild(denied)
        final = report.final
        logo = next(a for a, e in final["entries"].items() if e["name"] == "logo.ai")
        self.assertEqual(final["entries"][logo]["status"], "no-source")
        self.assertIn("original not readable", final["entries"][logo]["note"])
        self.assertEqual((final["overall"], final["set_complete"], final["pending"]), ("verified", False, [logo]))
        self.assertFalse(nas.exists(f"{final['folder']}/logo.ai"))


if __name__ == "__main__":
    unittest.main()
