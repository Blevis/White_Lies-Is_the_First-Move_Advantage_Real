# WHITE LIES — Is the First-Move Advantage Real?

An empirical chess study and interactive research publication based on **836,070 sampled Lichess games played in March 2025**. The project combines an auditable Python analysis, an executed notebook, and a static MkDocs website with an aggregate-data explorer.

[Research documentation](docs/index.md) · [Full scientific report](reports/FINAL_RESEARCH_REPORT.md) · [Methodology](docs/methodology/statistics.md) · [Reproduction guide](docs/reproducibility/installation.md)

## Research website

The Material for MkDocs publication includes an editorial homepage, H1/H2 findings, a filterable dashboard, an explanatory opening board, eleven annotated scientific figures, and synchronized report and audit pages. Browser interactions read recorded aggregate outputs; they do not run new tests or publish game-level records.

**Deployment:** configured for GitHub Pages, but not yet published. On November 14, 2026, the repository API reported Pages disabled. The expected standard project address is `https://blevis.github.io/White_Lies-Is_the_First-Move_Advantage_Real/`; it is **not a verified live URL**. Enable **Settings → Pages → GitHub Actions**, then merge the implementation into `main`. The workflow obtains the canonical URL from GitHub's Pages configuration. See [website maintenance](docs/project/website.md) for deployment and customization details.

Preview locally with Python 3.11 or newer:

```bash
python3 -m venv .venv-docs
source .venv-docs/bin/activate
python -m pip install -r requirements-docs.txt
python -m mkdocs serve
```

On Windows PowerShell, create the environment with `py -3 -m venv .venv-docs` and activate it with `.\.venv-docs\Scripts\Activate.ps1`. Open the address printed by MkDocs, normally `http://127.0.0.1:8000/`.

Website dependencies are separate from the scientific requirements. The build hook copies final figures and reports and exports compact, source-hashed aggregate JSON. It never executes the analysis or notebook.

```bash
python scripts/build_docs_assets.py --check
python -m mkdocs build --strict
python scripts/check_site.py
```

Compiled `site/` output is ignored by Git and uploaded only as a deployment artifact.

## The finding

White scores **51.776%** (95% CI **51.653%–51.899%**) in the weighted eligible March 2025 Lichess population: **+1.776 percentage points** over 50%. One-sided Monte Carlo p=9.999e-05 (10,000-simulation resolution limit). Equal-rating standardization gives **51.886%** (dyadic CI 51.707%–52.064%).

Black's immediate reply is associated with score differences in **14/35 eligible cells** after BH correction; full W/D/B distributions differ in 15. H2 weakens markedly under near-equal-rating restrictions. These are **observational associations**, not causal claims or defense recommendations.

Read the [full research report](reports/FINAL_RESEARCH_REPORT.md), [short conclusion](reports/FINAL_CONCLUSION.md), [audit](reports/implementation_audit.md), and [verification checklist](reports/COMPLETION_CHECKLIST.md).

## Questions and outcome

- **H1:** H0 expected White score =0.50; one-sided H1 >0.50. Test the weighted overall population, then rating and speed groups with multiplicity correction.
- **H2:** Within first-move/speed/rating cells after 1.e4 or 1.d4, test equality of Black replies' W/D/B distributions and separately their score spread.

A win is 1, draw 0.5, loss 0. White score is **(W + D/2)/N**, different from White win probability. Primary analysis uses weights **1/sample_rate**; weighted totals are never treated as observed sample sizes.

## Verified data and scope

**March 1–31, 2025 only:** 836,070 sampled games from the [Lichess monthly rated-standard dump](https://database.lichess.org/), 97,512,351 source games scanned. All checksum, manifest, hash-selection, sampling-rate and record checks pass; 0 additional rows excluded. Includes blitz, rapid and classical; BOT titles, invalid ratings/results, other terminations and games below two plies were excluded by the collector. Resignations and legitimate short games are retained.

The sample is deterministic by game ID, with 1% base sampling and 10% classical/2200/2500-band overrides. Bands use mean opponent Elo. All collected bands enter H1; H2 uses bands >=1200 and >=200 observed games/reply. The archived Explorer CSV has unverified dates and is excluded. The legacy game CSV drops resignations and is excluded.

## Method and results

10,000-replicate sampling-aware Poisson multiplier bootstrap, draw-preserving multinomial null simulations, exact decisive-game binomial cross-checks where applicable, BH adjustment, equal-rating spline score regression and shared-player dyadic sensitivity. Prespecified choices are recorded in the audit. Independent-game and disjoint-player assumptions are explicit in the report.

| Group                      |       N | White score   | 95% CI          |   Above 50% (pp) |   Adjusted p | Interpretation           |
|:---------------------------|--------:|:--------------|:----------------|-----------------:|-------------:|:-------------------------|
| Overall (primary weighted) | 836,070 | 51.776%       | 51.653%–51.899% |            1.776 |    9.999e-05 | Score above 50% detected |
| blitz                      | 623,882 | 51.776%       | 51.637%–51.915% |            1.776 |    0.0001267 | Score above 50% detected |
| classical                  |  54,562 | 51.793%       | 51.402%–52.182% |            1.793 |    0.0001267 | Score above 50% detected |
| rapid                      | 157,626 | 51.776%       | 51.523%–52.024% |            1.776 |    0.0001267 | Score above 50% detected |

Near-equal-rating score: **51.819%** (CI 51.637%–52.004%, n=327,230). Band scores have no monotonic trend. Sensitivities preserve H1's direction, but the >=40-ply subset reduces the score to **50.769%** (CI 50.637%–50.903%), a **−1.007 pp** change that also changes the population under study. H2's median reply-score range is 6.24 pp; ranges are selected extremes with uncertainty, not objective opening values. Near-equal-rating H2 retains only **1/28 score-spread rejections**.

![White score and confidence intervals](figures/h1_score_confidence_intervals.png)

![Black replies after e4, band 1600](figures/fig07_replies_e4.png)

## Reproduce offline

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m src.run_analysis
python -m jupyter nbconvert --to notebook --execute --inplace analysis.ipynb --ExecutePreprocessor.timeout=600
python -m pytest -q
python tests/mock_run.py
```

The pipeline validates inputs before analysis, performs EDA/H1/H2/robustness, writes numerical tables and reports, exports 11 scientific figures in PNG/PDF, and checks outputs. It makes no network calls or large downloads. The retained `data/games_2025-03.parquet` and adjacent manifest must be present; the complete monthly dump is not included or downloaded automatically. The notebook runs from the repository root using `src` imports. Seed: **202503**. Executed package versions: [software_versions.json](results/software_versions.json).

For an isolated reproduction that preserves the recorded outputs and publication README, run:

```bash
python -m src.run_analysis --output-root /path/to/separate-output
```

The original pipeline's default report writer regenerates the research README, and executing the notebook reruns that pipeline. Review diffs after either operation. The scientific pipeline remains unchanged. [Running the analysis](docs/reproducibility/running.md) and [validation](docs/reproducibility/validation.md) explain the commands and their scope.

## Repository guide

| Location | Content |
|---|---|
| `analysis.ipynb` | Executed scientific notebook with interpretation |
| `src/validation.py` | Fail-closed provenance and counted cleaning |
| `src/stats.py`, `hypothesis_h1.py` | Reusable scores, bootstrap/null tests, weighting and adjustment |
| `src/h2.py`, `hypothesis_h2.py` | Existing spread test plus March grouping, coverage, full-distribution tests and BH |
| `src/run_analysis.py`, `plotting.py`, `reporting.py` | Offline execution, figures and data-driven documents |
| `src/fetch_games.py`, `explorer.py`, `wiki_scrape.py` | Preserved optional collectors and metadata helpers |
| `results/` | Provenance, EDA, H1/H2, sensitivity, model and source-availability tables |
| `figures/fig01_*` through `fig10_*` | Final March figures, plus H1 interval plot; each PNG and PDF |
| `reports/` | Audit, full report, short conclusion and verification |
| `tests/` | Analytic, synthetic calibration/power, provenance and artifact checks |
| `mkdocs.yml`, `requirements-docs.txt` | Website configuration and pinned documentation dependencies |
| `docs/` | Homepage, research, explorer, methodology, reproducibility and project pages |
| `docs/assets/` | Local design assets, compact aggregate data and copied final figures/reports |
| `overrides/` | Modular Material template customizations |
| `scripts/build_docs_assets.py`, `scripts/docs_hook.py` | Deterministic website synchronization without running research |
| `.github/workflows/docs.yml` | Documentation validation and official GitHub Pages deployment |
| `website/` | Preserved earlier Streamlit interface; MkDocs is the primary publication |

Old `q1_*`, `q2_*`, `draw_rate_by_band.*` and LaTeX artifacts are retained exploratory Explorer outputs; their dates are unverified. They do not support the March conclusions. `original_project/build_notebook.py` is an archived historical generator and must not replace the repaired notebook.

## Limits and optional future work

The study covers one site/month with selected rated game types. Ratings and opening choices are observational; repeated players limit independent-game inference. Near-equal H2 has less evidence, threshold decisions change, and high-rating classical cells are sparse. Explorer source alignment and full ECO mapping remain unverified. Full-year collection and Masters analysis remain optional future research and have not been implemented. The static dashboard presents the existing March study; it does not extend its data coverage. Read the [limitations](docs/research/limitations.md) alongside the findings.

## Contributing

Use repository issues or pull requests for reproducible problems and focused improvements. Statistical changes should identify the affected source table or method, regenerate evidence through the scientific pipeline and include validation. Website changes should preserve score definitions, observed sample sizes, weighting labels and uncertainty. Edit authoritative reports in `reports/` and regenerate website copies instead of maintaining separate scientific narratives.

The primary data are attributed to [Lichess](https://database.lichess.org/). Methodological references and source distinctions appear in [research sources](docs/project/sources.md). No institutional affiliation, peer-review status or endorsement is implied.
