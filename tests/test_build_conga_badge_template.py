import re
import subprocess
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
BUILDER = REPO / "tools" / "build_conga_badge_template.py"


def mm_to_twips(mm):
    return round(mm / 25.4 * 1440)


class BuildCongaBadgeTemplateTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        cls.out = Path(cls.tmp.name) / "badge.docx"
        subprocess.run(
            [sys.executable, str(BUILDER), "--output", str(cls.out)],
            check=True,
        )
        with zipfile.ZipFile(cls.out) as z:
            cls.names = set(z.namelist())
            cls.doc = z.read("word/document.xml").decode("utf-8")

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def test_package_has_required_parts(self):
        for part in ("[Content_Types].xml", "_rels/.rels", "word/document.xml",
                     "word/_rels/document.xml.rels", "word/styles.xml",
                     "word/settings.xml"):
            self.assertIn(part, self.names)

    def test_page_is_79_by_50_mm(self):
        self.assertIn(f'<w:pgSz w:w="{mm_to_twips(79)}" w:h="{mm_to_twips(50)}"', self.doc)

    def test_margins_are_4_5_mm_sides_and_3_mm_top_bottom(self):
        side, tb = mm_to_twips(4.5), mm_to_twips(3)
        self.assertRegex(
            self.doc,
            rf'<w:pgMar w:top="{tb}" w:right="{side}" w:bottom="{tb}" w:left="{side}"',
        )

    def test_single_borderless_cell_is_70_mm_wide_and_vertically_centered(self):
        self.assertEqual(self.doc.count("<w:tc>"), 1)
        self.assertIn(f'<w:gridCol w:w="{mm_to_twips(70)}"/>', self.doc)
        self.assertIn('<w:vAlign w:val="center"/>', self.doc)
        self.assertIn('<w:top w:val="nil"/>', self.doc)
        self.assertIn('w:hRule="exact"', self.doc)

    def test_name_paragraph_is_centered_26pt_arial_bold(self):
        name_para = re.search(r"<w:p>(?:(?!</w:p>).)*PREFERRED_NAME(?:(?!</w:p>).)*</w:p>", self.doc, re.S)
        self.assertIsNotNone(name_para)
        p = name_para.group(0)
        self.assertIn('<w:jc w:val="center"/>', p)
        self.assertIn('<w:sz w:val="52"/>', p)
        self.assertIn("<w:b/>", p)
        self.assertIn('w:ascii="Arial"', p)
        self.assertIn("{{PREFERRED_NAME_CONGA_FIELD}} {{LAST_NAME_CONGA_FIELD}}", p)

    def test_affiliation_uses_word_if_field_with_individual_donor_fallback(self):
        self.assertIn('<w:fldChar w:fldCharType="begin"/>', self.doc)
        self.assertIn(
            ' IF "{{PRIMARY_AFFILIATION_CONGA_FIELD}}" = "" "Individual Donor" '
            '"{{PRIMARY_AFFILIATION_CONGA_FIELD}}" ',
            self.doc,
        )
        self.assertIn('<w:sz w:val="30"/>', self.doc)

    def test_custom_tokens_replace_placeholders(self):
        out = Path(self.tmp.name) / "custom.docx"
        subprocess.run(
            [sys.executable, str(BUILDER), "--output", str(out),
             "--preferred-name-token", "{{PREF}}",
             "--last-name-token", "{{LAST}}",
             "--affiliation-token", "{{AFFIL}}"],
            check=True,
        )
        with zipfile.ZipFile(out) as z:
            doc = z.read("word/document.xml").decode("utf-8")
        self.assertIn("{{PREF}} {{LAST}}", doc)
        self.assertIn('IF "{{AFFIL}}" = ""', doc)
        self.assertNotIn("CONGA_FIELD", doc)


if __name__ == "__main__":
    unittest.main()
