---
title: Running the analysis
description: Supported offline analysis commands, input requirements, output locations and the separation between research execution and site builds.
---

# Run the March analysis

Activate the scientific environment and run commands from the repository root. The analysis works offline with the saved sample.

## Check the inputs

Both `data/games_2025-03.parquet` and its adjacent `.manifest.json` file are required. Before calculating results, the analysis checks the file checksum, March dates, sampling rates and selected game IDs. An incomplete sample cannot replace the validated input.

## Save a separate copy of the results

For an isolated reproduction, use the supported output-root option:

=== "Linux / macOS"

    ```bash
    python -m src.run_analysis --output-root /tmp/white-lies-reproduction
    ```

=== "Windows PowerShell"

    ```powershell
    python -m src.run_analysis --output-root "$env:TEMP\white-lies-reproduction"
    ```

The pipeline still reads the repository's validated input files, then writes `results/`, `figures/` and generated reports beneath the selected destination. This runs the full analysis, including 10,000 simulation repetitions, so it takes longer than building the website.

## Update results inside the repository

```bash
python -m src.run_analysis
python tests/mock_run.py
```

The default command writes research artifacts into the repository. It also invokes the existing report writer, which regenerates the research README. Review the resulting diff before keeping regenerated outputs or documentation changes. The scientific seed is **202503**; final simulation count is **10,000**.

## Execution stages

1. Validate the manifest and sample; record the cleaning ledger.
2. Export descriptive outcomes, coverage and opening frequencies.
3. Run weighted H1, rating standardization and shared-player sensitivity.
4. Run H2 reply grouping, eligibility, score spread and distribution tests.
5. Run robustness scenarios; export scientific figures and reports.
6. Verify that the expected artifacts exist and their contents are consistent.

The website reads these completed results. Building the site copies reports, charts and group summaries; it does not publish individual game records.

For the interactive research narrative, see [executing the notebook](notebook.md). For precise file roles, see [output files](outputs.md).
