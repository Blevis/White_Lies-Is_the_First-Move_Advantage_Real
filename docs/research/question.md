---
title: The research question
description: Two empirical questions about White's scoring advantage and Black's immediate replies in March 2025 Lichess games.
---

# Does the first move really matter?

Chess gives White the first move. That simple asymmetry makes a compelling statistical question: in recorded play, does White receive more than half the available points?

The study follows **836,070 sampled rated-standard Lichess games played March 1–31, 2025**. It investigates scoring patterns across blitz, rapid and classical games, with a second analysis of Black's immediate replies to `1.e4` and `1.d4`.

## Two questions, two levels of evidence

| Question | Statistical target | What the answer describes |
| --- | --- | --- |
| **H1 — the first move** | Is expected White score greater than 0.50? | A weighted scoring association in the eligible March population |
| **H2 — the first reply** | Within a first-move, speed and rating cell, do eligible replies have equal outcome distributions? | Associations between chosen replies and recorded outcomes |

H2 also tests reply-score spread separately. Two distributions can have the same expected score while differing in how often games end in a draw.

## Score is more than winning

A White win earns one point, a draw earns half a point and a Black win earns zero points for White:

$$
S = \frac{W + D/2}{W+D+B}.
$$

This is a **score**, not a win probability. The primary weighted estimate is 51.776% even though White's weighted outright-win share is 49.533%. Draws account for the difference.

## What would a causal answer require?

Recorded colors, opponents, time controls and opening replies do not constitute a randomized experiment. Ratings imperfectly describe strength, recurring players connect observations, and different players choose different defenses. A measured association cannot establish what would happen if the same players were assigned a different color or reply under otherwise identical conditions.

!!! note "The scope of the claim"
    These results describe eligible Lichess games in one month. They do not resolve the theoretical value of perfect chess, identify the best defense, or establish a universal effect of moving first.

Continue with [H1: the scoring advantage](h1.md), [H2: opening replies](h2.md), or the [authoritative full report](report.md).
