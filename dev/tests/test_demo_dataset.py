"""Demo data: valid-format files that open after recovery, and test cases split by holdout."""
import io
import unittest

from cerbero_lab import formats
from cerbero_lab.fixtures import load
from cerbero_lab.pipeline import run
from cerbero_lab.policy import test_case_bundles
from cerbero_lab.records import parse, validate

DEMO = "fixtures/demo/S00V-demo-valid-formats.json"


class ValidFormats(unittest.TestCase):
    def test_generators_produce_parseable_files(self):
        self.assertTrue(formats.check_pdf(formats.pdf("line one\nline (two)")))
        self.assertEqual(formats.docx_text(formats.docx("a & b\n<c>")), "a & b\n<c>")
        self.assertEqual(formats.check_tiff(formats.tiff("seed")), (64, 48))
        self.assertEqual(len(formats.tiff("seed")), len(formats.tiff("seed", mark=True)))
        self.assertNotEqual(formats.tiff("seed"), formats.tiff("seed", mark=True))

    def test_pdf_text_is_extractable(self):
        try:
            from pypdf import PdfReader
        except ImportError:
            self.skipTest("pypdf not installed")
        sc = load(DEMO)
        text = PdfReader(io.BytesIO(sc.blobs["brief-v2"])).pages[0].extract_text()
        self.assertIn("AURORA brief v2", text)

    def test_recovered_deliverables_open_and_equal_the_approved_versions(self):
        sc = load(DEMO)
        report, nas = run("C", sc)
        self.assertEqual((report.final["overall"], report.final["set_complete"]), ("verified", True))
        self.assertEqual(report.final["outside"], ["A-raw0142"])
        folder = report.final["folder"]
        cover = nas.content(f"{folder}/cover.tif")
        self.assertEqual(formats.check_tiff(cover), (64, 48))
        self.assertEqual(cover, sc.blobs["cover-v2"])
        self.assertIn("Delivery 2", formats.docx_text(nas.content(f"{folder}/copy.docx")))
        self.assertEqual(len(sc.blobs["cover-tampered"]), len(sc.blobs["cover-v2"]))


class TestCaseSeeds(unittest.TestCase):
    def test_each_seed_file_holds_one_split_and_validates(self):
        seeds = test_case_bundles()
        self.assertEqual(sorted(seeds), ["CERBERO-TD-0000-01.md", "CERBERO-TH-0000-01.md"])
        for name, data in seeds.items():
            records = parse(data.decode("utf-8"))["records"]
            self.assertEqual(validate(records), [])
            splits = {r["split"] for r in records.values()}
            self.assertEqual(splits, {"holdout"} if "-TH-" in name else {"development"})


if __name__ == "__main__":
    unittest.main()
