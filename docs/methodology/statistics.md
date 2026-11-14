---
title: Statistical methodology
description: White score, inverse-probability weighting, H1 and H2 test structures and the distinction between score and outcome distribution.
---

# From game outcomes to estimates

The analysis keeps three related quantities separate: expected score, outright-win probability and win probability among decisive games.

## Outcome definitions

For each game, White's score is $Y_i=1$ for a win, $Y_i=0.5$ for a draw and $Y_i=0$ for a loss. With observed outcome counts $W,D,B$ and $N=W+D+B$:

$$
S=\frac{W+D/2}{N}, \qquad P(W)=\frac{W}{N}, \qquad
P(W\mid\text{decisive})=\frac{W}{W+B}.
$$

Undefined quantities for empty groups or groups with no decisive games remain missing. They are not replaced by zero.

## Inverse-probability weighting

Each game's inclusion probability $p_i$ determines its weight:

$$
w_i=\frac{1}{p_i}, \qquad
\widehat S=\frac{\sum_i w_iY_i}{\sum_i w_i}.
$$

This ratio estimates the eligible source-game composition after unequal-rate sampling. Its denominator is an estimated population total, not an independent sample size. The **836,070 observed records** determine the available information. Kish effective N describes weight dispersion and is not a count of independent players.

## H1: compare White's score with 50%

The primary one-sided hypothesis concerns the overall weighted population. Null simulations preserve stratum draw probabilities and set White and Black win probabilities equal within each stratum. This stratum-by-stratum symmetry is stronger than a pooled-mean null alone. A separate design-based Wald check directly addresses the pooled mean and supports the same conclusion.

The exact decisive-game binomial cross-check applies to unweighted or equal-weight estimates. It is not an exact test for the unequal-weight pooled score. Details of the bootstrap and finite-simulation p-values are on the [uncertainty page](uncertainty.md).

## H2: compare replies inside a fixed cell

At each reply's observed sample size, the null simulates outcomes from the cell's pooled White/Draw/Black proportions. Two statistics are calibrated against 10,000 simulated tables:

1. The sample-size-weighted standard deviation of reply scores tests scoring differences.
2. Pearson's full-distribution statistic tests differences in all three outcome probabilities, re-estimating the pooled mix in every simulated table.

The observed maximum-minus-minimum range and its supplementary p-value are descriptive supporting outputs. The two primary testing families have separate multiplicity corrections. A reply's contrast with the remaining eligible replies is exploratory, and its interval is not adjusted for selection.

Source: [full report, methodology](../research/report.md#4-methodology); implementations in `src/stats.py`, `src/hypothesis_h1.py` and `src/hypothesis_h2.py`.
