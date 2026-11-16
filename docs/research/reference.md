---
title: Study reference
description: Quick links to graphs, calculations, terms and source files.
---

# Graphs, formulas and concepts

A quick reference for the study. Open a topic for its definitions or calculation details.

## Graph index

| Graph | Type | Main finding |
| --- | --- | --- |
| [05 — Rating gap](approach.md#graph-05-are-opponents-closely-matched) | Histogram | A balanced average can hide unequal opponents |
| [06 — Sample coverage](approach.md#graph-06-where-do-we-have-enough-games) | Heatmap with logarithmic colors | Some speed-rating groups have very little data |
| [01 — Recorded outcomes](h1.md#graph-01-what-happened-in-the-sampled-games) | Bar chart | Counts describe the sample before weighting; draws matter |
| [H1 — Overall and subgroup intervals](h1.md#h1-interval-graph-the-overall-result-in-context) | Forest plot | The main score and its uncertainty lie above 50% |
| [03 — Score by speed](h1.md#graph-03-does-the-pattern-appear-at-different-speeds) | Point-and-error-bar chart | Scores are close across speeds, without proving equality |
| [02 — Score by rating](h1.md#graph-02-does-the-edge-grow-with-rating) | Point-and-error-bar chart | The score does not steadily rise with rating |
| [04 — Draw rates](h1.md#graph-04-why-keep-draws-in-the-analysis) | Multi-series line chart | Draw frequency varies, so a binary win/loss measure loses information |
| [07 — Replies to e4](h2.md#graph-07-replies-after-1e4) | Three-panel forest plot | Reply scores, intervals and coverage vary |
| [08 — Replies to d4](h2.md#graph-08-replies-after-1d4) | Three-panel forest plot | Reply scores and precision vary by speed |
| [10 — Simulated null spread](h2.md#graph-10-observed-spread-against-the-null-model) | Two histograms with observed-value lines | Compare real spread with the equal-outcome simulations |
| [09 — Reply-score ranges](h2.md#graph-09-how-wide-are-the-observed-reply-score-ranges) | Two-panel heatmap | A large observed range is not automatically a significant or causal difference |

## Formula index

??? info "Find a calculation"
    | Concept | Calculation |
    | --- | --- |
    | Score, win/draw/loss rates and decisive-game win rate | [Questions — measures](question.md#score-win-rate-and-draw-rate) |
    | Repeatable selection, $u_i<\pi_i$, and source-count accounting | [Data — sampling](approach.md#step-2-apply-eligibility-rules-and-sample-by-game-id) |
    | Average rating, rating gap, score mapping, weights and effective sample size | [Data — prepared fields](approach.md#step-5-prepare-the-fields-used-in-analysis) |
    | H1 hypotheses, raw and weighted score, difference in percentage points | [H1 — comparison](h1.md#step-1-define-the-comparison) and [score](h1.md#step-3-calculate-the-score-and-apply-weights) |
    | Bootstrap percentiles and finite-population correction | [H1 — bootstrap](h1.md#bootstrap-how-much-could-the-estimate-vary) |
    | Draw-preserving null simulation and Monte Carlo p-value | [H1 — null model](h1.md#null-simulation-would-equal-scoring-produce-this-result) |
    | Pooled-mean Wald variance and exact decisive-game binomial check | [H1 — cross-checks](h1.md#cross-checks-test-the-result-another-way) |
    | Benjamini–Hochberg adjusted p-values | [H1 — multiple tests](h1.md#adjust-subgroup-tests-for-multiple-comparisons) |
    | Rating regression and equal-rating standardization | [H1 — rating checks](h1.md#step-6-check-ratings-and-repeated-players) |
    | H2 outcome-vector hypothesis and coverage | [H2 — question](h2.md#step-1-define-the-hypothesis-and-comparison-groups) and [eligibility](h2.md#step-2-decide-which-replies-have-enough-data) |
    | Reply score, bootstrap interval and exact-bound transformation | [H2 — reply estimates](h2.md#step-3-calculate-and-plot-each-replys-score) |
    | Pooled outcome probabilities, simulated tables, score SD and Pearson statistic | [H2 — two tests](h2.md#step-4-simulate-equal-outcomes-and-run-two-tests) |
    | Score range, noise-adjusted spread and reply-versus-rest contrast | [H2 — summary measures](h2.md#step-5-summarize-all-eligible-groups) |
    | Change from the main result | [Checks — H1 selections](limitations.md#step-1-change-which-games-enter-h1) |
    | Shared-player variance, interval and exploratory H2 Wald statistic | [Checks — repeated players](limitations.md#step-3-account-for-repeated-players) |

## Glossary

??? info "Chess and outcomes"
    | Term | Meaning |
    | --- | --- |
    | **Score** | White's average points per game: win 1, draw ½, loss 0 |
    | **Win rate** | The share of games White wins; draws do not add to it |
    | **Percentage point** | A difference between percentages: 51.8% is 1.8 percentage points above 50% |
    | **Rating** | An estimate of playing strength, specific to the platform and game speed |
    | **Rating band** | A group based on the average of the two players' ratings |
    | **Time control** | The thinking time available; the study uses blitz, rapid and classical categories |
    | **Ply** | One individual player's move; 20 plies are ten moves by each side |
    | **Cell** | One first move, time control and rating band in H2 |

??? info "Sampling and data checks"
    | Term | Meaning |
    | --- | --- |
    | **Hash sampling** | Repeatable selection based on a number calculated from each game ID |
    | **Sampling weight** | The inverse of a game's selection rate: 100 for a 1% rate, 10 for a 10% rate |
    | **Effective sample size** | A diagnostic of unequal weights; not a count of independent players. |
    | **Provenance** | The record connecting a dataset to its source, collection settings and checks |
    | **Manifest** | The file recording those settings, counts, completion status and checksum |
    | **Checksum** | A file fingerprint used to check whether the local data agree with the recorded file |
    | **Exploratory data analysis (EDA)** | Summaries and plots used to understand the data and identify coverage or quality problems |
    | **Descriptive statistics** | Counts and summaries of the observed games |
    | **Statistical inference** | Using sample data to estimate or test population patterns under stated assumptions. |

??? info "Uncertainty and tests"
    | Term | Meaning |
    | --- | --- |
    | **Null hypothesis** | The benchmark model used in a test, such as equal scoring or equal outcome probabilities |
    | **p-value** | Under the null model, how often a statistic is at least as extreme as the observed one |
    | **Significance level** | The decision threshold chosen in advance; 0.05 for the main test |
    | **One-sided test** | A test looking for a difference in a specified direction; here, White scoring above 50% |
    | **Confidence interval** | A range built to cover its target in a stated share of repeated samples, under the method’s assumptions. |
    | **Bootstrap** | Reusing the observed data to generate repeated estimates and measure their variation |
    | **Monte Carlo test** | Simulating datasets under a null model to calibrate a test statistic |
    | **Standard deviation (SD)** | A measure of how spread out values are around their average |
    | **Standard error** | Estimated variation of an estimate across repeated samples; a measure of precision |
    | **Wald test** | A test using an estimate's distance from a benchmark and its standard error |
    | **Exact binomial test** | Tests a two-outcome count; used here for decisive games with equal or absent weights. |
    | **Multinomial simulation** | Draws counts for White wins, draws and Black wins, keeping the total fixed. |
    | **Pearson statistic** | A measure of how much observed outcome counts differ from the counts expected under the null model |
    | **Multiple testing** | Running several related tests, creating more opportunities to flag differences by chance |
    | **Benjamini–Hochberg adjustment** | Limits the expected share of false discoveries across a test family, subject to its assumptions. |
    | **Adjusted p-value / q-value** | The BH-adjusted p-value used to decide which subgroup tests pass the threshold |

??? info "Models and conclusions"
    | Term | Meaning |
    | --- | --- |
    | **Spline regression** | A model with a flexible curve made of smoothly joined pieces |
    | **Dyadic / shared-player interval** | Allows games sharing either player to be related; assumes other games are independent. |
    | **Sensitivity analysis** | Repeating an analysis with alternative filters or assumptions to see what changes |
    | **Statistical significance** | Evidence against a specified null model under the test's assumptions |
    | **Practical significance** | The size and possible importance of a difference, rather than its detectability alone |
    | **Association** | Outcomes vary together with color or reply choice in the recorded games |
    | **Causation** | Changing color or reply would itself change the outcome; these observed games do not establish that claim |

## From code to evidence

??? info "Code and output files"
    | Location | Role |
    | --- | --- |
    | `src/fetch_games.py` | Streams the archive, applies collection rules, samples games and writes the manifest |
    | `src/validation.py` | Checks the manifest and records, then creates score, weight and rating-gap fields |
    | `src/stats.py` | Shared outcome measures, BH adjustment and individual reply intervals |
    | `src/hypothesis_h1.py` | Weighted H1 estimation, bootstrap and null simulations, rating model and shared-player calculations |
    | `src/h2.py` and `src/hypothesis_h2.py` | Reply grouping, eligibility, score-spread and Pearson tests, intervals, corrections and selected shared-player checks |
    | `src/run_analysis.py` | Runs the analysis stages, sensitivity scenarios and output checks |
    | `src/plotting.py` and `src/reporting.py` | Generate the final graphs and research reports |
    | `analysis.ipynb` | Executes and explains the same offline analysis |
    | `results/`, `figures/` and `reports/` | Store numerical evidence, graph files and the original research record |
    | `tests/` | Checks statistical behavior, validation rules and output consistency |

    The saved input, fixed rules, seed **202503**, **10,000 repetitions** and recorded package versions support repeatable results. They do not remove statistical assumptions.

[Research questions](question.md) · [Detailed methods](../methodology/data.md) · [Output files](../reproducibility/outputs.md)
