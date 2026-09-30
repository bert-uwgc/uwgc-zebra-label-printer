"""Build a blank, fillable badge PDF for manual printing without Salesforce.

Run from anywhere: python tools/build_fillable_badge_pdf.py
Requires PyMuPDF. The PDF page matches the 79 x 50 mm roll pitch in the badge spec.
"""

import argparse
import io
import json
from pathlib import Path

import pymupdf
from pypdf import PdfReader, PdfWriter
from pypdf.generic import DictionaryObject, NameObject, NumberObject, TextStringObject


REPO = Path(__file__).resolve().parents[1]
SPEC = REPO / "docs" / "badge-template-spec.json"
DEFAULT_OUTPUT = REPO / "output" / "pdf" / "manual-badge-label-auto-fit.pdf"


def mm(value):
    return value * 72 / 25.4


def add_text_field(page, document, name, label, rectangle, font, size):
    field = pymupdf.Widget()
    field.field_name = name
    field.field_label = label
    field.field_type = pymupdf.PDF_WIDGET_TYPE_TEXT
    field.field_value = ""
    field.rect = pymupdf.Rect(*rectangle)
    field.text_font = font
    field.text_fontsize = size
    field.text_color = (0, 0, 0)
    field.text_align = pymupdf.TEXT_ALIGN_CENTER
    field.border_width = 0
    field.border_color = None
    field.fill_color = (1, 1, 1)
    added = page.add_widget(field)
    # Annotation flag 4 makes the typed value appear in printed output.
    document.xref_set_key(added.xref, "F", "4")


def center_fields_and_add_bold_font(pdf_bytes):
    """Set standard AcroForm alignment and font resources for PDF viewers."""
    writer = PdfWriter()
    writer.clone_document_from_reader(PdfReader(io.BytesIO(pdf_bytes)))
    acroform = writer._root_object["/AcroForm"].get_object()
    acroform[NameObject("/DA")] = TextStringObject("/Helv 0 Tf 0 g")
    resources = acroform.get("/DR") or DictionaryObject()
    acroform[NameObject("/DR")] = resources
    fonts = resources.get("/Font") or DictionaryObject()
    resources[NameObject("/Font")] = fonts
    fonts[NameObject("/Helv")] = writer._add_object(DictionaryObject({
        NameObject("/Type"): NameObject("/Font"),
        NameObject("/Subtype"): NameObject("/Type1"),
        NameObject("/BaseFont"): NameObject("/Helvetica"),
        NameObject("/Encoding"): NameObject("/WinAnsiEncoding"),
    }))
    fonts[NameObject("/HeBo")] = writer._add_object(DictionaryObject({
        NameObject("/Type"): NameObject("/Font"),
        NameObject("/Subtype"): NameObject("/Type1"),
        NameObject("/BaseFont"): NameObject("/Helvetica-Bold"),
        NameObject("/Encoding"): NameObject("/WinAnsiEncoding"),
    }))
    for annotation in writer.pages[0]["/Annots"]:
        field = annotation.get_object()
        field[NameObject("/Q")] = NumberObject(1)
        if field["/T"] == "display_name":
            field[NameObject("/DA")] = TextStringObject("/HeBo 0 Tf 0 g")
        else:
            field[NameObject("/DA")] = TextStringObject("/Helv 0 Tf 0 g")
    return writer


def build(output):
    spec = json.loads(SPEC.read_text(encoding="utf-8"))
    layout = spec["layout"]
    document = pymupdf.open()
    page = document.new_page(
        width=mm(layout["page_width_mm"]),
        height=mm(layout["page_height_mm"]),
    )
    x0 = mm(layout["content_left_margin_from_page_mm"])
    x1 = mm(layout["page_width_mm"] - layout["content_right_margin_from_page_mm"])

    # A zero-point AcroForm font asks the PDF viewer to fit the entered text.
    add_text_field(page, document, "display_name", "Full display name", (x0, mm(8), x1, mm(22)), "Helv", 0)
    add_text_field(
        page, document, "primary_affiliation", "Organization or Individual Donor; add (Retired) if applicable",
        (x0, mm(24), x1, mm(31)), "Helv", 0,
    )
    add_text_field(
        page, document, "board_affiliation_1", "Board affiliation, first line (optional)",
        (x0, mm(33), x1, mm(39)), "Helv", 0,
    )
    add_text_field(
        page, document, "board_affiliation_2", "Board affiliation, second line (optional)",
        (x0, mm(40), x1, mm(46)), "Helv", 0,
    )

    output = Path(output)
    output.parent.mkdir(parents=True, exist_ok=True)
    document.set_metadata({"title": "Manual badge label - blank fillable form"})
    writer = center_fields_and_add_bold_font(document.tobytes(garbage=4, deflate=True))
    with output.open("wb") as stream:
        writer.write(stream)
    document.close()
    return output


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--output", default=str(DEFAULT_OUTPUT))
    args = parser.parse_args()
    print(f"Wrote {build(args.output)}")


if __name__ == "__main__":
    main()
