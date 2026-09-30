"""Contract checks for the printable, manually fillable badge label."""

import subprocess
import sys
import unittest
import uuid
from pathlib import Path

from pypdf import PdfReader
from pypdf.generic import IndirectObject


REPO = Path(__file__).resolve().parents[1]
BUILDER = REPO / "tools" / "build_fillable_badge_pdf.py"


class FillableBadgePdfTest(unittest.TestCase):
    def test_blank_printable_label_has_editable_fields_at_label_size(self):
        output = REPO / "tests" / ".tmp" / f"manual-badge-{uuid.uuid4().hex}.pdf"
        output.parent.mkdir(exist_ok=True)
        self.addCleanup(output.unlink, missing_ok=True)
        subprocess.run(
            [sys.executable, str(BUILDER), "--output", str(output)],
            check=True,
            capture_output=True,
            text=True,
        )
        reader = PdfReader(output)
        self.assertEqual(len(reader.pages), 1)
        page = reader.pages[0]
        self.assertAlmostEqual(float(page.mediabox.width), 79 / 25.4 * 72, delta=0.05)
        self.assertAlmostEqual(float(page.mediabox.height), 50 / 25.4 * 72, delta=0.05)

        expected = {
            "display_name",
            "primary_affiliation",
            "board_affiliation_1",
            "board_affiliation_2",
        }
        fields = reader.get_fields() or {}
        self.assertEqual(set(fields), expected)
        self.assertTrue(all(not field.get("/V") for field in fields.values()))

        widgets = [a.get_object() for a in page.get("/Annots", [])]
        self.assertEqual(len(widgets), len(expected))
        self.assertTrue(all(w.get("/Subtype") == "/Widget" for w in widgets))
        self.assertTrue(all(int(w.get("/F", 0)) & 4 for w in widgets))
        self.assertEqual({w.get("/T") for w in widgets}, expected)
        self.assertTrue(all(int(w.get("/Q", 0)) == 1 for w in widgets))
        name_widget = next(w for w in widgets if w.get("/T") == "display_name")
        self.assertIn("/HeBo 28 Tf", name_widget.get("/DA", ""))
        org_widget = next(w for w in widgets if w.get("/T") == "primary_affiliation")
        self.assertIn("/Helv 15 Tf", org_widget.get("/DA", ""))
        board_widgets = [w for w in widgets if w.get("/T", "").startswith("board_affiliation_")]
        self.assertTrue(all("/Helv 13 Tf" in w.get("/DA", "") for w in board_widgets))
        board_heights = [float(w["/Rect"][3]) - float(w["/Rect"][1]) for w in board_widgets]
        self.assertAlmostEqual(board_heights[0], board_heights[1], delta=0.05)
        acroform = reader.trailer["/Root"]["/AcroForm"]
        self.assertIn("/DA", acroform)
        fonts = acroform["/DR"]["/Font"]
        self.assertIsInstance(fonts.raw_get("/HeBo"), IndirectObject)
        self.assertEqual(fonts["/HeBo"]["/BaseFont"], "/Helvetica-Bold")
        self.assertNotIn("CONGA_FIELD", page.extract_text())


if __name__ == "__main__":
    unittest.main()
