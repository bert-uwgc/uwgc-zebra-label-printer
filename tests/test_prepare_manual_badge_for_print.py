"""Printed badges must fit values saved in the fillable PDF."""

import subprocess
import sys
import unittest
import uuid
from pathlib import Path

import pymupdf
from pypdf import PdfReader, PdfWriter


REPO = Path(__file__).resolve().parents[1]
BUILDER = REPO / "tools" / "build_fillable_badge_pdf.py"
PREPARER = REPO / "tools" / "prepare_manual_badge_for_print.py"


class PrepareManualBadgeForPrintTest(unittest.TestCase):
    def test_short_and_long_entries_render_bold_and_within_label(self):
        cases = (
            ("Alex Rivera", "Example Organization", "Board of Directors", "Foundation Board"),
            (
                "Alexandria Montgomery",
                "Example Organization with a Longer Name",
                "Board of Directors",
                "A Long Board Affiliation Description",
            ),
        )
        name_sizes = []
        for name, organization, board_1, board_2 in cases:
            token = uuid.uuid4().hex
            blank = REPO / "tests" / ".tmp" / f"blank-{token}.pdf"
            filled = REPO / "tests" / ".tmp" / f"filled-{token}.pdf"
            ready = REPO / "tests" / ".tmp" / f"ready-{token}.pdf"
            blank.parent.mkdir(exist_ok=True)
            for path in (blank, filled, ready):
                self.addCleanup(path.unlink, missing_ok=True)
            subprocess.run([sys.executable, str(BUILDER), "--output", str(blank)], check=True, capture_output=True)

            writer = PdfWriter()
            writer.clone_document_from_reader(PdfReader(blank))
            writer.update_page_form_field_values(
                None,
                {
                    "display_name": name,
                    "primary_affiliation": organization,
                    "board_affiliation_1": board_1,
                    "board_affiliation_2": board_2,
                },
                auto_regenerate=False,
            )
            with filled.open("wb") as stream:
                writer.write(stream)
            saved = PdfReader(filled)
            self.assertEqual(saved.get_fields()["display_name"].get("/V"), name)
            self.assertTrue(all(
                widget.get_object().get("/AP", {}).get("/N")
                for widget in saved.pages[0].get("/Annots", [])
            ))

            subprocess.run(
                [sys.executable, str(PREPARER), str(filled), "--output", str(ready)],
                check=True,
                capture_output=True,
                text=True,
            )
            reader = PdfReader(ready)
            self.assertEqual(len(reader.pages), 1)
            self.assertFalse(reader.get_fields())
            self.assertFalse(reader.pages[0].get("/Annots"))
            with pymupdf.open(ready) as document:
                page = document[0]
                self.assertAlmostEqual(page.rect.width, 79 / 25.4 * 72, delta=0.05)
                self.assertAlmostEqual(page.rect.height, 50 / 25.4 * 72, delta=0.05)
                text = page.get_text()
                for value in (organization, board_1, board_2):
                    self.assertIn(value, text)
                for word in name.split():
                    self.assertIn(word, text)
                spans = [span for block in page.get_text("dict")["blocks"]
                         if "lines" in block for line in block["lines"] for span in line["spans"]]
                for span in spans:
                    self.assertGreaterEqual(span["bbox"][0], 12, span["text"])
                    self.assertLessEqual(span["bbox"][2], page.rect.width - 12, span["text"])
                    self.assertGreaterEqual(span["bbox"][1], 8, span["text"])
                    self.assertLessEqual(span["bbox"][3], page.rect.height - 8, span["text"])
                bold = [span for span in spans if "Bold" in span["font"]]
                self.assertTrue(bold)
                name_sizes.append(max(span["size"] for span in bold))
        self.assertAlmostEqual(name_sizes[0], 28, delta=0.2)
        self.assertLess(name_sizes[1], name_sizes[0])
        self.assertGreaterEqual(name_sizes[1], 15)


if __name__ == "__main__":
    unittest.main()
