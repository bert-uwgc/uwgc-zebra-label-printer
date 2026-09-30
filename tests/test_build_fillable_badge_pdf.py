"""Contract checks for the printable, manually fillable badge label."""

import subprocess
import sys
import unittest
import uuid
from pathlib import Path

from pypdf import PdfReader


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
        self.assertIn("/HeBo 0 Tf", name_widget.get("/DA", ""))
        fonts = reader.trailer["/Root"]["/AcroForm"]["/DR"]["/Font"]
        self.assertEqual(fonts["/HeBo"]["/BaseFont"], "/Helvetica-Bold")
        self.assertNotIn("CONGA_FIELD", page.extract_text())


if __name__ == "__main__":
    unittest.main()
