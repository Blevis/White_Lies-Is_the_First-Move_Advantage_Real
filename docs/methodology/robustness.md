---
title: Testing other analysis choices
description: Which findings hold up when we change the games included or the minimum reply counts.
---

# What changes when we make different choices?

A **sensitivity check** repeats the analysis after changing a rule or assumption. White’s score remains above 50% in every reported check, but the size of the edge changes. Reply differences are less consistent.

## Keeping only longer games reduces the edge

The main analysis keeps valid short games. Requiring at least **40 plies**—40 individual moves, or 20 moves by each side—leaves **688,011 games**. White’s weighted score falls to **50.769%** (95% CI **50.637%–50.903%**), **1.007 percentage points below** the main result.

Game length is known only after play. Removing short games changes the set of outcomes we study. This check shows why the precise size of the scoring edge should not be treated as universal.

| White-score check | Sampled games | White score | 95% interval | Change from main result |
| --- | ---: | ---: | --- | ---: |
| Main weighted result | 836,070 | 51.776% | 51.653%–51.899% | — |
| Unweighted sample | 836,070 | 51.900% | 51.794%–52.005% | +0.124 pp |
| Rating gap ≤25 | 327,230 | 51.819% | 51.637%–52.004% | +0.042 pp |
| Exclude time forfeits | 665,036 | 52.149% | 52.013%–52.284% | +0.373 pp |
| At least 10 plies | 827,981 | 51.700% | 51.578%–51.822% | −0.076 pp |
| At least 40 plies | 688,011 | 50.769% | 50.637%–50.903% | −1.007 pp |

Other checks limit rating bands or exclude classical games. The [full report](../research/report.md#7-discussion-and-robustness) and `results/robustness_results.csv` record them all. Here, **pp** means percentage points. The study flags changes of at least 1 point for attention; this is a reporting choice, not a universal measure of chess importance. These checks use exploratory, unadjusted p-values.

## Reply findings change with the comparison rules

| Reply-analysis check | Tested groups | Groups with score differences | Groups with win/draw/loss differences |
| --- | ---: | ---: | ---: |
| Main analysis | 35 | 14 | 15 |
| Minimum 100 games per reply | 36 | 11 | 12 |
| Minimum 500 games per reply | 32 | 11 | 14 |
| Minimum 1,000 games per reply | 26 | 13 | 15 |
| All rating bands | 44 | 15 | 14 |
| Rating gap ≤25 | 28 | 1 | 0 |
| Exclude time forfeits | 35 | 22 | 18 |
| At least 10 plies | 35 | 13 | 13 |

Each row has its own adjustment for multiple tests. The eligible groups can change between rows, so the counts do not compare exactly the same games.

Keeping players within 25 rating points weakens the reply evidence substantially. This may reflect fewer games, changes in who is compared, or both; the analysis cannot separate those explanations. Within a fixed speed-and-rating group, every game has the same sampling weight, so weighting does not change the reply scores.

[Compare recorded sensitivities interactively](../explore/index.md) · [Read the limitations](../research/limitations.md)
