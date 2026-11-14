---
title: Findings and interpretation
description: What the March study establishes, how large the observed associations are and where interpretation must remain limited.
---

# What the evidence says

The study finds a measurable scoring imbalance in favor of White and opening-reply associations in some defined groups. Its strongest conclusion is about **observed scoring patterns in eligible March 2025 Lichess games**.

## A detectable association with a modest magnitude

The primary score is **51.776%**, or **1.776 percentage points above 50%**. The narrow interval reflects a large observed sample under the stated sampling and dependence assumptions. Statistical detectability does not establish a large change in an individual player's chance of winning.

White's weighted outright-win share is **49.533%**, with **4.486% draws** and **45.980% Black wins**. A draw counts half toward White's expected score. Interchanging score, win probability and decisive-game win rate would change the question being answered.

## Several analyses support the direction

The near-equal-rating score of 51.819% and standardized score of 51.886% remain above 50%. Shared-player sensitivity produces a similar interval for the primary mean. These checks address particular assumptions; they do not create random assignment or remove every source of dependence.

The at-least-40-ply result is **50.769%**. Its **−1.007 pp** shift is a meaningful warning against treating the primary magnitude as universal. Conditioning on game length changes which outcomes enter the study.

## Reply associations are conditional

H2's **14 / 35 score** and **15 / 35 distribution** results belong to different corrected testing families. They neither show an association in every group nor identify a defense that would improve a particular player's outcome. The near-equal-rating sensitivity leaves only one score rejection among 28 tested cells.

| Supported interpretation | Why a broader claim is unsupported |
| --- | --- |
| White scores above 50% in the primary weighted analysis | Observational data do not isolate the causal effect of color |
| Reply distributions differ in some cells | Reply choice reflects player selection and other game conditions |
| Scores vary across rating bands | The pattern is not monotonic and bands are platform-specific |
| Some sparse cells are inconclusive | Lack of evidence does not establish equal scores |

Read the [limitations](limitations.md) alongside the [full report](report.md). The [interactive explorer](../explore/index.md) shows the recorded estimates without running additional tests in the browser.
