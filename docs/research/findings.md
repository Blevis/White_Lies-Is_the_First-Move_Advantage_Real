---
title: 6. The conclusion
description: Two clear answers, with the limits that matter.
---

# 6. A small edge for White

<div class="study-answer" markdown="1">
**White earned about 51.8% of the points.**

The main estimate is **51.776%**, with a **95% interval of 51.653%–51.899%**. This is a small scoring edge in the games studied.
</div>

## The two answers

| Question | Answer |
| --- | --- |
| **Does White score more?** | Yes, in this sample's weighted analysis. The positive direction holds across the reported checks. |
| **Do Black's replies differ?** | In some groups. The evidence weakens sharply among closely matched players. |

**Score is not win rate.** Draws add half a point. White's weighted win rate was **49.533%**.

## What follows from this?

- The edge is **small**, and its size changes with the games included.
- The reply results **do not identify a best defense**.
- One month of observed games **does not prove cause and effect**.

## From games to evidence

**Collect → Check → Prepare → Analyze → Test assumptions → Report.**

The outputs include the validated sample, result tables, **11 graphs**, notebook and research reports.

??? info "Files and reproduction"
    Inputs are in `data/`; code in `src/`; results in `results/`; graphs in `figures/`; original reports in `reports/`. The root `analysis.ipynb` runs the same offline pipeline.

    After installing the scientific environment, use a separate output directory:

    ```bash
    python -m src.run_analysis --output-root /path/to/separate-output
    ```

    The saved sample and manifest are required. The run uses seed **202503** and **10,000 repetitions**. The default repository run can also regenerate the research README.

    Building the website reads saved group results; it does not rerun the statistics or publish individual games. [Full setup and output guide](../reproducibility/installation.md).

The [study reference](reference.md) collects the graphs, formulas and glossary. [Detailed methods](../methodology/data.md) and the [full report](report.md) provide the technical record.
