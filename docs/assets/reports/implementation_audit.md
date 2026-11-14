# Implementation audit

## Baseline inspected (2026-11-13)

All source files, tests, notebook cells, requirements, README, VS Code settings, legacy documentation, manifest, tracked figures/tables and the historical notebook generator were inspected. There is no AGENTS.md. Existing data and legacy outputs are preserved.

- `fetch_games.py` implements streaming, deterministic ID hashing, rejection counts, sampling probabilities and a checksum manifest. Its existing offline tests cover CSV/Parquet agreement, truncation, sampling and flags. The `is_resignation` field is a heuristic (decisive Normal result without mate), not a verified termination reason.
- The March manifest declares 97,512,351 scanned games and 836,070 retained. The actual Parquet has 836,070 rows, dates 2025-03-01 through 2025-03-31, no duplicate IDs, and SHA-256 `e055e8f921b3b242188c0493d57acc8fe83a2200ee0223e6cb817dc5a627ffaa`. Record checks and full accounting are automated in `src/validation.py`.
- The dataset includes 571,572 games sampled at 1% and 264,498 at 10%; pooled unweighted scores do not target the eligible source-game population. March supports both H1 and immediate-reply H2. It is a sample, not all March games.
- `stats.py` has working score/variance and disjoint-family helpers. Empty/invalid inputs, resampling, multiplicity and weighting were not adequately handled. Family subtraction, estimates, contrasts and ranges were used in the old notebook; H2 functions existed but were not integrated.
- `h2.py` has a valid independent-game multinomial score-spread simulation and finite-simulation correction. It lacks multiplicity adjustment, robust count validation, sparse-cell status, complete coverage reporting and a full W/D/B distribution test. Score spread alone does not detect alternatives that only change draw rates.
- `explorer.py` now sends explicit dates and keys caches by query. The archived `data/raw/explorer_raw.csv` has 180 position aggregates but no `since`/`until`. Git history shows the explicit-date patch postdates the original collection. No response cache or collection sidecar exists locally. Its period cannot be verified; it is excluded from confirmatory analysis. Nested totals are checked only as an archive diagnostic.
- `analysis.ipynb` imports flat modules, loads missing `data/explorer_raw.csv`, can start network collection, and scrapes uncached Wikipedia. Existing results/figures concern the unverified Explorer source. The notebook needs to use package imports and the March pipeline offline.
- Existing `q1_score_by_band`, `q2_families_by_band`, `draw_rate_by_band` and LaTeX tables are exploratory archive artifacts. Their underlying aggregates can reproduce the plots but cannot validate a 2025 claim. New figures use distinct filenames.
- `wiki_scrape.py` parses Code/Moves tables and provides approximate ECO fallback labels. No local validated Wikipedia mapping/cache exists. PGN ECO/name fields can be described as supplied; full ECO reconciliation is optional and unnecessary for H2.
- `tests/mock_run.py` is obsolete: references missing `main.ipynb`, flat layout and an outdated API mock. It will become an offline pipeline smoke entry point.
- README claims a full-year target, Masters comparison and dashboard as intended work. None are implemented. The final scope is March 2025; those claims will be replaced with executed findings.
- The initial `python -m pytest -q` could not run because pytest was absent. A local `.venv` is being populated with declared dependencies; baseline results are recorded below after execution.

## Analysis decisions fixed before subgroup/reply analysis

Primary H1: all validated March blitz/rapid/classical games, all collected rating bands, inverse-probability ratio score. Alpha .05, one-sided, seed 202503, 10,000 replicates. H1 subgroup reporting requires N >= 200 and at least 20 decisive outcomes; smaller groups are descriptive/inconclusive. Benjamini–Hochberg correction covers eligible speed, band and speed-by-band tests together, excluding the single primary test. Near-equal means |Elo difference| <= 25; sensitivity bounds are 10, 50 and 100. A difference of 1 percentage point is used only as a transparent descriptive material-change flag.

H2: preserve Explorer floor 10,000; March floor 200 observed games per reply, band >= 1200 (existing study convention), at least two eligible replies. Alternatives use floors 100, 500, 1000 and all-band inclusion. Each test uses exactly one first-move/speed/band cell. BH is applied separately to the score-spread family and full-distribution family across all eligible primary cells. Figures of null distributions use the prespecified e4/blitz/1600 and d4/blitz/1600 cells. Reply extremes are descriptive, selected after observing scores; their CIs are marginal, not selection-adjusted.

Uncertainty: independent-game, stratified Poisson multiplier bootstrap with Bernoulli finite-population scaling for the weighted ratio; observed games, not weighted population totals, determine precision. Null simulations use fixed stratum sample sizes with draw-preserving multinomials; exact conditional binomial cross-checks apply only to unweighted/equal-weight estimates. Recurring-player sensitivity uses a dyadic sandwich covariance (shared player in either color), plus rating-adjusted score regression. These are assumptions/sensitivity analyses, not a causal design.

## Baseline verification

After installing dependencies in `.venv`, the unmodified baseline suite passed: **16 passed**. Full automated provenance checks (including all retained IDs meeting their hash threshold, rates matching arguments, per-cell counts, source URL/month and rejection accounting) passed. All 836,070 records passed additional cleaning: **0 exclusions** under every recorded rule. Only optional title fields are null; missing titles correctly mean untitled players.

## Completed implementation and verification

The offline March workflow now validates/cleans data, exports EDA, runs weighted H1 bootstrap/null/pooled-mean tests with exact raw cross-checks, fits an equal-rating score model, performs shared-player sensitivity, and integrates the existing H2 spread logic with full-distribution tests, coverage, marginal intervals and BH. An additional Pearson test was necessary because equal reply scores can mask different draw rates. A boundary test corrected the signed-rating categories so both -25 and +25 belong to the near-equal category.

The repaired 24-cell notebook executed all 10 code cells successfully. The final expanded suite passed **65 tests with 0 failures**. The full pipeline and real-data artifact smoke check passed; all ten requested figures plus the H1 interval plot exist in PNG/PDF. Reports and README are rendered from executed tables. Dataset/legacy files and historical figures are preserved. New figure names distinguish the validated March results from archived Explorer exploration. A checksum proves agreement with the local manifest, not an independent re-scan or cryptographic attestation of the original remote dump.

Primary result: weighted White score 51.776323% (95% CI 51.652618–51.898815%); H2 score spread rejects 14/35 and full distributions 15/35 after their separate corrections. Near-equal restriction leaves 1/28 H2 score rejections, and the >=40-ply H1 subset materially reduces the score. Both sensitivities are prominently reported rather than hidden. All optional source limitations are recorded in the final report and completion checklist.
