---
title: 1. Questions and concepts
description: Two chess questions, one sample, and a simple way to measure the result.
---

# 1. Does moving first help?

We studied **836,070 Lichess games from March 2025** to answer two questions:

- **H1:** Does White earn more than half the points?
- **H2:** After `1.e4` or `1.d4`, are outcomes different after different replies by Black?

## Score, win rate and draw rate

A win earns **1 point**, a draw **½**, and a loss **0**.

$$
\text{White score}=\frac{\text{White wins}+\tfrac12\text{draws}}{\text{all games}}.
$$

For example: **48 wins + 8 draws in 100 games = 52% score, but 48% win rate.**

**Score includes draws. Win rate counts wins only.**

??? info "Outcome formulas"
    Let $W,D,B$ count White wins, draws and Black wins, with $N=W+D+B$.

    $$
    S=\frac{W+D/2}{N}, \qquad
    P(W)=\frac{W}{N}, \qquad
    P(D)=\frac{D}{N}, \qquad
    P(B)=\frac{B}{N}.
    $$

    Excluding draws gives the decisive-game win rate:

    $$
    P(W\mid \text{decisive})=\frac{W}{W+B}.
    $$

    An empty group has no score. An all-draw group scores 50% but has no decisive-game win rate. Undefined values remain missing.

## Three terms to know

| Term | Meaning |
| --- | --- |
| **Rating** | An estimate of player strength |
| **Time control** | Game speed: blitz, rapid or classical |
| **Ply** | One player's move; 20 plies = 10 moves by each side |

## What the study can tell us

The games reveal **patterns in real play**. They do not prove cause and effect: players differ in strength and choose their openings.

The scope is **one month, one platform and three rated game speeds**.

??? info "The hypotheses and source"
    Lichess publishes monthly archives with results, ratings and moves. We use those records to test a familiar claim about White's advantage.

    For H1, the null is equal scoring; the alternative is a score above 50%:

    $$
    H_0: E[Y]=0.50, \qquad H_1: E[Y]>0.50.
    $$

    The planned test is one-sided at a 0.05 threshold. For H2, the null says all eligible replies within one first-move, speed and rating group share the same win/draw/loss probabilities.

    The [study reference](reference.md) provides the glossary, graphs and formulas. [Detailed methods](../methodology/data.md) gives the full technical explanation.

**Next: [2. Collect and prepare the data →](approach.md)**
