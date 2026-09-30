"""Render a saved manual badge form as a fitted, print-ready PDF.

Usage: python tools/prepare_manual_badge_for_print.py filled-badge.pdf
The input stays unchanged. The output has no editable form fields.
"""

import argparse
from pathlib import Path

import pymupdf
from pypdf import PdfReader


MM_TO_PT = 72 / 25.4
PAGE_WIDTH = 79 * MM_TO_PT
PAGE_HEIGHT = 50 * MM_TO_PT
LEFT = 4.5 * MM_TO_PT
RIGHT = PAGE_WIDTH - LEFT
TOP = 3 * MM_TO_PT
BOTTOM = PAGE_HEIGHT - TOP
EXPECTED_FIELDS = (
    "display_name",
    "primary_affiliation",
    "board_affiliation_1",
    "board_affiliation_2",
)


def read_values(path):
    reader = PdfReader(path)
    if len(reader.pages) != 1:
        raise ValueError("Expected a one-page manual badge form")
    fields = reader.get_fields() or {}
    if not all(key in fields for key in EXPECTED_FIELDS):
        raise ValueError("Input is not the manual badge form")
    values = {key: str(fields[key].get("/V", "")).strip() for key in EXPECTED_FIELDS}
    if not values["display_name"]:
        raise ValueError("Fill in and save the name field before preparing the badge")
    if not values["primary_affiliation"]:
        values["primary_affiliation"] = "Individual Donor"
    if any("\n" in value or "\r" in value for value in values.values()):
        raise ValueError("Use one line per field")
    return values


def fitted_line(text, font, maximum_size, minimum_size):
    """Return a point size that keeps the whole line inside the safe width."""
    width_at_one_point = font.text_length(text, fontsize=1)
    if width_at_one_point == 0:
        return maximum_size
    size = min(maximum_size, (RIGHT - LEFT) / width_at_one_point)
    if size < minimum_size:
        raise ValueError("A field is too long for one badge line; use a shorter display value")
    # Leave a small rounding allowance at either end for PDF text metrics.
    return min(maximum_size, size * 0.995)


def build(input_path, output_path):
    values = read_values(input_path)
    regular = pymupdf.Font("helv")
    bold = pymupdf.Font("hebo")
    lines = [
        (values["display_name"], "hebo", bold, 28, 15),
        (values["primary_affiliation"], "helv", regular, 15, 9),
    ]
    lines.extend(
        (values[key], "helv", regular, 13, 9)
        for key in ("board_affiliation_1", "board_affiliation_2") if values[key]
    )
    fitted = [
        (value, pdf_font, font, fitted_line(value, font, maximum, minimum))
        for value, pdf_font, font, maximum, minimum in lines
    ]
    gaps = [3 * MM_TO_PT if index == 0 else 1.5 * MM_TO_PT
            for index in range(len(fitted) - 1)]
    heights = [size * 1.2 for _, _, _, size in fitted]
    total_height = sum(heights) + sum(gaps)
    if total_height > BOTTOM - TOP:
        raise ValueError("Badge content is too tall; shorten the display values")

    document = pymupdf.open()
    page = document.new_page(width=PAGE_WIDTH, height=PAGE_HEIGHT)
    y = (PAGE_HEIGHT - total_height) / 2
    for index, (value, pdf_font, font, size) in enumerate(fitted):
        width = font.text_length(value, fontsize=size)
        x = (PAGE_WIDTH - width) / 2
        baseline = y + size
        page.insert_text((x, baseline), value, fontname=pdf_font, fontsize=size, color=(0, 0, 0))
        y += heights[index]
        if index < len(gaps):
            y += gaps[index]
    document.set_metadata({"title": "Manual badge label - print ready"})
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    document.save(output_path, garbage=4, deflate=True)
    document.close()
    return output_path


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("input", type=Path, help="Saved, filled manual badge PDF")
    parser.add_argument("--output", type=Path, help="Print-ready PDF path")
    args = parser.parse_args()
    output = args.output or args.input.with_name(args.input.stem + "-print-ready.pdf")
    try:
        build(args.input, output)
    except (ValueError, OSError) as error:
        parser.error(str(error))
    print(f"Wrote {output}")


if __name__ == "__main__":
    main()
