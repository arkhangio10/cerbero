"""Persistence across sessions, using only files written to disk between sessions.

Baseline -> save -> export -> close -> load only the persisted files -> investigate -> recover ->
another session loads the new files and reviews the result. No Memory object crosses a session.
"""
import hashlib
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from cerbero_lab import grader
from cerbero_lab.fixtures import load
from cerbero_lab.persistence import load_memory
from cerbero_lab.pipeline import baseline_session, correspondence, declarations, with_memory
from cerbero_lab.records import Bundle, parse
from cerbero_lab.sim import SimFile, SimNAS, inside
from cerbero_lab.variants import VariantC

ROOT = "cerbero-memory"


def scenario(name):
    return load(f"fixtures/scenarios/{name}.json")


def to_disk(files: dict[str, bytes], directory: str) -> None:
    for name, data in files.items():
        Path(directory, name).write_bytes(data)


def from_disk(directory: str) -> dict[str, bytes]:
    return {p.name: p.read_bytes() for p in sorted(Path(directory).glob("CERBERO-*.md"))}


def memory_files(nas) -> dict[str, bytes]:
    return {Path(p).name: nas.content(p) for p in sorted(nas.files) if inside(p, ROOT)}


def session(sc, files: dict[str, bytes], nas=None, **kwargs):
    """Open a new session on a NAS whose memory folder holds exactly these files."""
    nas = with_memory(sc, files, nas)
    memory, info = load_memory(nas, ROOT, sc.location_root(sc.request["scope"]))
    return VariantC(sc, nas, memory, session=info, **kwargs), memory, info, nas


def after_session(sc, nas, files: dict[str, bytes]):
    """The same NAS contents without its memory folder, which is replaced by files read back from disk."""
    kept = {p: SimFile(f.data, f.mtime) for p, f in nas.files.items() if not inside(p, ROOT)}
    fresh = sc.build_nas(files=kept)
    for folder in nas.dirs:
        fresh.dirs.add(folder)
    return with_memory(sc, files, fresh)


def all_records(files: dict[str, bytes]):
    bundles = {name: parse(data.decode("utf-8")) for name, data in files.items()}
    ids = [rid for b in bundles.values() for rid in b["records"]]
    return bundles, ids


class CrossSession(unittest.TestCase):
    def test_baseline_incident_recovery_and_review_in_three_sessions(self):
        sc = scenario("S00-demo-aurora")
        with tempfile.TemporaryDirectory() as disk1, tempfile.TemporaryDirectory() as disk2:
            files, _, _ = baseline_session(sc)
            to_disk(files, disk1)
            del files

            variant, memory, info, nas2 = session(sc, from_disk(disk1))
            self.assertIsNot(memory, sc.memory)
            self.assertTrue(all(a.startswith("AST-0001-") for a in memory.assets), list(memory.assets))
            self.assertFalse({"A-layout", "SET-D2", "L-proj", "DOM-vol1"} & (set(memory.assets) | set(memory.sets)
                                                                           | set(memory.locations) | set(memory.domains)))
            self.assertEqual(info.next_case, 2)
            report = variant.run()
            key = correspondence(sc, memory)
            states = {key[a]: s for a, s in report.states.items() if a in key}
            for aid, expected in sc.expected["states"].items():
                self.assertIn(states[aid], (expected, "intact-metadata" if expected == "intact" else expected), aid)
            self.assertEqual((report.final["overall"], report.final["set_complete"]), ("verified", True))
            outside = [memory.assets[a]["name"] for a in report.final["outside"]]
            self.assertEqual(outside, ["DSC_0142.ARW"], "a changed file outside Delivery 2 is reported apart")
            to_disk(memory_files(nas2), disk2)

            files3 = from_disk(disk2)
            nas3 = after_session(sc, nas2, files3)
            memory3, info3 = load_memory(nas3, ROOT, sc.location_root(sc.request["scope"]))
            self.assertEqual(info3.next_case, 3)
            self.assertEqual([p for p, i in info3.files.items() if i["status"] == "needs-review"], [])
            self.assertEqual(info3.unfinished_plans, [])
            receipts = [r for r in info3.records.values() if r["type"] == "receipt"]
            self.assertEqual([(r["overall"], r["set_complete"]) for r in receipts], [("verified", True)])
            self.assertEqual([memory3.assets[a]["name"] for a in receipts[0]["outside_target"]], ["DSC_0142.ARW"])
            verified = [r for r in info3.records.values() if r["type"] == "receipt-entry" and r["status"] == "verified"]
            self.assertEqual(len(verified), 3)
            for entry in verified:
                plan_entry = info3.records[entry["entry_id"]]
                seen = nas3.sha256(entry["destination_path"])["data"]["sha256"]
                self.assertEqual(seen, entry["destination_sha256"])
                self.assertEqual(seen, plan_entry["expected_sha256"])
                self.assertEqual(seen, info3.records[plan_entry["version_id"]]["sha256"])

            third = VariantC(sc, nas3, memory3, session=info3, intent="investigate").run()
            self.assertTrue(third.persisted)
            final_files = memory_files(nas3)
            bundles, ids = all_records(final_files)
            self.assertEqual(len(ids), len(set(ids)), "record IDs are unique across sessions")
            bundle_ids = [b["header"]["bundle_id"] for b in bundles.values()]
            self.assertEqual(len(bundle_ids), len(set(bundle_ids)))
            self.assertTrue(any(rid.startswith("CLM-0003-") for rid in ids))
            newest = max((n for n in bundles if "IDX" in n), key=lambda n: bundles[n]["header"]["bundle_id"])
            listed = {Path(r["file"]).name: r for r in bundles[newest]["records"].values()}
            for name, data in final_files.items():
                if name == newest:
                    continue
                self.assertIn(name, listed, "the newest index lists every other memory file")
                if listed[name]["status"] == "current":
                    self.assertEqual(listed[name]["sha256"], hashlib.sha256(data).hexdigest(), name)

    def test_superseding_records_carry_contradictions_to_the_next_session(self):
        sc = scenario("S14-stale-memory-provenance")
        files, _, _ = baseline_session(sc)
        variant, _, _, nas = session(sc, files)
        report = variant.run()
        self.assertEqual(len(report.revalidated), 2)
        memory3, info3 = load_memory(after_session(sc, nas, memory_files(nas)), ROOT, sc.location_root("L-proj"))
        stale = [c for c in memory3.copies if c["path"] == "backups/aurora-2026-10-01/cover.tif"]
        self.assertEqual([c["status"] for c in stale], ["needs-review"])
        self.assertEqual(sorted(c["status"] for c in memory3.claims if c["kind"] == "recoverability"),
                         ["needs-review", "needs-review"])
        superseded = {r["supersedes"] for r in info3.records.values() if r.get("supersedes")}
        self.assertFalse(superseded & set(info3.records), "superseded records are not active")

    def test_an_unsaved_index_leaves_the_session_files_for_review_without_reusing_ids(self):
        sc = scenario("S03-recent-wrong-copy")
        sc.faults.append({"kind": "save_fail", "hint_prefix": "CERBERO-IDX-0002"})
        files, _, _ = baseline_session(sc)
        variant, _, _, nas = session(sc, files)
        report = variant.run()
        self.assertIn("index-not-persisted", report.acknowledged)
        variant3, memory3, info3, _ = session(sc, memory_files(nas), after_session(sc, nas, {}))
        review = {Path(p).name: i for p, i in info3.files.items() if i["status"] == "needs-review"}
        session2 = sorted(Path(p).name for p in nas.files if Path(p).name.startswith("CERBERO-B-0002-"))
        self.assertGreaterEqual(len(session2), 2)
        self.assertEqual(sorted(review), session2)
        self.assertFalse([r for r in info3.records.values() if r["type"] == "receipt"])
        self.assertEqual(info3.next_case, 3)
        self.assertTrue(any("needs review" in item for item in variant3.report.open_items))
        self.assertIsNotNone(memory3)

    def test_a_restart_after_the_plan_is_reported_and_a_new_plan_gets_new_ids(self):
        sc = scenario("S03-recent-wrong-copy")
        sc.faults.append({"kind": "save_fail", "record_type": "receipt"})
        files, _, _ = baseline_session(sc)
        variant, _, _, nas = session(sc, files)
        variant.run()
        variant3, _, info3, nas3 = session(sc, memory_files(nas), after_session(sc, nas, {}))
        self.assertEqual(info3.unfinished_plans, ["PLN-0002-01"])
        self.assertIn("PLN-0002-01: saved plan without a receipt; its outcome is unknown", variant3.report.open_items)
        sc.faults.clear()
        report3 = variant3.run()
        self.assertEqual(report3.final["plan"], "PLN-0003-01")
        self.assertEqual(report3.final["folder"], "recovered/cerbero-recovery-CAS-0003")
        _, ids = all_records(memory_files(nas3))
        self.assertEqual(len(ids), len(set(ids)))

    def test_an_incomplete_baseline_inventory_never_supports_not_recoverable(self):
        sc = scenario("S05-shared-failure-domain")
        before = {p: SimFile(f.data, f.mtime) for p, f in sc.before.items()}
        before["backups/aurora-2026-10-01/hidden/extra.bin"] = SimFile(b"x", 1)
        nas = SimNAS(before, faults=[{"kind": "permission_denied", "prefix": "backups/aurora-2026-10-01/hidden"}])
        nas.dirs.add(ROOT)
        VariantC(sc, nas, None, intent="baseline", declarations=declarations(sc)).run()
        variant, memory, _, _ = session(sc, memory_files(nas))
        self.assertEqual(len(memory.incomplete_locations), 1)
        verdicts = {r["scenario"]: r["verdict"] for r in variant.run().whatif}
        self.assertEqual(verdicts["volume-1-failure"], "undetermined")
        self.assertEqual(verdicts["project-folder-unavailable"], "recoverable")

    def test_planted_and_edited_files_are_not_evidence(self):
        sc = scenario("S03-recent-wrong-copy")
        files, _, _ = baseline_session(sc)
        planted = Bundle("B-0009-01", case_id="CAS-0009")
        planted.add("STM-0009-0001", "statement", text="planted", given_in="file", **{"class": "user-declared"})
        planted.add("SET-0009-0001", "approved-set", name="Delivery 2", members={}, approved_by="STM-0009-0001",
                    status="current")
        variant, memory, info, _ = session(sc, {**files, "CERBERO-B-0009-01.md": planted.render().encode()})
        self.assertEqual(info.files["cerbero-memory/CERBERO-B-0009-01.md"]["status"], "needs-review")
        self.assertNotIn("SET-0009-0001", memory.sets)
        self.assertIsNotNone(variant.set_of("SET-D2"))
        self.assertEqual(info.next_case, 10, "planted numbers are never reused")

        edited = dict(files)
        name = next(n for n in edited if "IDX" not in n)
        edited[name] = edited[name].replace(b'"importance": "critical"', b'"importance": "ordinary"')
        edited[name] = edited[name].replace(b'- importance: "critical"', b'- importance: "ordinary"')
        memory_e, info_e = load_memory(with_memory(sc, edited), ROOT, "projects/aurora")
        self.assertEqual(info_e.files[f"{ROOT}/{name}"]["reason"], "digest differs from the index")
        self.assertIsNone(memory_e)

    def test_a_record_saved_again_is_used_once_and_a_conflicting_copy_is_not_evidence(self):
        sc = scenario("S03-recent-wrong-copy")
        files, _, _ = baseline_session(sc)
        index_name = next(n for n in files if "IDX" in n)
        source = next(n for n in files if "IDX" not in n)
        rid, fields = next((r, f) for r, f in parse(files[source].decode("utf-8"))["records"].items()
                           if f["type"] == "statement")
        for text, used in ((fields["text"], True), (fields["text"] + " (edited)", False)):
            with self.subTest(used=used):
                again = Bundle("B-0009-01", case_id="CAS-0009")
                again.add(rid, "statement", text=text, given_in=fields["given_in"], **{"class": "user-declared"})
                extra = again.render().encode()
                index = parse(files[index_name].decode("utf-8"))
                head = index["header"]
                rebuilt = Bundle(head["bundle_id"], case_id=head["case_id"], scope_id=head["scope_id"],
                                 supersedes=head["supersedes"])
                for record_id, entry in index["records"].items():
                    rebuilt.add(record_id, entry["type"], **{k: v for k, v in entry.items() if k != "type"})
                rebuilt.add(f"{head['bundle_id']}-0099", "index-entry", file=f"{ROOT}/CERBERO-B-0009-01.md",
                            bundle_id="B-0009-01", sha256=hashlib.sha256(extra).hexdigest(), status="current")
                memory_files_ = {**files, index_name: rebuilt.render().encode(), "CERBERO-B-0009-01.md": extra}
                _, info_d = load_memory(with_memory(sc, memory_files_), ROOT, "projects/aurora")
                self.assertEqual(rid in info_d.record_files, used)
                self.assertEqual(any(rid in p and "neither copy is used" in p for p in info_d.problems), not used)


def changes(nas):
    return nas.calls["mkdir"], nas.calls["copy"]


class Limits(unittest.TestCase):
    """Listing, size and byte limits, restarts and collisions. The budgets are design defaults of the lab and the
    Skill; the device limits of UGOS are unknown until measured (NAS checklist)."""

    def test_more_than_200_memory_files_are_inventoried_by_partition_and_indexed_in_parts(self):
        sc = scenario("S03-recent-wrong-copy")
        files, _, _ = baseline_session(sc)
        extra = {}
        for n in range(2, 252):
            bundle = Bundle(f"B-{n:04d}-01", case_id=f"CAS-{n:04d}", scope_id=None)
            bundle.add(f"OPN-{n:04d}-0001", "open-item", subject="history", reason=f"session {n}", needed_to_resolve="none")
            extra[f"CERBERO-B-{n:04d}-01.md"] = bundle.render().encode()
        nas = with_memory(sc, {**files, **extra})
        memory, info = load_memory(nas, ROOT, "projects/aurora", confirmed=tuple(extra))
        self.assertFalse(info.inventory_complete, "the full listing was truncated: other prefixes cannot be ruled out")
        self.assertTrue(info.index_file.endswith("CERBERO-IDX-0001-01.md"))
        self.assertEqual(sum(i["status"] == "current" for i in info.files.values()), 252)
        self.assertEqual(info.next_case, 252)
        self.assertLessEqual(info.listings, 60)
        report = VariantC(sc, nas, memory, session=info).run()
        self.assertEqual(report.final["overall"], "verified")
        parts = sorted(p for p in nas.files if "CERBERO-IDX-0252-" in p)
        self.assertGreater(len(parts), 1, "an index of 260 files does not fit one bundle")
        self.assertTrue(all(len(nas.content(p)) <= 16 * 1024 for p in parts))
        memory2, info2 = load_memory(nas, ROOT, "projects/aurora")
        self.assertEqual([p for p, i in info2.files.items() if i["status"] == "needs-review"], [])
        self.assertEqual(info2.next_case, 253)
        self.assertEqual(len(info2.unfinished_plans), 0)

    def test_an_index_series_listed_only_in_part_is_never_taken_as_the_newest(self):
        sc = scenario("S03-recent-wrong-copy")
        files, _, _ = baseline_session(sc)
        older = next(n for n in files if "IDX" in n)
        nas = with_memory(sc, {**files, "CERBERO-IDX-0000-01.md": files[older].replace(b"IDX-0001-01", b"IDX-0000-01")})
        nas.faults.append({"kind": "list_limit", "limit": 1})
        from cerbero_lab import persistence
        with mock.patch.object(persistence, "LISTING_BUDGET", 4):
            memory, info = load_memory(nas, ROOT, "projects/aurora")
        self.assertIsNone(info.index_file)
        self.assertIsNone(memory)
        self.assertTrue(any("index snapshots not completely listed" in p for p in info.problems), info.problems)
        self.assertLessEqual(info.listings, 4)

    def test_a_memory_file_returned_in_part_is_not_evidence(self):
        sc = scenario("S03-recent-wrong-copy")
        files, _, _ = baseline_session(sc)
        nas = with_memory(sc, files)
        nas.faults.append({"kind": "truncate_read", "prefix": f"{ROOT}/CERBERO-B-0001-02.md", "bytes": 300})
        _, info = load_memory(nas, ROOT, "projects/aurora")
        self.assertEqual(info.files[f"{ROOT}/CERBERO-B-0001-02.md"]["reason"], "returned only in part (300 bytes)")

    def test_a_save_that_stores_fewer_bytes_than_sent_is_not_persisted(self):
        sc = scenario("S03-recent-wrong-copy")
        sc.faults.append({"kind": "save_partial", "record_type": "plan"})
        files, _, _ = baseline_session(sc)
        variant, _, _, nas = session(sc, files)
        report = variant.run()
        self.assertEqual(changes(nas), (0, 0))
        self.assertIn("incomplete save", report.final["reason"])
        _, info = load_memory(nas, ROOT, "projects/aurora")
        half = [p for p, i in info.files.items() if i["status"] == "needs-review"]
        self.assertTrue(half, "the half-written files (the plan, and the receipt that carries it) are never evidence")
        self.assertFalse([r for r in info.records.values() if r["type"] in ("plan", "plan-entry")])

    def test_large_bundles_are_split_into_whole_fragments_and_the_plan_binds_them(self):
        from cerbero_lab import variants
        sc = scenario("S00-demo-aurora")
        sc.faults.append({"kind": "save_size_limit", "bytes": 2600})
        with mock.patch.object(variants, "MAX_BUNDLE_BYTES", 1500):
            files, _, _ = baseline_session(sc)
            variant, _, _, nas = session(sc, files)
            report = variant.run()
        self.assertNotIn("not-persisted", report.acknowledged)
        self.assertEqual((report.final["overall"], report.final["set_complete"]), ("verified", True))
        self.assertTrue(report.final["fragments"], "plan entries were saved as fragments bound by digest")
        for path, digest in report.final["fragments"].items():
            self.assertEqual(hashlib.sha256(nas.content(path)).hexdigest(), digest)
        _, info = load_memory(nas, ROOT, "projects/aurora")
        self.assertEqual([p for p, i in info.files.items() if i["status"] == "needs-review"], [])
        with tempfile.TemporaryDirectory() as tmp:
            to_disk(memory_files(nas), tmp)
            graded = grader.grade(Path(tmp), sc, read_file=nas.content)
        self.assertEqual((graded["parse_errors"], graded["integrity_problems"]), ([], []))

        unsplit = scenario("S00-demo-aurora")
        unsplit.faults.append({"kind": "save_size_limit", "bytes": 2600})
        with mock.patch.object(variants, "MAX_BUNDLE_BYTES", 10 ** 6):
            files, _, _ = baseline_session(scenario("S00-demo-aurora"))
            variant, _, _, nas = session(unsplit, files)
            report = variant.run()
        self.assertEqual(changes(nas), (0, 0))
        self.assertIn("too_large", report.final["reason"])

    def test_a_plan_fragment_changed_after_approval_invalidates_the_plan(self):
        from cerbero_lab import variants

        class Tamper(dict):
            def get(self, key, default=None):
                if key == "approve_plan":
                    fragment = next(p for p in nas.files if "CERBERO-B-0002-" in p and b'"plan-entry"' in nas.content(p))
                    nas.files[fragment] = SimFile(nas.content(fragment).replace(b"layout.indd", b"layout.inde"), 1)
                return super().get(key, default)

        sc = scenario("S00-demo-aurora")
        with mock.patch.object(variants, "MAX_BUNDLE_BYTES", 1500):
            files, _, _ = baseline_session(sc)
            variant, _, _, nas = session(sc, files)
            variant.answers = Tamper(variant.answers)
            report = variant.run()
        self.assertEqual(report.final["overall"], "invalidated")
        self.assertEqual(changes(nas), (0, 0))

    def test_a_crash_before_the_index_leaves_the_files_for_review_and_ids_fresh(self):
        sc = scenario("S03-recent-wrong-copy")
        files, _, _ = baseline_session(sc)
        variant, _, _, nas = session(sc, files)
        with mock.patch.object(VariantC, "finish", lambda self: None):
            variant.run()
        variant3, memory3, info3, nas3 = session(sc, memory_files(nas), after_session(sc, nas, {}))
        review = sorted(Path(p).name for p, i in info3.files.items() if i["status"] == "needs-review")
        self.assertEqual(review, sorted(Path(p).name for p in nas.files if "CERBERO-B-0002-" in p))
        self.assertEqual(info3.next_case, 3)
        self.assertFalse([r for r in info3.records.values() if r["type"] in ("plan", "receipt")])
        variant3.run()
        _, ids = all_records(memory_files(nas3))
        self.assertEqual(len(ids), len(set(ids)))

    def test_two_sessions_opened_on_the_same_memory_never_overwrite_each_other(self):
        sc = scenario("S03-recent-wrong-copy")
        files, _, _ = baseline_session(sc)
        nas = with_memory(sc, files)
        first_memory, first_info = load_memory(nas, ROOT, "projects/aurora")
        second_memory, second_info = load_memory(nas, ROOT, "projects/aurora")
        VariantC(sc, nas, first_memory, session=first_info).run()
        written = {p: nas.content(p) for p in nas.files if "-0002-" in p}
        report = VariantC(sc, nas, second_memory, session=second_info).run()
        self.assertEqual({p: nas.content(p) for p in written}, written)
        self.assertTrue(any(item.endswith("not persisted (exists)") for item in report.open_items))
        self.assertEqual(report.final["overall"], "failed", "its plan could not be saved under a free name")

    def test_session_budgets_stop_investigation_and_keep_the_recovery_reserve(self):
        from cerbero_lab import variants
        sc = scenario("S06-permission-denied-incomplete-inventory")
        files, _, _ = baseline_session(sc)
        variant, _, _, nas = session(sc, files)
        variant.run()
        self.assertLessEqual(variant.listings, variants.LISTING_BUDGET)

        sc = scenario("S00-demo-aurora")
        files, _, _ = baseline_session(sc)
        with mock.patch.object(variants, "DIGEST_BUDGET", 24), mock.patch.object(variants, "DIGEST_RESERVE", 20):
            variant, _, _, nas = session(sc, files)
            report = variant.run()
        self.assertLessEqual(variant.digest_count, 24)
        self.assertTrue(report.coverage["budget_exhausted"])
        with mock.patch.object(variants, "DIGEST_BUDGET", 12), mock.patch.object(variants, "DIGEST_RESERVE", 0):
            variant, _, _, nas = session(scenario("S00-demo-aurora"), files)
            report = variant.run()
        self.assertIn("does not cover the essential checks", report.final["reason"])
        self.assertIn("budget", report.acknowledged)
        self.assertEqual(changes(nas), (0, 0))
        with mock.patch.object(variants, "BYTE_BUDGET", 60_000), mock.patch.object(variants, "BYTE_RESERVE", 0):
            variant, _, _, nas = session(scenario("S00-demo-aurora"), files)
            variant.run()
        self.assertLessEqual(variant.bytes_hashed, 60_000)


def documented_trace(prefix: str, sc) -> dict[str, bytes]:
    """Memory written by hand from references/memory-records.md, with real-looking IDs and a NAS prefix."""
    layout = sc.blob_sha["layout-v2"]
    root = f"{prefix}/projects/aurora"
    base = Bundle("B-0007-01", case_id="CAS-0007", scope_id="SCP-0003")
    base.add("STM-0007-0001", "statement", text="Delivery 2 is approved.", given_in="this session",
             **{"class": "user-declared"})
    base.add("OBS-0007-0001", "observation", check_card=None, agent="file-agent", delegation="D7", state="completed",
             result="digests of 5 files", coverage="5 of 5", observed_at="unknown", **{"class": "observed"})
    base.add("SCP-0003", "scope", real_root=root, name="aurora", authorized_by="STM-0007-0001", newest_mtime=None)
    names = {"A-brief": "brief.pdf", "A-layout": "layout.indd", "A-copy": "copy.docx", "A-cover": "cover.tif",
             "A-logo": "logo.ai"}
    ids = {}
    for n, (key, name) in enumerate(names.items(), start=1):
        aid, vid = f"AST-0007-{n:04d}", f"VER-0007-{n:04d}"
        ids[key] = aid
        digest = sc.memory.versions[sc.memory.assets[key]["current"]]["sha256"]
        base.add(aid, "asset", scope_id="SCP-0003", name=name, recorded_path=f"{root}/{name}", importance="critical",
                 declared_by="STM-0007-0001", current_version=vid, recorded_size=1, recorded_mtime=None,
                 observation="OBS-0007-0001")
        base.add(vid, "version", asset_id=aid, sha256=digest, size_bytes=1, approved_by="STM-0007-0001",
                 observation="OBS-0007-0001")
    base.add("SET-0007-0001", "approved-set", name="Delivery 2",
             members={ids[k]: f"VER-0007-{n:04d}" for n, k in enumerate(names, start=1)},
             approved_by="STM-0007-0001", status="current")
    case = Bundle("B-0008-01", case_id="CAS-0008", scope_id="SCP-0003")
    case.add("CAS-0008", "case", scope_id="SCP-0003", request="investigate-recover", status="open", opened_in="this session")
    for key, aid in ids.items():
        case.add(f"CLM-0008-{len(case.records) + 1:04d}", "claim", kind="asset-state", subject=aid,
                 asset_state="missing" if key == "A-layout" else "intact", located_at=None, statement="as observed",
                 supports=["OBS-0007-0001"], contradicts=[], depends_on=["OBS-0007-0001"], status="current",
                 **{"class": "observed"})
    folder = f"{prefix}/recovered/cerbero-recovery-CAS-0008"
    case.add("PLN-0008-01", "plan", case_id="CAS-0008", revision=1, reference="approved-version",
             target_set="SET-0007-0001", recovery_folder=folder, goal="recover Delivery 2", preconditions="as written",
             success_conditions="as written", risks="as written", pending=[], previous_receipt=None, supersedes_plan=None)
    case.add("ENT-0008-01-01", "plan-entry", plan_id="PLN-0008-01", asset_id=ids["A-layout"], name="layout.indd",
             version_id="VER-0007-0002", expected_sha256=layout, size_bytes=16384,
             source_path=f"{prefix}/backups/aurora-2026-10-01/layout.indd", destination_path=f"{folder}/layout.indd")
    receipt = Bundle("B-0008-02", case_id="CAS-0008", scope_id="SCP-0003")
    receipt.add("APR-0008-01", "approval", plan_id="PLN-0008-01", plan_sha256="c" * 64, decision="granted",
                statement="Yes, approve PLN-0008-01 with digest cccc...cccc")
    receipt.add("RCP-0008-01", "receipt", plan_id="PLN-0008-01", plan_sha256="c" * 64, overall="verified",
                reference="approved-version", set_complete=True, coverage="1 of 1 entries", pending=[], reason=None)
    receipt.add("REN-0008-01-01", "receipt-entry", receipt_id="RCP-0008-01", entry_id="ENT-0008-01-01",
                asset_id=ids["A-layout"], version_id="VER-0007-0002", status="verified",
                destination_path=f"{folder}/layout.indd", source_sha256_before=layout, destination_sha256=layout,
                source_sha256_after=None, note="")
    files = {f"CERBERO-{b.header['bundle_id']}.md": b.render().encode() for b in (base, case, receipt)}
    index = Bundle("IDX-0008-01", case_id="CAS-0008", scope_id="SCP-0003")
    for n, (name, data) in enumerate(files.items(), start=1):
        index.add(f"IDX-0008-01-{n:04d}", "index-entry", file=f"{prefix}/cerbero-memory/{name}",
                  bundle_id=name[8:-3], sha256=hashlib.sha256(data).hexdigest(), status="current")
    files["CERBERO-IDX-0008-01.md"] = index.render().encode()
    return files


class GraderContract(unittest.TestCase):
    def test_a_trace_written_from_the_documentation_grades_with_real_ids_and_prefix(self):
        sc = scenario("S03-recent-wrong-copy")
        prefix = "/volume1/studio share"
        recovered = {f"{prefix}/recovered/cerbero-recovery-CAS-0008/layout.indd": sc.blobs["layout-v2"]}
        with tempfile.TemporaryDirectory() as tmp:
            to_disk(documented_trace(prefix, sc), tmp)
            result = grader.grade(Path(tmp), sc, read_file=recovered.get)
        self.assertEqual((result["parse_errors"], result["integrity_problems"]), ([], []))
        self.assertEqual(result["passed"], result["total"], [c for c in result["checks"] if not c["pass"]])
        self.assertEqual(result["files_checked"], 1)
        self.assertEqual(result["case"], "CAS-0008")

    def test_a_receipt_entry_without_its_documented_fields_is_an_integrity_problem(self):
        sc = scenario("S03-recent-wrong-copy")
        files = documented_trace("/volume1/x", sc)
        name = "CERBERO-B-0008-02.md"
        files[name] = files[name].replace(b'- receipt_id: "RCP-0008-01"\n', b"")
        with tempfile.TemporaryDirectory() as tmp:
            to_disk(files, tmp)
            result = grader.grade(Path(tmp), sc)
        self.assertTrue(any("missing receipt_id" in p for p in result["integrity_problems"]))


if __name__ == "__main__":
    unittest.main()
