---
title: Sampling and exclusions
description: Deterministic game-ID sampling, unequal inclusion rates, eligibility rules and observed sample accounting.
---

# Who enters the analysis?

Eligible records are rated standard blitz, rapid or classical games with numeric player ratings, a valid result, a Normal or Time forfeit termination, no BOT title and at least two plies. A ply is one player's move. Legitimate resignations and short games are retained.

## Deterministic sampling

The collector hashes each game ID with MD5 and compares the resulting fraction to the declared inclusion probability. This makes selection reproducible by ID. For statistical inference, that rule is approximated as pseudo-random Bernoulli sampling.

The base inclusion probability is **1%**. Classical games and rating bands with lower bounds **2200 or 2500** use **10%**. These are overrides, not compounded sampling probabilities. The sample contains **571,572 games at 1%** and **264,498 at 10%**.

An unweighted pooled score therefore reflects the oversampled composition. The primary estimate uses weights of 100 or 10 respectively to estimate the eligible source-game mixture.

## Rating bands

Bands use the floor of the opponents' mean Elo, with lower bounds **0, 1000, 1200, 1400, 1600, 1800, 2000, 2200 and 2500**. The first means below 1000; the last means 2500+. The 2200 band extends through 2499. These are Lichess ratings for the relevant speed, not FIDE strength categories.

## Source accounting

| Sequential rejection rule | Rejected games |
| --- | ---: |
| Unsupported speed | 37,351,463 |
| Invalid rating | 0 |
| Invalid result | 1,310 |
| Unsupported termination | 188,228 |
| BOT title | 162,871 |
| Fewer than two plies | 210 |

Another **58,972,199** games were counted as not sampled, leaving 836,070 retained. The minimum-plies rule is checked after hash selection, so its count concerns sampled candidates. These sequential categories balance the manifest's scanned total; they are not independent counts of every possible violation.

## Analysis eligibility is a separate layer

H1 includes all collected bands, with subgroup tests requiring at least 200 games and 20 decisive outcomes. H2 restricts the primary analysis to bands at least 1200 and replies with at least 200 games, requiring two such replies per cell. Insufficient groups remain visible as unavailable or descriptive results.

Source: [full report, dataset and methodology](../research/report.md), `results/cleaning_ledger.csv`, and the collection manifest. See [statistical methods](statistics.md) for weighting and test families.
