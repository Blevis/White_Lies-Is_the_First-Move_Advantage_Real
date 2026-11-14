---
title: Rating and player dependence
description: Near-equal-rating restriction, equal-rating spline standardization and dyadic shared-player sensitivity.
---

# Accounting for ratings and recurring players

The primary weighted score pools observed games. Two additional approaches examine measured rating imbalance, and a dependence sensitivity recognizes that the same player can appear in many games.

## Restrict to near-equal ratings

The main restriction keeps games with an absolute White–Black rating difference of at most **25 Elo points**. It retains **327,230 games**, yielding a weighted White score of **51.819%** (95% CI **51.637%–52.004%**). Cutoffs of 10, 50 and 100 appear as additional sensitivity analyses.

This changes the study population. Similar ratings do not imply identical latent ability, and restrictions reduce available sample sizes and H2 coverage.

## Standardize to equal ratings

An inverse-probability-weighted score-mean regression uses speed-band intercepts and a natural cubic spline of White-minus-Black rating difference. Interior knots are −200, −50, 0, 50 and 200. It models the 0/0.5/1 outcome directly.

Predictions are evaluated at zero rating difference and averaged over the observed IPW speed-band composition. The standardized score is **51.886%**, with a **dyadic 95% interval of 51.707%–52.064%**. One sparse-cell row is omitted; the model uses 836,069 games, has full rank (32/32), and has no fitted predictions outside [0,1].

The model shares a rating curve across cells and does not use player-skill fixed effects. Its estimate is conditional on the model, not a causal effect of color.

## Shared-player dependence

The sample includes **567,922 distinct case-normalized player names**, with **296,939 recurring players**. Game N is not an independent-player count.

Dyadic sandwich covariance aggregates influence contributions for games sharing a player in either color and subtracts contributions for repeated unordered player pairs to avoid double counting. It permits shared-player dependence while assuming independence for disjoint-player games.

For the original weighted mean, this sensitivity gives **51.655%–51.898%**. The method also supplies the rating-standardized interval and exploratory score tests for two prespecified H2 cells. It does not account for every temporal or network dependency, nor cluster every H2 simulation.

Source: [full report, rating and dependence adjustments](../research/report.md#rating-and-dependence-adjustments). The report cites [Aronow, Samii and Assenova's dyadic variance estimator](https://arxiv.org/abs/1312.3398).
