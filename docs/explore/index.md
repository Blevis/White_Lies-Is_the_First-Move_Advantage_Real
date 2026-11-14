---
title: Interactive research explorer
description: Explore the validated March 2025 White Lies results with population filters, confidence intervals, outcome shares, opening replies, and sensitivity comparisons.
hide:
  - toc
---

# Follow the evidence

A small scoring difference. A large observational study. Explore **836,070 sampled games** through the estimates, intervals, and exclusions that give the findings their meaning.

This dashboard reads the final, exported March 2025 results. Filters select existing estimates; they do not run new significance tests. **White score counts a draw as half a point and is different from White win probability.**

<div data-wl-explorer>
  <p role="status">Loading the validated research aggregates…</p>
  <noscript><p>This explorer needs JavaScript. The <a href="../research/report/">full report</a> and <a href="figures/">scientific figures</a> provide the same research evidence without interactive controls.</p></noscript>
</div>

## Reading the dashboard

- **H1 filters** select time control, mean-rating band, and estimator. The speed comparison holds the selected rating band fixed; the rating comparison holds the selected speed fixed. Both comparison charts always use the published weighted estimates.
- **Unweighted estimates** describe the deliberately oversampled sample. Only the whole-sample unweighted interval is exported, so that option becomes unavailable when selecting a subgroup.
- **H2 filters** select a separate first-move / speed / rating cell. Only replies in a tested cell that meet the 200-game threshold enter the chart and table. Unavailable cells explain why they were not tested.
- **Gold points and lines** show White scores and exported 95% intervals. Focus or hover a chart row to read its full interval; the dashed line marks 50%. Each chart adapts its scale to the displayed uncertainty.
- **The sensitivity chart** always shows the same whole-study comparisons. The at-least-40-ply restriction changes the target population and materially reduces the estimated scoring difference.

!!! warning "Association, uncertainty, and selection"
    These are observational data from one site and one month. Ratings, opening choice, and repeated players complicate interpretation. A reply's interval is marginal; sorting or selecting an extreme does not make it a causal effect or a recommendation. A nonsignificant test does not prove equality.

Explore the [H1 analysis](../research/h1.md), [H2 analysis](../research/h2.md), [uncertainty methods](../methodology/uncertainty.md), and [robustness checks](../methodology/robustness.md) for the assumptions behind these views.

## Data provenance

The small [aggregate data file](../assets/data/research.json) contains exported group statistics, provenance hashes, and the published summaries. It contains no game records or player identifiers. The website build copies these values from `results/`; it neither re-runs the analysis nor downloads the source dump.

The authoritative sources are [`h1_results.csv`](https://github.com/Blevis/White_Lies-Is_the_First-Move_Advantage_Real/blob/main/results/h1_results.csv), [`h2_reply_scores.csv`](https://github.com/Blevis/White_Lies-Is_the_First-Move_Advantage_Real/blob/main/results/h2_reply_scores.csv), [`h2_results.csv`](https://github.com/Blevis/White_Lies-Is_the_First-Move_Advantage_Real/blob/main/results/h2_results.csv), and [`robustness_results.csv`](https://github.com/Blevis/White_Lies-Is_the_First-Move_Advantage_Real/blob/main/results/robustness_results.csv). See the [output guide](../reproducibility/outputs.md) to trace each view back to the research pipeline.
