# UWGC Zebra Label Printer

This repository is a starting point for Zebra label printer work. No application or deployment files have been added yet.

The badge design starts with [label measurements](docs/label_dimensions.md), a [machine-readable draft specification](docs/badge-template-spec.json), and a [Conga template plan](docs/conga-template-plan.md). The plan uses placeholder Salesforce fields until their exact merge names are available.

## Fill and print a badge without Salesforce

Open [the revised blank fillable badge PDF](output/pdf/manual-badge-label-v2.pdf) in Adobe Acrobat or another PDF form viewer. Click the large name area, then enter the organization and any board affiliations in the fields below it. Enter `Individual Donor` when there is no organization; append ` (Retired)` to an organization when applicable. Leave unused board lines empty. **Save a copy** of the filled form.

For consistent text sizing, make a print-ready copy from the saved form:

```text
python tools/prepare_manual_badge_for_print.py "path\to\filled-badge.pdf"
```

This writes `filled-badge-print-ready.pdf` beside the saved form. It centers all lines, renders the name bold at up to 28 pt, and reduces long lines to fit. If a line cannot fit legibly, the command asks for a shorter display value. The filled form's editing preview may clip long text; **print the print-ready copy**.

Print at **Actual size / 100%** on 79 x 50 mm media, one PDF page per label. The page includes the 1.5 mm liner offset on each side of the 76 mm sticker. Form values and layout were checked locally; a physical printer check is still needed.

Install `pymupdf` and `pypdf` to use the preparation command. To rebuild the blank PDF, run `python tools/build_fillable_badge_pdf.py`. The blank PDF contains no Salesforce merge fields or prefilled badge data.

## Use with ChatGPT and Codex

In the ChatGPT desktop app, add this repository folder as a local project and make it the primary folder. Codex will then discover the repository guidance in [AGENTS.md](AGENTS.md). In Codex CLI, start a session from this directory.

Connecting the GitHub repository to Codex cloud is an account-level step: select `bert-uwgc/uwgc-zebra-label-printer` when connecting GitHub, then create an environment for it. The local files alone do not establish that connection.
