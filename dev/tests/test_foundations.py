"""Simulator semantics, record format (R05), copy eligibility (R06) and failure-domain rules."""
import copy
import unittest
from pathlib import Path

from cerbero_lab import records
from cerbero_lab.fixtures import Memory, load
from cerbero_lab.mapping import copy_eligibility, domain_effect, evaluate_set
from cerbero_lab.records import Bundle, check_references, parse, validate
from cerbero_lab.sim import SimFile, SimNAS

DOMAINS = {
    "vol1": {"kind": "volume", "parent": "nas1"},
    "vol2": {"kind": "volume", "parent": "nas1"},
    "nas1": {"kind": "device"},
    "usb1": {"kind": "device"},
}
SHA_A, SHA_B = "a" * 64, "b" * 64


def nas_with(files, **kwargs):
    return SimNAS({p: SimFile(d, 1) for p, d in files.items()}, **kwargs)


class SimulatorTests(unittest.TestCase):
    def test_copy_never_overwrites_and_counts_attempt(self):
        nas = nas_with({"a/x": b"1", "b/x": b"2"})
        result = nas.copy("a/x", "b/x")
        self.assertFalse(result["ok"])
        self.assertEqual(nas.content("b/x"), b"2")
        self.assertEqual(nas.overwrite_attempts, 1)

    def test_state_change_needs_approval_and_declined_changes_nothing(self):
        nas = nas_with({"a/x": b"1"}, approve=lambda op, args: False)
        self.assertEqual(nas.mkdir("r")["error"]["code"], "approval_declined")
        self.assertFalse(nas.exists("r"))
        self.assertEqual((nas.approvals_requested, nas.approvals_declined), (1, 1))

    def test_copy_requires_existing_parent(self):
        nas = nas_with({"a/x": b"1"})
        self.assertEqual(nas.copy("a/x", "r/sub/x")["error"]["code"], "parent_missing")

    def test_exact_size_filter_truncation_and_denied_folders(self):
        nas = nas_with({"p/a": b"12", "p/b": b"12", "p/c": b"123", "p/d/e": b"12"},
                       faults=[{"kind": "permission_denied", "prefix": "p/d"}, {"kind": "list_limit", "limit": 1}])
        result = nas.find("p", size=2)["data"]
        self.assertEqual([e["path"] for e in result["entries"]], ["p/a"])
        self.assertTrue(result["truncated"])
        self.assertEqual(result["denied"], ["p/d"])
        self.assertEqual(nas.sha256("p/d/e")["error"]["code"], "permission_denied")

    def test_mutation_during_copy_and_transient_copy_failure(self):
        nas = nas_with({"a/x": b"old"}, blobs={"new": b"new"},
                       faults=[{"kind": "mutate_on_copy", "src": "a/x", "blob": "new"},
                               {"kind": "copy_fail", "src": "a/x", "times": 1}])
        nas.dirs.add("r")
        self.assertEqual(nas.copy("a/x", "r/x")["error"]["code"], "copy_failed")
        self.assertTrue(nas.copy("a/x", "r/x")["ok"])
        self.assertEqual(nas.content("r/x"), b"new")

    def test_save_requires_an_existing_folder_and_faults_change_the_answer(self):
        nas = nas_with({"m/keep": b"1"}, faults=[{"kind": "save_unverified", "hint_prefix": "CERBERO-PLN"},
                                                 {"kind": "save_incomplete", "hint_prefix": "CERBERO-RCP"}])
        self.assertEqual(nas.save_text("missing", "CERBERO-B", "x")["error"]["code"], "not_found")
        self.assertFalse(nas.save_text("m", "CERBERO-PLN-1", "x")["data"]["verified"])
        self.assertNotIn("outputFile", nas.save_text("m", "CERBERO-RCP-1", "x")["data"])

    def test_links_resolve_to_their_target_and_stat_reports_the_real_path(self):
        nas = nas_with({"private/x": b"secret"}, faults=[{"kind": "link", "path": "backups/x", "target": "private/x"}])
        self.assertEqual(nas.stat("backups/x")["data"]["realpath"], "private/x")
        self.assertEqual(nas.sha256("backups/x")["data"]["realpath"], "private/x")


class RecordFormatTests(unittest.TestCase):
    """R05: the bundle format is reversible and rejects ambiguous or incomplete input explicitly."""

    def round_trip(self, **fields):
        bundle = Bundle("B-0001-01", case_id="CAS-0001")
        bundle.add("CPY-0001-0001", "copy", **fields)
        return parse(bundle.render())["records"]["CPY-0001-0001"]

    def test_apostrophes_commas_spaces_and_unicode_survive(self):
        for path in ["/nas/Cliente O'Neil/foto, final.tif", "proyectos/Año 2026/Ünïcødé — 写真.tif",
                     "a b/  leading and trailing  ", "it's '\"'\"' quoted", "back\\slash/and \"double\""]:
            self.assertEqual(self.round_trip(real_path=path)["real_path"], path)

    def test_multiline_and_delimiter_like_text_survive_on_one_line(self):
        text = "line one\n- type: plan\n## RECORD PLN-9999-01\n# CERBERO BUNDLE X\r\nend\t  \x85"
        bundle = Bundle("B-0001-01")
        bundle.add("CLM-0001-0001", "claim", statement=text)
        rendered = bundle.render()
        self.assertEqual(rendered.count("\n## RECORD "), 1)
        self.assertEqual(len(rendered.splitlines()), len(rendered.split("\n")) - 1, "no hidden line breaks")
        self.assertEqual(parse(rendered)["records"]["CLM-0001-0001"]["statement"], text)

    def test_lists_keep_items_that_contain_commas(self):
        items = ["projects/a, b.tif", "plain", ""]
        self.assertEqual(self.round_trip(depends_on=items)["depends_on"], items)

    def test_parser_rejects_foreign_text_duplicates_and_bad_values(self):
        with self.assertRaises(ValueError):
            parse("# Notes\n- schema: \"cerbero-memory-2\"\n")
        header = '# CERBERO BUNDLE B\n- schema: "cerbero-memory-2"\n- bundle_id: "B"\n- case_id: null\n- scope_id: null\n- supersedes: null\n'
        for body in ['\n## RECORD X\n- type: "a"\n\n## RECORD X\n- type: "b"\n',
                     '\n## RECORD X\n- type: "a"\n- type: "b"\n',
                     '\n## RECORD X\n- type: copy\n',
                     '\n## RECORD X\nfree text\n']:
            with self.assertRaises(ValueError, msg=body):
                parse(header + body)
        with self.assertRaises(ValueError):
            parse(header.replace("cerbero-memory-2", "cerbero-memory-1"))

    def test_validation_names_incomplete_records_and_wrong_kinds(self):
        problems = validate({"CPY-0001-0001": {"type": "copy", "real_path": "x"},
                             "VER-0001-0001": {"type": "version", "asset_id": "AST-0001-0001", "sha256": "nothex",
                                               "size_bytes": "12", "approved_by": None, "observation": "OBS-0001-0001"},
                             "ZZZ-0001-0001": {"type": "unknown-kind"}})
        self.assertTrue(any("incomplete copy record, missing version_id" in p for p in problems))
        self.assertTrue(any("sha256 is not a valid sha256" in p for p in problems))
        self.assertTrue(any("size_bytes is not a valid int" in p for p in problems))
        self.assertTrue(any("unknown record type" in p for p in problems))

    def test_dangling_references_are_reported(self):
        recs = {"VER-0001-0001": {"type": "version", "asset_id": "AST-0001-0009", "sha256": SHA_A, "size_bytes": 1,
                                  "approved_by": None, "observation": "OBS-0001-0001"},
                "OBS-0001-0001": {"type": "observation"}}
        self.assertEqual(check_references(recs), ["VER-0001-0001: reference to missing record AST-0001-0009"])

    def test_the_writer_refuses_unordered_sets_and_duplicate_records(self):
        bundle = Bundle("B-0001-01")
        bundle.add("CLM-0001-0001", "claim", depends_on={"x"})
        with self.assertRaises(TypeError):
            bundle.render()
        with self.assertRaises(ValueError):
            bundle.add("CLM-0001-0001", "claim")

    def test_every_record_type_is_documented_with_the_same_fields(self):
        text = Path("../skill/cerbero-guardian/references/memory-records.md").read_text(encoding="utf-8")
        table = text.split("## Record types and required fields")[1].split("\n## ")[0]
        documented = {}
        for line in table.splitlines():
            cells = [c.strip() for c in line.strip().strip("|").split("|")]
            if len(cells) == 2 and cells[0] in records.RECORD_TYPES:
                documented[cells[0]] = {f.split(" ")[0].strip("`") for f in cells[1].split(", ")}
        for kind, spec in records.RECORD_TYPES.items():
            self.assertEqual(documented.get(kind), set(spec), kind)


def memory_with(copies, versions=None, locations=None, domains=None):
    return Memory(scope_root="p", baseline_time=0, sets={"S": {"members": {"A": "V"}}},
                  versions=versions or {"V": {"asset": "A", "sha256": SHA_A, "size": 1}},
                  locations=locations or {"L": {"root": "bk", "memberships": {"volume": "vol2"}},
                                          "P": {"root": "p", "memberships": {"volume": "vol1"}}},
                  domains=domains or DOMAINS, copies=copies, observations={"OBS-1"})


def good_copy(**changes):
    base = {"id": "C1", "version": "V", "path": "bk/a", "location": "L", "sha256": SHA_A,
            "observation": "OBS-1", "access": "readable", "status": "current"}
    base.update(changes)
    return base


class EligibilityTests(unittest.TestCase):
    """R06: one definition; negative evidence excludes, missing evidence is uncertain."""

    def state(self, copy_record, **kwargs):
        memory = memory_with([copy_record], **kwargs)
        return copy_eligibility(memory, copy_record, "V")

    def test_a_matching_version_id_alone_is_not_enough(self):
        self.assertEqual(self.state(good_copy())["state"], "eligible")
        for change, expected in [({"sha256": SHA_B}, "excluded"), ({"access": "denied"}, "excluded"),
                                 ({"status": "superseded"}, "excluded"), ({"path": "elsewhere/a"}, "excluded"),
                                 ({"path": "bk/../p/a"}, "excluded"), ({"sha256": None}, "uncertain"),
                                 ({"access": "unknown"}, "uncertain"), ({"observation": "OBS-404"}, "uncertain"),
                                 ({"status": "needs-review"}, "uncertain"), ({"location": "L-404"}, "uncertain")]:
            self.assertEqual(self.state(good_copy(**change))["state"], expected, change)

    def test_a_fresh_observation_settles_access_and_provenance_but_not_a_wrong_digest(self):
        memory = memory_with([good_copy(access="unknown", observation=None)])
        self.assertEqual(copy_eligibility(memory, memory.copies[0], "V", observed={"C1": True})["state"], "eligible")
        self.assertEqual(copy_eligibility(memory, memory.copies[0], "V", observed={"C1": False})["state"], "excluded")

    def test_review_probe_wrong_hash_and_denied_access_make_nothing_recoverable(self):
        sc = load("fixtures/scenarios/S03-recent-wrong-copy.json")
        memory = copy.deepcopy(sc.memory)
        for record in memory.copies:
            record.update(sha256="0" * 64, access="denied")
        result = evaluate_set(memory, "SET-D2", {"id": "x", "type": "location", "location": "L-proj"})
        self.assertEqual(result["verdict"], "not-recoverable")
        self.assertEqual({m["eligible"] for m in result["members"].values()}, {0})

    def test_unknown_access_gives_undetermined_not_recoverable(self):
        sc = load("fixtures/scenarios/S03-recent-wrong-copy.json")
        memory = copy.deepcopy(sc.memory)
        for record in memory.copies:
            record["access"] = "unknown"
        result = evaluate_set(memory, "SET-D2", {"id": "x", "type": "location", "location": "L-proj"})
        self.assertEqual(result["verdict"], "undetermined")


class FailureDomainTests(unittest.TestCase):
    def test_same_volume_is_affected(self):
        self.assertEqual(domain_effect({"memberships": {"volume": "vol1"}}, "vol1", DOMAINS), "affected")

    def test_other_volume_and_other_device_are_unaffected_by_inference(self):
        self.assertEqual(domain_effect({"memberships": {"volume": "vol2"}}, "vol1", DOMAINS), "unaffected")
        self.assertEqual(domain_effect({"memberships": {"device": "usb1"}}, "vol1", DOMAINS), "unaffected")

    def test_device_failure_reaches_volumes_on_it(self):
        self.assertEqual(domain_effect({"memberships": {"volume": "vol2"}}, "nas1", DOMAINS), "affected")

    def test_unrecorded_membership_is_uncertain_whatever_the_folder_name(self):
        self.assertEqual(domain_effect({"memberships": {}}, "vol1", DOMAINS), "uncertain")
        self.assertEqual(domain_effect({"memberships": {"device": "nas1"}}, "vol1", DOMAINS), "uncertain")

    def test_contradictory_memberships_are_uncertain_not_independent(self):
        location = {"memberships": {"volume": "vol1", "device": "usb1"}}
        self.assertEqual(domain_effect(location, "vol1", DOMAINS), "uncertain")
        self.assertEqual(domain_effect(location, "usb1", DOMAINS), "uncertain")
        mislabeled = {"memberships": {"volume": "usb1"}}
        self.assertEqual(domain_effect(mislabeled, "vol1", DOMAINS), "uncertain")

    def test_cycles_missing_parents_and_repeated_kinds_are_uncertain(self):
        cycle = {"v": {"kind": "volume", "parent": "d"}, "d": {"kind": "device", "parent": "v"}}
        self.assertEqual(domain_effect({"memberships": {"volume": "v"}}, "v", cycle), "uncertain")
        orphan = {"v": {"kind": "volume", "parent": "gone"}}
        self.assertEqual(domain_effect({"memberships": {"volume": "v"}}, "v", orphan), "uncertain")
        repeated = {"v1": {"kind": "volume", "parent": "v2"}, "v2": {"kind": "volume"}}
        self.assertEqual(domain_effect({"memberships": {"volume": "v1"}}, "v2", repeated), "uncertain")
        self.assertEqual(domain_effect({"memberships": {"volume": "vol1"}}, "unrecorded", DOMAINS), "uncertain")

    def test_a_contradictory_topology_never_counts_as_redundancy(self):
        domains = dict(DOMAINS, vol2={"kind": "volume", "parent": "vol2b"}, vol2b={"kind": "device", "parent": "vol2"})
        memory = memory_with([good_copy()], domains=domains)
        result = evaluate_set(memory, "S", {"id": "v", "type": "domain", "domain": "vol1"})
        self.assertEqual(result["verdict"], "undetermined")
        self.assertEqual(result["members"]["A"]["eligible"], 0)

    def test_nested_folder_is_lost_with_its_parent_location(self):
        scenario = load("fixtures/scenarios/S05-shared-failure-domain.json")
        result = evaluate_set(scenario.memory, "SET-D2", {"id": "x", "type": "location", "location": "L-proj"})
        self.assertEqual({m["eligible"] for m in result["members"].values()}, {1})

    def test_incomplete_inventory_blocks_not_recoverable(self):
        memory = Memory(scope_root="p", baseline_time=0, sets={"S": {"members": {"A": "V"}}},
                        locations={"L": {"root": "p", "memberships": {"volume": "vol1"}}}, domains=DOMAINS,
                        copies=[{"id": "C1", "version": "V", "path": "p/a", "location": "L", "status": "current"}])
        scenario = {"id": "v", "type": "domain", "domain": "vol1"}
        self.assertEqual(evaluate_set(memory, "S", scenario)["verdict"], "not-recoverable")
        memory.incomplete_locations = {"L2"}
        self.assertEqual(evaluate_set(memory, "S", scenario)["verdict"], "undetermined")


if __name__ == "__main__":
    unittest.main()
