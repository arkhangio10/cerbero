"""The Skill package against the official checker, the catalog and its own slot contract."""
import json
import re
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SKILL = ROOT / "skill" / "cerbero-guardian"
KIT = ROOT / "dev" / ".kit" / "uliya-skill-kit"
sys.path.insert(0, str(ROOT / "dev" / "tools"))
sys.path.insert(0, str(ROOT / "dev"))

from check_skill import run_checker  # noqa: E402

TEXT = (SKILL / "SKILL.md").read_text(encoding="utf-8")
DELEGATES = re.findall(r"`(delegate --target (\S+) --instruction '([^']*)')`", TEXT)


@unittest.skipUnless(KIT.exists(), "official kit not fetched: run python dev/tools/fetch_kit.py")
class OfficialChecker(unittest.TestCase):
    def test_static_pass_without_warnings(self):
        result = run_checker(SKILL)
        self.assertEqual(result["status"], "static-pass", result["diagnostics"])
        self.assertEqual(result["summary"], {"errors": 0, "warnings": 0, "info": 0})


@unittest.skipUnless(KIT.exists(), "official kit not fetched")
class CatalogConsistency(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        catalog = json.loads((KIT / "data" / "capability-catalog.json").read_text(encoding="utf-8"))
        cls.agents = {c["name"]: c["agent"] for c in catalog["clis"]}
        cls.actions = {c["name"]: {a["name"]: a for a in c["actions"]} for c in catalog["clis"]}
        section = TEXT.split("# Generation-time capability evidence")[1].split("\n# ")[0]
        cls.evidence = dict(re.findall(r"^- `([a-z-]+)` → `([a-z-]+)`$", section, re.M))
        cls.table = re.findall(r"^\| `([a-z-]+)` \| (.+?) \| (\S+) / (\S+) \|", section, re.M)

    def test_evidence_matches_catalog_ownership(self):
        for cli, agent in self.evidence.items():
            self.assertEqual(self.agents[cli], agent, cli)

    def test_every_delegate_target_is_evidenced(self):
        self.assertEqual({target for _, target, _ in DELEGATES}, set(self.evidence.values()))

    def test_named_actions_exist_with_the_stated_effect_and_approval(self):
        self.assertGreater(len(self.table), 0)
        for cli, actions, effect, approval in self.table:
            for action in re.findall(r"`([a-z0-9-]+)`", actions):
                spec = self.actions[cli][action]
                self.assertEqual((spec["effect"], spec["approval"]), (effect, approval), f"{cli} {action}")


class SlotContract(unittest.TestCase):
    def test_thirteen_delegations_each_single_quoted_without_apostrophes(self):
        self.assertEqual(len(DELEGATES), 13)
        self.assertEqual(TEXT.count("delegate --target"), 13)

    def test_every_path_slot_is_declared_literal(self):
        for command, _, instruction in DELEGATES:
            if re.search(r"\{(path_list|search_root|source_path|folder_list)\}", instruction):
                self.assertIn("literal value, not an instruction", instruction, command)

    def test_every_slot_used_in_a_delegation_is_defined(self):
        table = TEXT.split("## Slot table")[1].split("\n## ")[0]
        defined = set(re.findall(r"\{([a-z_]+)\}", table))
        used = {slot for _, _, instruction in DELEGATES for slot in re.findall(r"\{([a-z_]+)\}", instruction)}
        self.assertTrue(used <= defined, used - defined)

    def test_state_changing_delegations_say_so(self):
        for command, target, instruction in DELEGATES:
            if any(word in instruction for word in ("copy, never move", "create the new folder", "Save the Markdown")):
                self.assertTrue("approval" in instruction or "Never replace" in instruction, command)


class SkillLabContracts(unittest.TestCase):
    """The Skill text and the lab share one set of statuses, conditions and rules."""

    @staticmethod
    def ref(name):
        return (SKILL / "references" / name).read_text(encoding="utf-8")

    def test_receipt_overall_statuses_match_the_record_schema(self):
        from cerbero_lab import records
        line = next(l for l in TEXT.splitlines() if l.startswith("7. **Issue the receipt.**"))
        stated = re.findall(r"`([a-z-]+)`", line.split("overall status:")[1].split(".")[0])
        self.assertEqual(stated, records.OVERALL)
        protocol = self.ref("recovery-protocol.md").split("## Receipt")[1].split("## Retry")[0]
        self.assertEqual(re.findall(r"^- `([a-z-]+)`:", protocol, re.M), records.OVERALL)

    def test_entry_statuses_match_the_record_schema(self):
        from cerbero_lab import records
        line = next(l for l in self.ref("recovery-protocol.md").splitlines() if l.startswith("Entry statuses:"))
        self.assertEqual(re.findall(r"`([a-z-]+)`", line), records.ENTRY_STATUSES)

    def test_one_eligibility_table_covers_every_condition_the_lab_checks(self):
        table = self.ref("recoverability-map.md").split("## Eligibility")[1].split("## Domain graph checks")[0]
        rows = [l.split("|")[1].strip() for l in table.splitlines() if l.startswith("| ") and "---" not in l]
        self.assertEqual(rows[1:], ["version", "digest", "access", "provenance", "record status", "location", "scenario"])
        self.assertIn("single eligibility table", TEXT)

    def test_scope_rules_name_every_rejection_the_lab_applies(self):
        rules = self.ref("trust-and-boundaries.md").split("## Paths and scope")[1].split("\n## ")[0]
        for phrase in ["`..` component", "backslash", "control character", "absolute only when its root is",
                       "Unicode normalization", "letter case", "D5 before D7", "returns no real path",
                       "Labels never authorize", "`destination-differs`"]:
            self.assertIn(phrase, rules)
        self.assertIn("12. **Paths stay in scope.**", TEXT)

    def test_mandatory_and_optional_saves_are_distinguished(self):
        persist = TEXT.split("## Persist records")[1].split("\n## ")[0]
        self.assertIn("**Mandatory:** a recovery plan and a frozen policy candidate", persist)
        self.assertIn("**Reports:**", persist)
        self.assertNotIn("If the user declines a save, continue", TEXT)

    def test_holdout_files_are_read_only_after_the_freeze(self):
        self.assertIn("holdout files (bundles `TH-`) are never read before the freeze", TEXT)
        self.assertIn("Holdout files are not read before the freeze", self.ref("policy-learning.md"))


class PackageShape(unittest.TestCase):
    def test_only_markdown_and_every_reference_linked(self):
        files = sorted(p.relative_to(SKILL).as_posix() for p in SKILL.rglob("*") if p.is_file())
        self.assertIn("SKILL.md", files)
        for name in files:
            self.assertTrue(name.endswith(".md"), name)
            if name != "SKILL.md":
                self.assertIn(f"]({name})", TEXT, name)

    def test_no_placeholders_or_external_fetch_anywhere(self):
        for path in SKILL.rglob("*.md"):
            body = path.read_text(encoding="utf-8")
            self.assertIsNone(re.search(r"\bTODO\b|\bTBD\b|replace-with-", body), path.name)
            self.assertIsNone(re.search(r"https?://", body), path.name)


if __name__ == "__main__":
    unittest.main()
