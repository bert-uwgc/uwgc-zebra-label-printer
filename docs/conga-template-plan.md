# Conga badge template draft

The first version is a single-badge Word template for Conga Composer for Salesforce, rendered to PDF for printing. It uses the geometry and draft typography in [badge-template-spec.json](badge-template-spec.json). The JSON records design inputs; it is not a Conga template.

Synthetic [one-line](badge-preview-short.png) and [two-line](badge-preview-long.png) previews show the intended arrangement. They are geometry previews rendered at 203 dpi, matching the Windows 11 driver name reported by the user, not Conga output or files to send to the printer.

## Artwork and media

- Set the Word page to **76 mm wide by 50 mm high**. The **3 mm gap** is between labels on the roll, so it belongs in the printer media setting, not in the page height. The label pitch is 53 mm.
- The Windows print queue appears as **ZDesigner ZD421-203dpi ZPL**. At the nominal 8 dots per mm, the label is 608 by 400 dots and the 3 mm gap is 24 dots. Use physical dimensions for the Word and PDF page; the dot counts are reference values for printer diagnostics or ZPL work.
- Start with a 3 mm safe inset on every side, leaving a provisional 70 mm by 44 mm content area. Adjust it after a physical print check.
- Use a borderless one-cell table covering that content area. Set its cell to vertical middle alignment. Center both paragraphs horizontally in the cell so the name and organization move together as one block when the name wraps.
- Put `{{FIRST_NAME_FIELD}} {{LAST_NAME_FIELD}}` on one centered paragraph at an initial **26 pt Arial Bold**. Allow normal word wrapping up to two lines. A short name stays on one line.
- Put `{{BADGE_ORGANIZATION_FIELD}}` beneath it on a centered paragraph at **15 pt Arial**. Supply an approved abbreviation in that field when the full organization does not fit. For a blank organization, display **Individual Donor**. Do not silently truncate it.
- Treat 26 pt and the 3 mm safe inset as first-pass values. Never reduce either text style below 15 pt. If a name exceeds two lines, review a smaller-font fallback or an approved display-name spelling before printing.

## Conga and Salesforce setup

1. In Conga Composer's Template Builder, replace the three placeholder names with the exact available merge fields. If organization comes from a related object, add the needed Conga query or report. An approved badge-organization field or formula should return the abbreviation chosen by staff or the fixed fallback when blank.
2. Store the Word file as a Conga template and configure the solution for **one record and one badge per run**, with PDF output. Do not add repeating detail regions.
3. In the Zebra driver, define the media as **76 mm by 50 mm die-cut labels with a 3 mm gap** and use actual-size printing. Confirm the media sensor and calibrate for the loaded roll.
4. Cross-check the physical printer against the 203 dpi Windows driver during the first print proof. Confirm its print method on the printer configuration report or in Zebra management tools. Non-direct-thermal stock requires a thermal-transfer capable printer and compatible ribbon. The driver name identifies ZPL and 203 dpi, not the loaded ribbon or media.
5. Test with synthetic short, long, hyphenated, and accented names; long and abbreviated organizations; and a blank organization. Inspect both the PDF and a physical print for wrapping, clipping, centering, and feed alignment.

## Inputs still pending

- Confirmed thermal-transfer print method and ribbon-media pairing. Cross-check physical printer resolution during the first print proof.
- Exact Salesforce merge-field names and approved organization abbreviation source.
- Physical print results to finalize the safe inset and font size.

## References

- [Conga Composer Word merge templates](https://documentation.conga.com/en/composer-for-salesforce/current/composer-for-administrators/creating-composer-templates/word-templates/word-template-basics/about-microsoft-word-merge-templates)
- [Conga Template Builder](https://documentation.conga.com/en/composer-for-salesforce/current/composer-for-administrators/creating-composer-templates/composer-template-basics/use-the-template-builder-to-construct-your-template)
- [Zebra ZD421 media and print specifications](https://docs.zebra.com/us/en/printers/desktop/zd421-and-zd621-desktop-printers-user-guide/media/general-media-and-print-specifications.html)
- [Zebra ZD421 configuration report](https://docs.zebra.com/us/en/printers/desktop/zd421-and-zd621-desktop-printers-user-guide/c-zd421-zd621-ug-tools/r-mlk-ug-printer-diagnostics/t-zd620zd420-ug-printing-the-printer-and-network-configuration-reports.html)
