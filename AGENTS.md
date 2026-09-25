# Repository guidance

This repository is the workspace for the Zebra label printer project. It currently contains no application, driver package, or deployment configuration.

- Establish the requested printer model, host platform, label format, and intended workflow before adding implementation files.
- Keep source code and reproducible build instructions in the repository. Do not commit printer drivers, generated labels, print jobs, credentials, or operational records unless the user explicitly requests a reviewed artifact.
- For code changes, add a focused test first, confirm it fails for the expected reason, then implement and rerun it.
- Treat installation, physical printing, tenant changes, and deployment as separate actions that require a task-specific request.
- Report which checks ran and distinguish local validation from results on a printer or managed device.
