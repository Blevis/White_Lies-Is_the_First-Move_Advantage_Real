---
title: Scores, weights and tests
description: The measures and comparisons used to answer the two research questions.
---

# How the comparisons work

We measure White's share of points, adjust for unequal sampling rates, then test the overall score and differences between opening replies.

## Three measures that answer different questions

| Measure | Calculation | Question it answers |
| --- | --- | --- |
| White score | (White wins + half the draws) / all games | What share of points did White earn? |
| White win rate | White wins / all games | How often did White win? |
| White win rate in games with a winner | White wins / (White wins + Black wins) | When the game was not drawn, how often did White win? |

An empty group has no score. A group containing only draws has a score of 50%, but no win rate among games with a winner. Undefined values remain missing, rather than being replaced by zero.

## Why use weights?

Some games had a 1% sampling rate and others a 10% rate. Their weights are 100 and 10 respectively. We multiply each game's score by its weight, add those weighted scores, then divide by the sum of weights.

The result estimates White's score for the original eligible game mix. **The sample size is still 836,070 observed games.** The larger total represented by the weights does not add new observations.

??? info "Score and weighting formulas"
    Let $W$, $D$ and $B$ be White wins, draws and Black wins. Then:

    $$
    S=\frac{W+D/2}{W+D+B}.
    $$

    For a game with score $Y_i$ and inclusion probability $p_i$:

    $$
    w_i=\frac{1}{p_i}, \qquad
    \widehat S=\frac{\sum_i w_iY_i}{\sum_i w_i}.
    $$

    This is a ratio estimate. Its weighted denominator estimates a population total. The reported Kish effective sample size describes how unequal the weights are; it does not count independent players.

## H1: is White's score above 50%?

The main test compares the overall weighted score with **50%**. It asks whether a score at least as high as the observed one would be unusual in simulated games where White and Black have equal winning chances.

The simulations keep the draw rate in each speed-and-rating group. They set White and Black win rates equal within each group. A separate check directly tests the overall average and supports the same conclusion.

An exact binomial check uses only games with a winner. It applies to unweighted or equal-weight results, not the combined unequal-weight score.

## H2: do outcomes differ between replies?

Within each first-move, speed and rating group, we simulate games where all eligible replies share the same White-win, draw and Black-win probabilities. We keep each reply's observed sample size and compare two measures:

1. **Score differences:** how spread out the reply scores are, giving more weight to replies with more games.
2. **Win/draw/loss differences:** how much the three outcome proportions differ between replies.

The tests use 10,000 simulations. Each set of tests has its own adjustment for multiple comparisons. Comparing a selected reply with the rest is exploratory; it does not establish a best defense.

??? info "Technical H2 statistics"
    The score test uses the sample-size-weighted standard deviation of reply scores. The full-outcome test uses Pearson's statistic, with the pooled outcome mix estimated again in each simulated table.

    The maximum-minus-minimum score range and its supplementary p-value are descriptive supporting results. Intervals for individual reply contrasts are not adjusted for selecting extreme scores.

## Terms used in the results

| Term | Meaning here |
| --- | --- |
| Expected score | Average points earned per game |
| Confidence interval | A range showing uncertainty around an estimated score under the method's assumptions |
| Null model | The equal-score or equal-outcome scenario used for the comparison |
| p-value | How often that model produces a result at least as extreme as the observed one |
| Adjusted p-value, or q-value | A test result adjusted for running a family of comparisons |
| Cell | A group with a fixed first move, speed and rating band in the reply analysis |
| Percentage point (pp) | The difference between percentages: 51.8% is 1.8 points above 50% |

See [understanding uncertainty](uncertainty.md) for intervals and testing limits, or the [full methodology](../research/report.md#4-methodology) for implementation details.
