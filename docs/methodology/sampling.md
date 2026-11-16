---
title: Sampling and exclusions
description: Which games were eligible, how games were selected, and why the analysis uses weights.
---

# How games entered the sample

The collector kept a repeatable sample of eligible games. Some less common groups were sampled more often, so the main analysis uses weights to account for that difference.

## Which games were eligible?

Games needed to be rated standard **blitz, rapid or classical**, with numeric ratings for both players and a valid result. They also needed a recorded ending of **Normal** or **Time forfeit**, no BOT-titled player, and at least **two plies**. A ply is one individual player's move.

Valid short games and resignations were kept. The resignation flag is an estimate from the game record and was not used to exclude games.

## How were games selected?

Each game ID was converted to a number using a hash. A game was selected if that number fell below its group's sampling threshold. The same ID and rule always produce the same selection.

| Game group | Sampling rate | Weight per sampled game |
| --- | ---: | ---: |
| Most eligible games | 1% | 100 |
| Classical games, or rating bands starting at 2200 or 2500 | 10% | 10 |

The higher rate applies once, even if a game meets both conditions. The sample contains **571,572 games selected at 1%** and **264,498 selected at 10%**.

Without weights, the combined result gives extra influence to the groups sampled more often. Weighting estimates the mix of eligible games in the original archive. For the statistical calculations, hash selection is treated as approximately random sampling.

## How were ratings grouped?

Bands use the average of the two players' Lichess ratings, rounded down. Their lower bounds are **0, 1000, 1200, 1400, 1600, 1800, 2000, 2200 and 2500**.

The first band means below 1000; the last means 2500 or above. The 2200 band covers 2200–2499. These are Lichess ratings for the relevant game speed, not FIDE rating categories.

## Which sampled groups could be tested?

- **White-score analysis (H1):** all collected rating bands are included. Subgroup tests need at least 200 games and 20 games with a winner.
- **Reply analysis (H2):** main tests use rating bands starting at 1200. Each reply needs 200 games, and each comparison group needs at least two eligible replies.

Groups with too little data are marked as unavailable or shown only as descriptions. Missing tests do not show that outcomes are equal.

??? info "Full source accounting"
    | Rejection rule, applied in order | Rejected games |
    | --- | ---: |
    | Unsupported speed | 37,351,463 |
    | Invalid rating | 0 |
    | Invalid result | 1,310 |
    | Unsupported ending | 188,228 |
    | BOT title | 162,871 |
    | Fewer than two plies | 210 |

    Another **58,972,199** games were not selected by sampling, leaving **836,070** retained games. The minimum-length rule was checked after hash selection, so that count concerns selected candidates. Each rejected game is counted under the first rule that excluded it.

See [scores, weights and tests](statistics.md) for the calculations, or the [full report](../research/report.md#3-dataset) for the recorded dataset details.
