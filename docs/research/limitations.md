---
title: 5. Checks and limits
description: The main changes under stricter comparisons, and the limits of the evidence.
---

# 5. Which findings hold up?

A **sensitivity check** repeats the analysis with another rule. White's score stays above 50%; reply findings change more.

## 1. Change the H1 sample { #step-1-change-which-games-enter-h1 }

| Games included | White score |
| --- | ---: |
| Main sample | **51.776%** |
| Players within 25 rating points | **51.819%** |
| At least 40 individual moves | **50.769%** |

**Keeping only longer games reduces the edge.** It also changes the question: valid short games and resignations are real outcomes.

??? info "All H1 checks and intervals"
    | H1 check | Sampled games | White score | 95% interval | Change from main |
    | --- | ---: | ---: | --- | ---: |
    | Main weighted result | 836,070 | 51.776% | 51.653%–51.899% | — |
    | Unweighted sample | 836,070 | 51.900% | 51.794%–52.005% | +0.124 pp |
    | Rating gap ≤10 | 158,880 | 51.735% | 51.475%–51.996% | -0.041 pp |
    | Rating gap ≤25 | 327,230 | 51.819% | 51.637%–52.004% | +0.042 pp |
    | Rating gap ≤50 | 509,899 | 51.882% | 51.730%–52.030% | +0.105 pp |
    | Rating gap ≤100 | 690,892 | 51.851% | 51.720%–51.980% | +0.075 pp |
    | Remove time forfeits | 665,036 | 52.149% | 52.013%–52.284% | +0.373 pp |
    | At least 10 individual moves | 827,981 | 51.700% | 51.578%–51.822% | -0.076 pp |
    | At least 40 individual moves | 688,011 | 50.769% | 50.637%–50.903% | -1.007 pp |
    | Rating bands starting at 1200 or above | 730,144 | 51.727% | 51.593%–51.858% | -0.049 pp |
    | Rating bands below 2200 | 625,850 | 51.757% | 51.633%–51.881% | -0.020 pp |
    | Remove classical games | 781,508 | 51.776% | 51.655%–51.899% | -0.000 pp |

    Every listed check remains above 50%. Keeping games with at least 40 plies—20 moves by each side—changes the score by **−1.007 percentage points**.

    $$
    \Delta_{\text{check}}=100(\widehat S_{\text{check}}-\widehat S_{\text{main}}).
    $$

    A 1-percentage-point change is a reporting flag, not a universal chess-importance threshold. Sensitivity p-values are exploratory and unadjusted; each listed H1 check reaches the simulation floor.

## 2. Tighten the H2 comparison { #step-2-change-the-h2-comparison-rules }

Among players within 25 rating points, **1 of 28 groups** shows score differences and **0 of 28** shows outcome-mix differences.

Fewer games and different coverage may explain part of the change. The analysis cannot separate their contributions.

??? info "All H2 checks"
    | H2 check | Tested groups | Score differences | Win/draw/loss differences |
    | --- | ---: | ---: | ---: |
    | Main comparison rules | 35 | 14 | 15 |
    | Minimum games per reply: 100 | 36 | 11 | 12 |
    | Minimum games per reply: 500 | 32 | 11 | 14 |
    | Minimum games per reply: 1000 | 26 | 13 | 15 |
    | All rating bands | 44 | 15 | 14 |
    | Rating gap ≤25 | 28 | 1 | 0 |
    | Remove time forfeits | 35 | 22 | 18 |
    | At least 10 individual moves | 35 | 13 | 13 |

    Each scenario has its own eligible groups and two correction families. Counts do not always refer to the same games, replies or groups.

## 3. Allow for repeated players { #step-3-account-for-repeated-players }

The sample has **567,922 players**; **296,939** appear more than once. Their games may be related.

A shared-player check gives **51.655%–51.898%** for White's main score—close to the original interval.

??? info "Shared-player formulas and model intervals"
    For the weighted mean, each game contributes:

    $$
    u_i=\frac{w_i(Y_i-\widehat S)}{\sum_i w_i}.
    $$

    Let $G_a$ contain player $a$'s games and $G_{ab}$ contain games between pair $\{a,b\}$. The variance combines player totals, subtracting pair totals to avoid double-counting:

    $$
    \widehat V_{\text{shared}}=
    \sum_a\left(\sum_{i\in G_a}u_i\right)^2
    -\sum_{\{a,b\}}\left(\sum_{i\in G_{ab}}u_i\right)^2.
    $$

    For positive variance, the interval is:

    $$
    \widehat S\pm1.96\sqrt{\widehat V_{\text{shared}}}.
    $$

    | Estimate being checked | White score | 95% interval | Interval method |
    | --- | ---: | --- | --- |
    | Main weighted estimate | 51.776% | 51.653%–51.899% | Sampling-aware bootstrap |
    | Same estimate, allowing shared players | 51.776% | 51.655%–51.898% | Shared-player variance |
    | Equal-rating model | 51.886% | 51.707%–52.064% | Model with shared-player variance |

    Games without a shared player are assumed independent. Time, tournament and network connections may remain. This method supports H1 and two selected H2 checks, not every H2 simulation.

    For those exploratory H2 score-equality checks, $\mathbf s$ holds reply scores, $\Sigma$ their covariance, and $A$ compares replies:

    $$
    Q=(A\mathbf s)^T(A\Sigma A^T)^{-1}(A\mathbf s).
    $$

    The large-sample reference is chi-square with $k-1$ degrees of freedom for $k$ replies. These exploratory p-values are unadjusted.

## 4. Keep the scope clear { #step-4-state-what-remains-uncertain }

- **One month and platform:** March 2025, Lichess, three rated speeds.
- **Observed choices:** players select openings; ratings cannot capture every strength difference.
- **Uneven data:** some groups are too small for a useful test.
- **Model assumptions:** sampling, related games and multiple testing all affect interpretation.

These results show **associations, not proven causes**.

??? info "Full limits"
    | Limit | What it means for the results |
    | --- | --- |
    | **One month and platform** | Conclusions concern selected March 2025 Lichess blitz, rapid and classical games; not a full year, over-the-board play or all chess players |
    | **Observed choices** | Color, opponents and replies are not a randomized experiment; measured associations do not prove cause and effect |
    | **Imperfect ratings** | Similar recorded ratings do not guarantee equal underlying strength; the model uses a shared rating curve and no individual player-skill effects |
    | **Approximate sampling model** | Hash selection is treated as approximately random sampling; estimates and intervals rely on that assumption |
    | **Related games** | Main simulations mostly assume independence; shared-player checks address only part of the possible dependence |
    | **Sparse groups and many tests** | Unavailable tests are inconclusive; selected high and low scores have extra uncertainty; adjustment relies on assumptions about related tests |
    | **Local source checks** | Matching a checksum verifies local consistency, not an independent authentication or rescan of the remote archive |
    | **Unverified older sources** | Archived Explorer dates and rating-group alignment cannot be verified; those results are excluded, and no complete new opening-code mapping is claimed |

[Detailed checks](../methodology/robustness.md) · [Rating and player methods](../methodology/ratings.md)

**Next: [6. The conclusion →](findings.md)**
