---
title: Understanding uncertainty
description: How to read confidence intervals, p-values and adjustments for multiple tests.
---

# How certain are the results?

A score calculated from a sample is an estimate. Confidence intervals show its uncertainty, while statistical tests compare it with a defined scenario such as equal scoring.

The analysis uses **10,000 repeated simulations** and a fixed random seed of **202503**. The website displays the saved results; changing a filter does not run a new test.

## Read a confidence interval

The main White score is **51.776%**, with a **95% confidence interval of 51.653%–51.899%**.

The point is the estimated score. The interval shows uncertainty around that estimate under the analysis assumptions. A narrower interval means greater precision, not a larger advantage.

A method producing 95% confidence intervals aims to cover the target score in 95% of repeated samples under those assumptions. It does not assign a 95% probability to this particular fixed interval, describe 95% of individual game outcomes, or remove bias from player selection.

Each displayed interval applies to its own estimate. The whole collection is not a guarantee that every interval covers its target at once.

## What does a small p-value mean?

A p-value measures how often the null model produces a result at least as extreme as the observed one. A small value suggests that the model does not describe the observed result well.

It does not measure the probability that the hypothesis is true, the size of the scoring edge, or whether moving first caused the difference.

With 10,000 simulations, the smallest reported Monte Carlo p-value is **1/10001**, or about **0.0001**. The main H1 result reaches that limit: none of those simulations produced a score as high as the observed score. It does not mean the probability is zero or that we know its exact value below that limit.

## Why adjust for many tests?

Running many tests creates more opportunities to flag differences by chance. The study uses **Benjamini–Hochberg adjustment** to address this across defined sets of tests. The tables label the adjusted values as **q-values** and use a 0.05 threshold.

| Set of tests | Adjustment scope |
| --- | --- |
| Main overall H1 test | One planned test, kept separate |
| H1 subgroups | 38 eligible tests across speeds, ratings and their combinations |
| H2 score differences | 35 eligible first-move, speed and rating groups |
| H2 win/draw/loss differences | A separate set of tests for the same 35 groups |

The adjustment relies on assumptions about relationships between tests. Repeated players and overlapping groups limit how strictly its usual false-discovery guarantees apply. A test that does not pass the threshold does not prove equal outcomes.

## Why repeated players matter

Games involving the same player may be related. Most main simulations treat games as independent. A separate shared-player check allows related outcomes when games share a player, for H1 and two selected H2 groups. It still assumes games with no shared player are independent.

See [rating and player checks](ratings.md) for the scope of that check.

??? info "How the intervals are calculated"
    **H1:** a sampling-aware Poisson multiplier bootstrap varies observed counts by speed, rating band and outcome. It recalculates both the weighted score total and the total weight on each repetition. Centered deviations use $\sqrt{1-p}$ to account for the sampling fraction. The interval uses bootstrap percentiles. The unweighted check omits that finite-population scaling.

    **H2:** each reply uses a multinomial bootstrap. Sparse or constant-outcome groups use conservative exact binomial bounds for White and Black win probabilities, transformed through $S=(1+P(W)-P(B))/2$.

    Individual reply intervals are not adjusted for searching for the highest or lowest score. They cannot guarantee an ordering of defenses.

See the [full methods](../research/report.md#4-methodology) and [research audit](../project/audit.md) for the recorded statistical choices.
