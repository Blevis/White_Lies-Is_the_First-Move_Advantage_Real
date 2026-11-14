---
title: Installation
description: Separate Python environments for building the MkDocs website and reproducing the scientific analysis.
---

# Start with the environment you need

Use **Python 3.11 or newer** and run commands from the repository root. Building the website only needs documentation dependencies and the committed aggregate outputs. It does not need to rerun the scientific pipeline or download games.

## Build the website

=== "Linux / macOS"

    ```bash
    python3 -m venv .venv-docs
    source .venv-docs/bin/activate
    python -m pip install -r requirements-docs.txt
    python -m mkdocs serve
    ```

=== "Windows PowerShell"

    ```powershell
    py -3 -m venv .venv-docs
    .\.venv-docs\Scripts\Activate.ps1
    python -m pip install -r requirements-docs.txt
    python -m mkdocs serve
    ```

Open the local address printed by MkDocs, normally `http://127.0.0.1:8000`. The build hook synchronizes final reports, figures and compact aggregate JSON from the existing research outputs. The explorer requires serving the site over HTTP; opening a generated HTML file directly can prevent its JSON fetch.

For a production build:

```bash
python -m mkdocs build --strict
```

The compiled site goes to `site/`, which is ignored by Git. A website build never executes the notebook or the research analysis.

## Install the scientific environment

=== "Linux / macOS"

    ```bash
    python3 -m venv .venv
    source .venv/bin/activate
    python -m pip install -r requirements.txt
    ```

=== "Windows PowerShell"

    ```powershell
    py -3 -m venv .venv
    .\.venv\Scripts\Activate.ps1
    python -m pip install -r requirements.txt
    ```

The scientific requirements are preserved separately. The versions used for the recorded run are listed in [`results/software_versions.json`](https://github.com/Blevis/White_Lies-Is_the_First-Move_Advantage_Real/blob/main/results/software_versions.json). The manifest and retained Parquet sample must be present for full reproduction; the complete monthly compressed source is not bundled.

Continue with [running the analysis](running.md), [the notebook guide](notebook.md) or [validation](validation.md).
