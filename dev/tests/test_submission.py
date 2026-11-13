"""Submission materials: proposal limits, PDF limits, demo length."""
import re
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "dev" / "tools"))

import proposal_pdf  # noqa: E402


class SubmissionLimits(unittest.TestCase):
    def test_ten_official_questions_within_500_words(self):
        counts = proposal_pdf.count((ROOT / "submission" / "PROPOSAL.md").read_text(encoding="utf-8"))
        self.assertEqual(len(counts["per_answer"]), 10)
        self.assertLessEqual(counts["total"], 500)

    def test_pdf_exists_and_is_under_1_mb(self):
        pdf = ROOT / "submission" / "cerbero-guardian-proposal.pdf"
        self.assertTrue(pdf.exists())
        self.assertLess(pdf.stat().st_size, 1024 * 1024)

    def test_latest_zip_matches_the_skill_folder(self):
        import zipfile

        builds = sorted((ROOT / "dist").glob("cerbero-guardian-*.zip"))
        self.assertTrue(builds, "no package built: run python dev/tools/build_skill_zip.py")
        skill = ROOT / "skill" / "cerbero-guardian"
        with zipfile.ZipFile(builds[-1]) as bundle:
            packed = {name.removeprefix("cerbero-guardian/"): bundle.read(name) for name in bundle.namelist()}
        current = {p.relative_to(skill).as_posix(): p.read_bytes() for p in skill.rglob("*") if p.is_file()}
        self.assertEqual(packed, current, "the ZIP is stale: build a new version")

    def test_demo_script_is_under_three_minutes(self):
        text = (ROOT / "submission" / "DEMO_SCRIPT.md").read_text(encoding="utf-8")
        ends = [int(m) * 60 + int(s) for m, s in re.findall(r"^\| \d+:\d+–(\d+):(\d+) \|", text, re.M)]
        self.assertTrue(ends)
        self.assertLess(max(ends), 180)


if __name__ == "__main__":
    unittest.main()
