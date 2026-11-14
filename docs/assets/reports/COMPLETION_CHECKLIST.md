# Completion and verification checklist

**Status: COMPLETE for the explicitly scoped March 2025 observational study.** Verified locally on 2026-11-13. No essential implementation or data blocker remains. Optional full-year/Explorer/ECO/dashboard work is not represented as completed.

- [x] Existing repository audited; baseline tests passed (16/16).
- [x] Actual study period fixed at March 1–31, 2025.
- [x] All 836,070 retained rows match the manifest and SHA-256.
- [x] Completion, source month/URL, paths, counts, rates, hash selection, cell counts and rejection accounting verified.
- [x] Record cleaning and all exclusion rules reported: zero additional exclusions.
- [x] IPW pooling, observed sample size, finite-population scaling and variable-denominator bootstrap implemented.
- [x] EDA includes outcomes, draws, rating gaps, lengths, openings, replies and sample coverage.
- [x] H1 includes 10,000-replicate intervals/nulls, exact equal-weight cross-checks, a pooled-mean design Wald check, BH, near-equal ratings and score regression.
- [x] H2 includes disjoint reply grouping, fixed eligibility rules, coverage, score spread, full W/D/B tests, marginal CIs and separate BH families.
- [x] Rating/threshold/band/control/weight/forfeit/short-game sensitivity checks documented.
- [x] Shared-player dyadic sensitivities computed for H1, the adjusted model and two prespecified H2 cells.
- [x] Ten required figures plus the H1 interval plot exported to both PNG and PDF (22 new figure files).
- [x] Numerical result tables, dataset summary, software versions and source-comparison unavailability record exported.
- [x] Full research report, 376-word conclusion and chess-themed README generated from computed results.
- [x] Repaired notebook executed successfully: 24 cells, all 10 code cells executed, zero error outputs.
- [x] Complete final test suite: **65 passed, 0 failed** (`python -m pytest -q`).
- [x] Statistical tests cover null calibration, planted score/reply effects, sparse replies, sampling imbalance, interval scaling/coverage, draw-only differences, adjustment recovery and dyadic covariance.
- [x] Real-data artifact smoke check passed (`python tests/mock_run.py`).
- [x] Final offline pipeline passed (`python -m src.run_analysis`); output verification succeeded.
- [x] CSV/JSON consistency checked, including weighted recombination of speed/band/cell estimates, reply partitions, eligibility and score intervals.
- [x] `git diff --check` passed; data and legacy artifacts remain unchanged.

## Executed commands

```bash
.venv/bin/python -m pytest -q
.venv/bin/python -m src.run_analysis
.venv/bin/python -m jupyter nbconvert --to notebook --execute --inplace analysis.ipynb --ExecutePreprocessor.timeout=600
.venv/bin/python tests/mock_run.py
git diff --check
```

The notebook also executes the offline analysis pipeline. Numerical findings reproduce with seed 202503 and 10,000 replicates. Original data checksum: `e055e8f921b3b242188c0493d57acc8fe83a2200ee0223e6cb817dc5a627ffaa`.

## Evidence and limits

Primary IPW White score: **51.776323%**, percentile 95% CI **51.652618–51.898815%**. Score-spread H2 rejects **14/35** cells; full-distribution H2 rejects **15/35**, after their separate BH corrections. Tables and reports carry the actual sample sizes, uncertainty and assumptions.

The archived Explorer CSV has unverified dates and no authenticating query cache/sidecar; a comparable numeric source check is unavailable. No API token is available. Further months, Masters comparison, a full validated ECO join and a dashboard remain optional future work. Original source-stream scan counts are authenticated only by the local collection manifest and accounting, not by rescanning the 31.8 GB compressed archive.

Scientific limitations remain: observational opening/color selection, imperfect ratings, assumptions about sampling and disjoint-player dependence, mostly independent-game H2 simulations, sparse high-rated classical cells, multiplicity dependence assumptions, marginal selected-reply intervals, weaker H2 under near-equal restriction and material H1 magnitude sensitivity to the 40-ply restriction. These delimit the completed study's conclusions; they are not hidden unfinished analyses.
