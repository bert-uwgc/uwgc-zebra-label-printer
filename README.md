# UWGC Zebra Label Printer

This repository is a starting point for Zebra label printer work. No application or deployment files have been added yet.

The badge design starts with [label measurements](docs/label_dimensions.md), a [machine-readable draft specification](docs/badge-template-spec.json), and a [Conga template plan](docs/conga-template-plan.md). The plan uses placeholder Salesforce fields until their exact merge names are available.

## Use with ChatGPT and Codex

In the ChatGPT desktop app, add this repository folder as a local project and make it the primary folder. Codex will then discover the repository guidance in [AGENTS.md](AGENTS.md). In Codex CLI, start a session from this directory.

Connecting the GitHub repository to Codex cloud is an account-level step: select `bert-uwgc/uwgc-zebra-label-printer` when connecting GitHub, then create an environment for it. The local files alone do not establish that connection.
