---
title: Output files and provenance
description: A map from website results and scientific figures to the authoritative CSV, JSON, Markdown and notebook artifacts.
---

# Find the source of a result

Tables and summaries are in `results/`, charts are in `figures/`, and original reports are in `reports/`. The website displays copies of these saved results.

| Source artifact | Contents | Used for |
| --- | --- | --- |
| `dataset_summary.json` | Manifest validation, sample accounting, raw and weighted outcomes | Provenance and scope |
| `h1_results.csv` | Overall, speed, band and speed-band estimates, intervals and test status | H1 charts and subgroup selection |
| `h1_summary.json` | Primary, raw, near-equal, standardized and dyadic results | Main finding and model comparisons |
| `h2_results.csv` | Which reply groups were tested, their coverage, and adjusted test results | H2 cell interpretation |
| `h2_reply_scores.csv` | Each reply’s game count, score, individual interval and inclusion status | Opening-reply explorer |
| `h2_summary.json` | Totals of tested groups and groups showing differences | H2 headline findings |
| `robustness_results.csv` | H1 and H2 sensitivity scenarios | Robustness comparisons |
| `h2_sensitivity_cells.csv` | How ranges and test results change for comparable reply groups | Detailed H2 audit |
| `source_comparison.csv` | Explicit unavailability of a validated Explorer comparison | Historical-source caveat |
| `software_versions.json` | Versions used in the recorded scientific environment | Reproduction context |

Other exported tables document cleaning, daily and rating-speed coverage, first moves, replies, supplied PGN labels and model coefficients. Their names and roles remain available in the [repository results directory](https://github.com/Blevis/White_Lies-Is_the_First-Move_Advantage_Real/tree/main/results).

## Refresh website copies

```bash
python scripts/build_docs_assets.py
python scripts/build_docs_assets.py --check
```

The generator reads completed aggregate outputs, emits `docs/assets/data/research.json`, copies the 11 final PNG/PDF figure pairs, and synchronizes the report and audit pages. The check command detects copies that no longer match their sources. Checksums record which source files were used.

MkDocs runs this copying step during each build. It does not run the analysis or export individual games and player names.

## Final figures versus historical figures

Final March figures are `fig01_game_outcomes` through `fig10_h2_null_spread`, plus `h1_score_confidence_intervals`, each with PNG and PDF versions. The [annotated gallery](../explore/figures.md) explains all eleven.

Historical `q1_*`, `q2_*`, `draw_rate_by_band.*` and LaTeX files remain preserved in the repository, but are excluded from the website's final-study gallery because their Explorer period is unverified.

Read the [full report](../research/report.md), or download its [original Markdown](../assets/reports/FINAL_RESEARCH_REPORT.md).
