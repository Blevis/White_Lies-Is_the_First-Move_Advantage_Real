---
title: Notebook guide
description: How to inspect and execute the authoritative analysis notebook without using the archived historical generator.
---

# Read the analysis as a notebook

`analysis.ipynb` is the executed scientific notebook at the repository root. It imports the `src` package, reruns the same offline March pipeline and displays the exported evidence with interpretation. The recorded notebook contains **24 cells**, including **10 executed code cells** with no saved error outputs.

## Open it interactively

With the scientific requirements installed and the repository root as your working directory:

```bash
python -m jupyter notebook analysis.ipynb
```

Choose the kernel from your scientific environment. The retained Parquet sample and manifest must be available. Reading the saved notebook does not require rerunning it; executing its analysis cell runs the full scientific computation.

## Execute and save the results

The repository's supported command is:

```bash
python -m jupyter nbconvert --to notebook --execute --inplace analysis.ipynb --ExecutePreprocessor.timeout=600
```

This command updates the notebook in place and the notebook's analysis pipeline regenerates research artifacts. Save or review existing changes before execution. The 600-second setting is a per-cell timeout, not a guarantee of total execution duration on every machine.

## A reading route

Start with provenance and sample accounting, then follow the definitions of score and weights. Read H1 alongside its rating adjustments and uncertainty, and read H2 alongside its eligibility and coverage. Finish with robustness and limitations before interpreting any selected reply extremes.

The site provides the same route through [dataset](../methodology/data.md), [H1](../research/h1.md), [H2](../research/h2.md) and [robustness](../methodology/robustness.md) pages. The [full report](../research/report.md) is synchronized from the repository's authoritative Markdown report.

!!! warning "Archived generator"
    `original_project/build_notebook.py` belongs to the historical project. It must not replace the repaired root notebook. Historical Explorer graphics and unverified aggregate dates do not support the final March claims.

See [validation and testing](validation.md) for checks of saved execution state and artifact consistency.
