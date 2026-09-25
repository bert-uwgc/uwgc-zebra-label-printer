# Conga badge template draft

The first version is a single-badge Word template for Conga Composer for Salesforce, rendered to PDF for printing. It uses the geometry and draft typography in [badge-template-spec.json](badge-template-spec.json). The JSON records design inputs; it is not a Conga template.

Synthetic [one-line](badge-preview-short.png) and [two-line](badge-preview-long.png) previews show the intended arrangement on the **76 mm sticker only**. They are geometry previews rendered at 203 dpi, matching the Windows 11 driver name reported by the user, not Conga output or files to send to the printer.

## Building the Word template

[tools/build_conga_badge_template.py](../tools/build_conga_badge_template.py) generates `templates/conga-badge-template.docx` from the spec, using only the Python standard library. Once the exact Template Builder tokens are known, pass them in and rebuild instead of editing field codes by hand:

```
python tools/build_conga_badge_template.py --preferred-name-token "{{...}}" --last-name-token "{{...}}" --affiliation-token "{{...}}"
python -m unittest tests.test_build_conga_badge_template
```

The affiliation paragraph is a real Word IF field wrapping the Conga token. Press Alt+F9 in Word to see the field code. With placeholder tokens the text looks clipped in Word because the tokens are longer than real names. Merged output is the thing to judge.

## Artwork and media

- Set the Word and PDF page to **79 mm wide by 50 mm high**, matching the roll width including backing and the sticker length. The **76 mm sticker** is centered, leaving **1.5 mm of backing on each side**. Keep text at least a provisional **3 mm inside the sticker**, which means a **4.5 mm page margin** on the left and right and a 70 mm content width. Verify the driver's horizontal origin with a print proof.
- The **3 mm gap** is between stickers on the roll. It belongs in the printer media setting, not in the document page height. The label pitch is 53 mm.
- The Windows print queue appears as **ZDesigner ZD421-203dpi ZPL**. At the nominal 8 dots per mm, the label is 608 by 400 dots and the 3 mm gap is 24 dots. Use physical dimensions for the Word and PDF page; the dot counts are reference values for printer diagnostics or ZPL work.
- Start with a 3 mm safe inset inside the sticker on every side, leaving a provisional 70 mm by 44 mm content area. Adjust it after a physical print check.
- Use a borderless one-cell table covering that content area. Set its cell to vertical middle alignment. Center both paragraphs horizontally in the cell so the name and organization move together as one block when the name wraps.
- Put `{{PREFERRED_NAME_CONGA_FIELD}} {{LAST_NAME_CONGA_FIELD}}` on one centered paragraph at an initial **26 pt Arial Bold**. Allow normal word wrapping up to two lines. A short name stays on one line. Check that Preferred Communication Name contains only the intended given or preferred name so Last Name is not repeated.
- Put `{{PRIMARY_AFFILIATION_CONGA_FIELD}}` beneath it on a centered paragraph at **15 pt Arial**. The source is Contact Primary Affiliation. Supply an approved abbreviation when the full affiliation does not fit. For a blank affiliation, display **Individual Donor**. Do not silently truncate it.
- Treat 26 pt and the 3 mm safe inset as first-pass values. Never reduce either text style below 15 pt. If a name exceeds two lines, review a smaller-font fallback or an approved display-name spelling before printing.

## Conga and Salesforce setup

The Salesforce source fields supplied are `Contact.Preferred_Communication_Name__c`, `Contact.LastName`, and `Contact.Primary_Affiliation__c`. The `{!Contact...}` form is Salesforce reference syntax, not a confirmed Conga Word merge token. Conga Word text merge fields use `{{...}}`, and the field name must match Template Builder exactly.

1. In Conga Composer's Template Builder, select Word format with Include Label off, copy the three exact tokens for these Contact fields, and replace the corresponding placeholders. Confirm the Contact record is the solution's master record or that all three fields appear in its dataset. A test merge must confirm their values.
2. For a blank Primary Affiliation, a Word IF field can display **Individual Donor**; Conga requires the IF itself to be a real Word field, with the Conga token inside it. Alternatively, a controlled Salesforce display field or query expression can supply the fallback. An approved abbreviation still needs a defined source; the raw affiliation field cannot choose one from its length alone.
3. Store the Word file as a Conga template and configure the solution for **one record and one badge per run**, with PDF output. Do not add repeating detail regions.
4. In the Zebra driver, use the **79 mm media width**, **50 mm sticker length**, and **3 mm gap**, then print at actual size. The document page leaves 1.5 mm blank on each side over the backing. Confirm gap sensing and calibrate for the loaded roll.
5. A **110 mm black thermal-transfer ribbon** is reported installed. Its width exceeds the 79 mm backing, meeting Zebra's width guidance. Verify that the driver is in thermal-transfer mode and that the ribbon formulation works with the stock. Cross-check the physical printer against the 203 dpi Windows driver during the first print proof.
6. Test with synthetic short, long, hyphenated, and accented names; long and abbreviated organizations; and a blank organization. Inspect both the PDF and a physical print for wrapping, clipping, centering, and feed alignment.

## Inputs still pending

- Ribbon-media pairing; verify thermal-transfer mode in the driver. Cross-check physical printer resolution during the first print proof.
- Exact Conga Template Builder Word merge tokens, and the approved organization abbreviation source.
- Confirmation that Preferred Communication Name contains the intended first-name text rather than a full name.
- Physical print results to finalize the safe inset and font size.

## References

- [Conga Composer Word merge templates](https://documentation.conga.com/en/composer-for-salesforce/current/composer-for-administrators/creating-composer-templates/word-templates/word-template-basics/about-microsoft-word-merge-templates)
- [Conga Template Builder](https://documentation.conga.com/en/composer-for-salesforce/current/composer-for-administrators/creating-composer-templates/composer-template-basics/use-the-template-builder-to-construct-your-template)
- [Conga IF fields in Word templates](https://documentation.conga.com/en/composer-for-salesforce/current/composer-for-administrators/creating-composer-templates/word-templates/advanced-word-templates/how-to-compare-two-values-in-word-templates-using-if-statements)
- [Zebra ZD421 media and print specifications](https://docs.zebra.com/us/en/printers/desktop/zd421-and-zd621-desktop-printers-user-guide/media/general-media-and-print-specifications.html)
- [Zebra ribbon width and backing guidance](https://docs.zebra.com/us/en/printers/desktop/zd421-and-zd621-desktop-printers-user-guide/setup/thermal-transfer-roll-ribbon-loading/loading-non-zebra-300-meter-transfer-ribbon.html)
- [Zebra ZD421 configuration report](https://docs.zebra.com/us/en/printers/desktop/zd421-and-zd621-desktop-printers-user-guide/c-zd421-zd621-ug-tools/r-mlk-ug-printer-diagnostics/t-zd620zd420-ug-printing-the-printer-and-network-configuration-reports.html)
