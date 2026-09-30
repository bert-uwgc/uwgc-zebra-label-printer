# UWGC Zebra Label Printer

This repository is a starting point for Zebra label printer work. No application or deployment files have been added yet.

The badge design starts with [label measurements](docs/label_dimensions.md), a [machine-readable draft specification](docs/badge-template-spec.json), and a [Conga template plan](docs/conga-template-plan.md). The plan uses placeholder Salesforce fields until their exact merge names are available.

## Fill and print a badge without Salesforce

Open [the blank fillable badge PDF](output/pdf/manual-badge-label.pdf) in a PDF viewer that supports forms. Click the large name area, then enter the organization and any board affiliations in the fields below it. Enter `Individual Donor` when there is no organization; append ` (Retired)` to an organization when applicable. Leave unused board lines empty. Preview the filled label before printing.

The name uses a fixed, prominent font so browser PDF viewers display it consistently. If a long name extends beyond the field, use an approved shorter display name before printing.

Print at **Actual size / 100%** on 79 x 50 mm media, one PDF page per label. The page includes the 1.5 mm liner offset on each side of the 76 mm sticker. Form values and layout were checked locally; a physical printer check is still needed.

To rebuild the blank PDF, install `pymupdf` and `pypdf`, then run `python tools/build_fillable_badge_pdf.py`. The output contains no Salesforce merge fields or prefilled badge data.

## Use with ChatGPT and Codex

In the ChatGPT desktop app, add this repository folder as a local project and make it the primary folder. Codex will then discover the repository guidance in [AGENTS.md](AGENTS.md). In Codex CLI, start a session from this directory.

Connecting the GitHub repository to Codex cloud is an account-level step: select `bert-uwgc/uwgc-zebra-label-printer` when connecting GitHub, then create an environment for it. The local files alone do not establish that connection.
