---
title: Output files and provenance
description: A map from website results and scientific figures to the authoritative CSV, JSON, Markdown and notebook artifacts.
---

# Follow a number back to its source

Scientific results live in `results/`, figures in `figures/`, and authoritative narratives in `reports/`. The website's JSON and rendered report are derived views, not an independent analysis.

| Source artifact | Contents | Used for |
| --- | --- | --- |
| `dataset_summary.json` | Manifest validation, sample accounting, raw and weighted outcomes | Provenance and scope |
| `h1_results.csv` | Overall, speed, band and speed-band estimates, intervals and test status | H1 charts and subgroup selection |
| `h1_summary.json` | Primary, raw, near-equal, standardized and dyadic results | Main finding and model comparisons |
| `h2_results.csv` | Cell eligibility, coverage, spread, distribution tests and corrected decisions | H2 cell interpretation |
| `h2_reply_scores.csv` | Reply counts, scores, marginal intervals and eligibility | Opening-reply explorer |
| `h2_summary.json` | Tested-cell and rejection totals, aggregate coverage | H2 headline findings |
| `robustness_results.csv` | H1 and H2 sensitivity scenarios | Robustness comparisons |
| `h2_sensitivity_cells.csv` | Matched-cell changes in ranges, decisions and selected extremes | Detailed H2 audit |
| `source_comparison.csv` | Explicit unavailability of a validated Explorer comparison | Historical-source caveat |
| `software_versions.json` | Versions used in the recorded scientific environment | Reproduction context |

Other exported tables document cleaning, daily and rating-speed coverage, first moves, replies, supplied PGN labels and model coefficients. Their names and roles remain available in the [repository results directory](https://github.com/Blevis/White_Lies-Is_the_First-Move_Advantage_Real/tree/main/results).

## Website asset generation

```bash
python scripts/build_docs_assets.py
python scripts/build_docs_assets.py --check
```

The generator reads completed aggregate outputs, emits `docs/assets/data/research.json`, copies the 11 final PNG/PDF figure pairs, and synchronizes the report and audit pages. The check mode detects stale generated assets. Source hashes identify the inputs used for the aggregate export.

The MkDocs build hook invokes this lightweight generation step. It never imports or runs the scientific pipeline and never exports individual game or player records.

## Final figures versus historical figures

Final March figures are `fig01_game_outcomes` through `fig10_h2_null_spread`, plus `h1_score_confidence_intervals`, each with PNG and PDF versions. The [annotated gallery](../explore/figures.md) explains all eleven.

Historical `q1_*`, `q2_*`, `draw_rate_by_band.*` and LaTeX files remain preserved in the repository, but are excluded from the website's final-study gallery because their Explorer period is unverified.

Read the [full report](../research/report.md), or download its [original Markdown](../assets/reports/FINAL_RESEARCH_REPORT.md).
