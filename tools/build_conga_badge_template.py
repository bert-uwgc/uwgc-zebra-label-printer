"""Build the Conga Composer badge template (.docx) from docs/badge-template-spec.json.

Uses only the Python standard library so the template can be rebuilt anywhere:

    python tools/build_conga_badge_template.py
    python tools/build_conga_badge_template.py --preferred-name-token "{{...}}" \
        --last-name-token "{{...}}" --affiliation-token "{{...}}"

Pass the exact tokens copied from Conga Template Builder once they are known.
"""

import argparse
import json
import zipfile
from pathlib import Path
from xml.sax.saxutils import escape

REPO = Path(__file__).resolve().parents[1]
SPEC = REPO / "docs" / "badge-template-spec.json"
DEFAULT_OUTPUT = REPO / "templates" / "conga-badge-template.docx"

# Trailing paragraph Word requires after a table; kept to 1 pt so the page never spills.
TRAILING_PARA_TWIPS = 20
NAME_SPACE_AFTER_TWIPS = 80  # 4 pt between name and affiliation

W_NS = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"


def twips(mm):
    return round(mm / 25.4 * 1440)


def half_points(pt):
    return round(pt * 2)


def run_props(font, pt, bold=False):
    b = "<w:b/><w:bCs/>" if bold else ""
    return (
        f'<w:rPr><w:rFonts w:ascii="{font}" w:hAnsi="{font}" w:cs="{font}"/>'
        f'{b}<w:sz w:val="{half_points(pt)}"/><w:szCs w:val="{half_points(pt)}"/></w:rPr>'
    )


def para_props(rpr, space_after=0):
    return (
        f'<w:pPr><w:spacing w:before="0" w:after="{space_after}" w:line="240" w:lineRule="auto"/>'
        f'<w:jc w:val="center"/>{rpr}</w:pPr>'
    )


def text_run(rpr, text):
    return f'<w:r>{rpr}<w:t xml:space="preserve">{escape(text)}</w:t></w:r>'


def name_paragraph(spec, preferred_token, last_token):
    name = spec["layout"]["name"]
    rpr = run_props(name["initial_font_family"], name["initial_font_pt"], bold=name["weight"] == "bold")
    return (
        f"<w:p>{para_props(rpr, NAME_SPACE_AFTER_TWIPS)}"
        f"{text_run(rpr, f'{preferred_token} {last_token}')}</w:p>"
    )


def affiliation_paragraph(spec, token):
    org = spec["layout"]["organization"]
    rpr = run_props(org["initial_font_family"], org["initial_font_pt"])
    fallback = org["blank_fallback"]
    # A real Word IF field with the Conga token inside it; Conga merges the token,
    # then Word evaluates the IF to show the fallback for a blank affiliation.
    code = f' IF "{token}" = "" "{fallback}" "{token}" '
    return (
        f"<w:p>{para_props(rpr)}"
        f'<w:r>{rpr}<w:fldChar w:fldCharType="begin"/></w:r>'
        f'<w:r>{rpr}<w:instrText xml:space="preserve">{escape(code)}</w:instrText></w:r>'
        f'<w:r>{rpr}<w:fldChar w:fldCharType="separate"/></w:r>'
        f"{text_run(rpr, token)}"
        f'<w:r>{rpr}<w:fldChar w:fldCharType="end"/></w:r>'
        "</w:p>"
    )


def document_xml(spec, preferred_token, last_token, affiliation_token):
    layout, media = spec["layout"], spec["media"]
    page_w, page_h = twips(layout["page_width_mm"]), twips(layout["page_height_mm"])
    side = twips(layout["content_left_margin_from_page_mm"])
    top_bottom = twips(layout["provisional_safe_margin_inside_sticker_mm"])
    content_w = page_w - 2 * side
    row_h = page_h - 2 * top_bottom - TRAILING_PARA_TWIPS
    assert content_w == twips(layout["content_width_mm"]), "spec widths disagree"
    assert media["label_height_mm"] == layout["page_height_mm"]

    no_borders = "".join(
        f'<w:{edge} w:val="nil"/>' for edge in ("top", "left", "bottom", "right", "insideH", "insideV")
    )
    zero_margins = "".join(
        f'<w:{edge} w:w="0" w:type="dxa"/>' for edge in ("top", "left", "bottom", "right")
    )
    table = (
        "<w:tbl><w:tblPr>"
        f'<w:tblW w:w="{content_w}" w:type="dxa"/><w:jc w:val="center"/>'
        f"<w:tblBorders>{no_borders}</w:tblBorders>"
        '<w:tblLayout w:type="fixed"/>'
        f"<w:tblCellMar>{zero_margins}</w:tblCellMar>"
        '<w:tblLook w:val="0000" w:firstRow="0" w:lastRow="0" w:firstColumn="0" w:lastColumn="0" w:noHBand="1" w:noVBand="1"/>'
        "</w:tblPr>"
        f'<w:tblGrid><w:gridCol w:w="{content_w}"/></w:tblGrid>'
        f'<w:tr><w:trPr><w:cantSplit/><w:trHeight w:val="{row_h}" w:hRule="exact"/></w:trPr>'
        f'<w:tc><w:tcPr><w:tcW w:w="{content_w}" w:type="dxa"/><w:vAlign w:val="center"/></w:tcPr>'
        f"{name_paragraph(spec, preferred_token, last_token)}"
        f"{affiliation_paragraph(spec, affiliation_token)}"
        "</w:tc></w:tr></w:tbl>"
    )
    trailing = (
        f'<w:p><w:pPr><w:spacing w:before="0" w:after="0" w:line="{TRAILING_PARA_TWIPS}" w:lineRule="exact"/>'
        '<w:rPr><w:sz w:val="2"/><w:szCs w:val="2"/></w:rPr></w:pPr></w:p>'
    )
    sect = (
        f'<w:sectPr><w:pgSz w:w="{page_w}" w:h="{page_h}"/>'
        f'<w:pgMar w:top="{top_bottom}" w:right="{side}" w:bottom="{top_bottom}" w:left="{side}" '
        'w:header="0" w:footer="0" w:gutter="0"/>'
        '<w:cols w:space="720"/><w:docGrid w:linePitch="360"/></w:sectPr>'
    )
    return (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        f'<w:document xmlns:w="{W_NS}"><w:body>{table}{trailing}{sect}</w:body></w:document>'
    )


STYLES_XML = (
    '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
    f'<w:styles xmlns:w="{W_NS}">'
    "<w:docDefaults><w:rPrDefault><w:rPr>"
    '<w:rFonts w:ascii="Arial" w:hAnsi="Arial" w:cs="Arial" w:eastAsia="Arial"/>'
    '<w:sz w:val="22"/><w:szCs w:val="22"/><w:lang w:val="en-US"/>'
    "</w:rPr></w:rPrDefault>"
    '<w:pPrDefault><w:pPr><w:spacing w:after="0" w:line="240" w:lineRule="auto"/></w:pPr></w:pPrDefault>'
    "</w:docDefaults>"
    '<w:style w:type="paragraph" w:default="1" w:styleId="Normal"><w:name w:val="Normal"/><w:qFormat/></w:style>'
    '<w:style w:type="table" w:default="1" w:styleId="TableNormal"><w:name w:val="Normal Table"/>'
    '<w:tblPr><w:tblInd w:w="0" w:type="dxa"/><w:tblCellMar><w:top w:w="0" w:type="dxa"/>'
    '<w:left w:w="0" w:type="dxa"/><w:bottom w:w="0" w:type="dxa"/><w:right w:w="0" w:type="dxa"/>'
    "</w:tblCellMar></w:tblPr></w:style>"
    "</w:styles>"
)

SETTINGS_XML = (
    '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
    f'<w:settings xmlns:w="{W_NS}"><w:defaultTabStop w:val="720"/>'
    '<w:characterSpacingControl w:val="doNotCompress"/>'
    '<w:compat><w:compatSetting w:name="compatibilityMode" w:uri="http://schemas.microsoft.com/office/word" w:val="15"/></w:compat>'
    "</w:settings>"
)

CONTENT_TYPES_XML = (
    '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
    '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
    '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
    '<Default Extension="xml" ContentType="application/xml"/>'
    '<Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>'
    '<Override PartName="/word/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.styles+xml"/>'
    '<Override PartName="/word/settings.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.settings+xml"/>'
    '<Override PartName="/docProps/core.xml" ContentType="application/vnd.openxmlformats-package.core-properties+xml"/>'
    "</Types>"
)

ROOT_RELS_XML = (
    '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
    '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
    '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/>'
    '<Relationship Id="rId2" Type="http://schemas.openxmlformats.org/package/2006/relationships/metadata/core-properties" Target="docProps/core.xml"/>'
    "</Relationships>"
)

DOC_RELS_XML = (
    '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
    '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
    '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles" Target="styles.xml"/>'
    '<Relationship Id="rId2" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/settings" Target="settings.xml"/>'
    "</Relationships>"
)

CORE_XML = (
    '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
    '<cp:coreProperties xmlns:cp="http://schemas.openxmlformats.org/package/2006/metadata/core-properties" '
    'xmlns:dc="http://purl.org/dc/elements/1.1/">'
    "<dc:title>Conga badge template (draft)</dc:title>"
    "</cp:coreProperties>"
)


def build(output, preferred_token, last_token, affiliation_token):
    spec = json.loads(SPEC.read_text(encoding="utf-8"))
    output = Path(output)
    output.parent.mkdir(parents=True, exist_ok=True)
    parts = {
        "[Content_Types].xml": CONTENT_TYPES_XML,
        "_rels/.rels": ROOT_RELS_XML,
        "docProps/core.xml": CORE_XML,
        "word/document.xml": document_xml(spec, preferred_token, last_token, affiliation_token),
        "word/styles.xml": STYLES_XML,
        "word/settings.xml": SETTINGS_XML,
        "word/_rels/document.xml.rels": DOC_RELS_XML,
    }
    with zipfile.ZipFile(output, "w", zipfile.ZIP_DEFLATED) as z:
        for name, xml in parts.items():
            # Fixed timestamp keeps rebuilds byte-identical.
            info = zipfile.ZipInfo(name, date_time=(2026, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            z.writestr(info, xml)
    return output


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--output", default=str(DEFAULT_OUTPUT))
    parser.add_argument("--preferred-name-token", default="{{PREFERRED_NAME_CONGA_FIELD}}")
    parser.add_argument("--last-name-token", default="{{LAST_NAME_CONGA_FIELD}}")
    parser.add_argument("--affiliation-token", default="{{PRIMARY_AFFILIATION_CONGA_FIELD}}")
    args = parser.parse_args()
    out = build(args.output, args.preferred_name_token, args.last_name_token, args.affiliation_token)
    print(f"Wrote {out}")


if __name__ == "__main__":
    main()
