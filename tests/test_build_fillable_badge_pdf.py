"""Contract checks for the printable, manually fillable badge label."""

import subprocess
import sys
import unittest
import uuid
import re
from pathlib import Path

from pypdf import PdfReader, PdfWriter
from pypdf.generic import IndirectObject


REPO = Path(__file__).resolve().parents[1]
BUILDER = REPO / "tools" / "build_fillable_badge_pdf.py"


class FillableBadgePdfTest(unittest.TestCase):
    def test_saved_fields_auto_size_short_and_long_text(self):
        blank = REPO / "tests" / ".tmp" / f"auto-blank-{uuid.uuid4().hex}.pdf"
        blank.parent.mkdir(exist_ok=True)
        self.addCleanup(blank.unlink, missing_ok=True)
        subprocess.run([sys.executable, str(BUILDER), "--output", str(blank)],
                       check=True, capture_output=True)
        sizes = []
        for name in ("Alex Rivera", "Alexandria Montgomery"):
            filled = REPO / "tests" / ".tmp" / f"auto-filled-{uuid.uuid4().hex}.pdf"
            self.addCleanup(filled.unlink, missing_ok=True)
            writer = PdfWriter()
            writer.clone_document_from_reader(PdfReader(blank))
            writer.update_page_form_field_values(None, {
                "display_name": name,
                "primary_affiliation": "Example Organization with a Longer Name",
                "board_affiliation_1": "Board of Directors",
                "board_affiliation_2": "A Long Board Affiliation Description",
            }, auto_regenerate=False)
            with filled.open("wb") as stream:
                writer.write(stream)
            saved = PdfReader(filled)
            self.assertEqual(saved.get_fields()["display_name"].get("/V"), name)
            widgets = {item.get_object()["/T"]: item.get_object()
                       for item in saved.pages[0]["/Annots"]}
            self.assertTrue(all(widget["/AP"]["/N"].get_object().get_data()
                                for widget in widgets.values()))
            appearance = widgets["display_name"]["/AP"]["/N"].get_object().get_data()
            font_sizes = re.findall(rb"([0-9.]+) Tf", appearance)
            self.assertEqual(len(font_sizes), 1)
            sizes.append(float(font_sizes[0]))
        self.assertGreater(sizes[0], 25)
        self.assertGreaterEqual(sizes[1], 15)
        self.assertLess(sizes[1], sizes[0])

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
        org_widget = next(w for w in widgets if w.get("/T") == "primary_affiliation")
        self.assertIn("/Helv 0 Tf", org_widget.get("/DA", ""))
        board_widgets = [w for w in widgets if w.get("/T", "").startswith("board_affiliation_")]
        self.assertTrue(all("/Helv 0 Tf" in w.get("/DA", "") for w in board_widgets))
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
