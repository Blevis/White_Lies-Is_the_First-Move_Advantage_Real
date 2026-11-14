---
title: Limitations and scope
description: Observational selection, repeated players, sparse opening cells and sample restrictions delimit the study's conclusions.
---

# The boundaries of the evidence

Scientific transparency includes the assumptions under which an estimate is useful. These limitations accompany the findings, rather than describe optional qualifications to read later.

## One platform, one month, selected games

The study covers rated-standard Lichess games played March 1–31, 2025, restricted to blitz, rapid and classical and the recorded eligibility rules. **836,070 is a deterministic sample**, not the complete March population. The **97,512,351 scanned games** include rejected and unsampled games; they are not the analyzed sample size.

The results do not establish full-year, over-the-board, elite or theoretical perfect-play outcomes.

## Selection and measured strength

Colors, opponents and defenses are observed. Ratings have measurement error and do not capture latent player strength completely. Mean-rating bands can contain unequal opponents. Standardization uses a shared rating-difference curve across speed-band cells and does not establish causal identification.

## Dependence and sampling assumptions

Hash selection is treated as pseudo-random Bernoulli sampling. The estimated population composition and bootstrap uncertainty depend on that approximation. A matching local checksum proves agreement with the local manifest; it is not an independent rescan or authentication of the original remote dump.

Repeated players connect observations. Dyadic sensitivity allows covariance for games sharing a player, while assuming independence of disjoint-player games. It does not capture every temporal, tournament or network dependency. Most H2 simulations retain independent-game assumptions. Benjamini–Hochberg guarantees depend on the usual dependence conditions.

## Sparse groups and selected comparisons

The 2500+ classical cell contains only one sampled game. An unavailable test is **inconclusive**, not evidence of equal outcomes. Reply intervals are marginal and selected extremes have additional uncertainty. H2 evidence weakens substantially when near-equal-rating games are selected.

## Restrictions change the population

Requiring at least 40 plies reduces White's score from 51.776% to **50.769%**. This removes legitimate short outcomes and conditions on a post-opening variable. Excluding time forfeits also changes the population. The sensitivity checks support a positive direction more consistently than a fixed magnitude.

## Unverified historical sources

Archived Opening Explorer aggregates have no authenticatable query-period sidecar or cached responses. Their dates and rating-bucket alignment cannot be verified, so they are excluded from the final March evidence. No validated full ECO mapping is available; supplied PGN opening labels remain descriptive.

Sources: [full report, limitations](report.md#8-limitations), [dataset provenance](../methodology/data.md), [research audit](../project/audit.md).
