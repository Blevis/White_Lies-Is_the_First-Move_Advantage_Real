---
title: Robustness and sensitivity
description: How game length, ratings, time forfeits, weighting and reply thresholds change estimates and tested-cell decisions.
---

# Stable direction, sensitive magnitude

Every reported H1 sensitivity remains above 50% and statistically detectable under its test assumptions. That consistency does **not** imply an invariant effect size.

## The game-length result matters

The primary analysis retains legitimate short games. Requiring at least **40 plies** leaves **688,011 games** and gives a weighted White score of **50.769%** (95% CI **50.637%–50.903%**). This is **1.007 percentage points below** the primary 51.776% estimate.

Game length is determined after the opening. Conditioning on it changes the population and removes valid short outcomes. The result demonstrates sensitivity in magnitude; it is not a reason to silently replace the primary sample.

| H1 scenario | Observed N | White score | 95% interval | Change from primary |
| --- | ---: | ---: | --- | ---: |
| Primary weighted | 836,070 | 51.776% | 51.653%–51.899% | — |
| Unweighted sample | 836,070 | 51.900% | 51.794%–52.005% | +0.124 pp |
| Rating gap ≤25 | 327,230 | 51.819% | 51.637%–52.004% | +0.042 pp |
| Exclude time forfeits | 665,036 | 52.149% | 52.013%–52.284% | +0.373 pp |
| At least 10 plies | 827,981 | 51.700% | 51.578%–51.822% | −0.076 pp |
| At least 40 plies | 688,011 | 50.769% | 50.637%–50.903% | −1.007 pp |

Additional reported checks restrict bands and exclude classical games. The full table appears in the [authoritative report](../research/report.md#7-discussion-and-robustness) and `results/robustness_results.csv`. A 1 pp change is the study's transparent descriptive flag, not a universal threshold for chess importance. Sensitivity p-values are exploratory and unadjusted.

## H2 changes with eligibility and selection

| H2 scenario | Tested cells | Score rejections | Distribution rejections |
| --- | ---: | ---: | ---: |
| Primary | 35 | 14 | 15 |
| Reply floor 100 | 36 | 11 | 12 |
| Reply floor 500 | 32 | 11 | 14 |
| Reply floor 1000 | 26 | 13 | 15 |
| All rating bands | 44 | 15 | 14 |
| Rating gap ≤25 | 28 | 1 | 0 |
| Exclude time forfeits | 35 | 22 | 18 |
| At least 10 plies | 35 | 13 | 13 |

Each H2 scenario has its own correction families. Tested groups and selected extremes can change, so these counts are not a comparison over an identical set of cells. Near-equal restriction attenuates evidence, with sample-size loss and confounding both plausible contributors. Constant weights within a fixed speed-band cell cannot change its H2 scores.

[Compare recorded sensitivities interactively](../explore/index.md) · [Read the limitations](../research/limitations.md)
