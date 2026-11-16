---
title: Installation
description: Separate Python environments for building the MkDocs website and reproducing the scientific analysis.
---

# Set up Python

Use **Python 3.11 or newer** and run commands from the repository root. Choose the website setup to preview pages, or the scientific setup to rerun the analysis.

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

Open the local address printed by MkDocs, normally `http://127.0.0.1:8000`. MkDocs copies the saved reports, charts and group results during the build. Use the local server to view the site; opening an HTML file directly can prevent the explorer from loading its data.

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

The analysis uses a separate set of packages. The versions used for the saved run are listed in [`results/software_versions.json`](https://github.com/Blevis/White_Lies-Is_the_First-Move_Advantage_Real/blob/main/results/software_versions.json). You also need the saved Parquet sample and its manifest. The full monthly archive is not bundled.

Continue with [running the analysis](running.md), [the notebook guide](notebook.md) or [validation](validation.md).
