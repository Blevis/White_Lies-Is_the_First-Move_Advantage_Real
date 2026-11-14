---
title: Confidence intervals and testing
description: Sampling-aware bootstrap intervals, finite Monte Carlo resolution, multiplicity correction and shared-player dependence assumptions.
---

# What the uncertainty means

The final analysis fixes the seed at **202503** and uses **10,000 replicates**. Intervals and tests are precomputed in Python; website filters select recorded results and do not run new inferential tests.

## H1 bootstrap intervals

Weighted H1 compresses observed games by speed, rating band and outcome. Poisson count multipliers are equivalent to independent Poisson(1) observation multipliers. Centered deviations are rescaled by $\sqrt{1-p}$ for the Bernoulli finite-population correction.

Both the weighted numerator and denominator are recomputed for each replicate. This allows uncertainty in stratum mass as well as outcomes. The reported 95% interval uses the bootstrap percentiles. Unweighted sensitivity uses an analogous Poisson bootstrap without finite-population scaling.

These are **pointwise intervals**, not simultaneous guarantees across all displayed groups. Their interpretation depends on the sampling approximation and outcome-dependence assumptions.

## Monte Carlo p-values have a floor

The one-sided H1 p-value is:

$$
p_{MC}=\frac{1+\#\{\text{simulated scores}\geq\text{observed score}\}}{10000+1}.
$$

The smallest possible reported value is **1/10001 ≈ 9.999e-05**. A floor value means no simulated statistic was at least as extreme in this run. It does not mean the probability is zero, nor measure an exact probability below that resolution. H2 uses finite-simulation corrections as well.

## H2 reply intervals

Reply scores use a 10,000-replicate multinomial bootstrap. Sparse or constant outcomes use conservative simultaneous exact binomial bounds for White and Black win probabilities, transformed through $S=(1+P(W)-P(B))/2$.

Those reply intervals are marginal. Selecting the highest and lowest observed replies introduces extra uncertainty that these intervals do not correct. The full collection of replies should not be read as a definitive ranking.

## Multiplicity and dependence

| Family | Correction scope |
| --- | --- |
| Primary H1 | One prespecified test; excluded from subgroup correction |
| Secondary H1 | 38 eligible speed, band and speed-by-band tests together |
| H2 score spread | 35 eligible primary cells |
| H2 full distribution | A separate family of the same 35 cells |

Benjamini–Hochberg adjustment uses its standard dependence assumptions. Overlapping subgroups and recurring players limit literal false-discovery guarantees. A dyadic sensitivity analysis permits shared-player covariance for H1 and two prespecified H2 cells, while assuming disjoint-player games are independent. It does not replace all H2 simulations with clustered tests.

Sources: [full report, methods](../research/report.md#4-methodology), [research audit](../project/audit.md), and [rating and dependence adjustments](ratings.md).
