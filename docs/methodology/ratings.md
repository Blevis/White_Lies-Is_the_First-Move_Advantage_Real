---
title: Rating and player checks
description: What happens when ratings are closely matched, modeled as equal, or games share a player.
---

# Checking ratings and repeated players

White might score more partly because of differences between the players. We checked measured rating differences in two ways, and separately checked how repeated players affect uncertainty.

## 1. Keep players with similar ratings

We kept games where the two players' ratings differed by at most **25 points**. This left **327,230 games** and a weighted White score of **51.819%**, with a **95% confidence interval of 51.637%–52.004%**.

White's score remained above 50%. Further checks used rating gaps of 10, 50 and 100 points.

This restriction studies a smaller set of games. Similar ratings also do not guarantee equal playing strength. In the reply analysis, less data and changed group coverage make the evidence much weaker.

## 2. Use a model to compare equal ratings

We fitted a model connecting White's score to the rating gap, game speed and rating band. We then used it to estimate the score if the players' recorded ratings were equal.

The estimated White score was **51.886%**, with a **95% interval of 51.707%–52.064%** that accounts for shared players. This supports the positive direction under the model's assumptions. It does not prove a causal effect of color.

??? info "Model specification"
    The model is an inverse-probability-weighted score-mean regression. It uses speed-band intercepts and a shared natural cubic spline of White-minus-Black rating difference, with interior knots at −200, −50, 0, 50 and 200.

    Predictions are evaluated at zero rating difference and averaged using the weighted speed-band mix. One sparse-cell row is omitted, leaving 836,069 games. The design has full rank, 32/32, and no fitted predictions fall outside [0,1]. The model does not include individual player-skill fixed effects.

## 3. Allow games involving the same player to be related

The sample contains **567,922 distinct player names**, compared without regard to capitalization. Of these, **296,939** appear more than once.

A shared-player uncertainty check gives a **51.655%–51.898%** interval for the main weighted score, close to the main bootstrap interval. This check also provides the equal-rating model's interval and exploratory score tests for two selected H2 groups.

The check allows games sharing a player to be related. It does not account for every connection through time, tournaments or player networks, and it does not replace all H2 simulations.

??? info "Shared-player calculation"
    The dyadic sandwich covariance estimator combines contributions from games sharing either player. It subtracts contributions for repeated unordered player pairs to avoid double counting, and assumes games with no shared player are independent.

    The [full report](../research/report.md#rating-and-dependence-adjustments) cites the dyadic variance method and records its implementation.

Continue with [testing other analysis choices](robustness.md), or return to [checks and limits](../research/limitations.md).
