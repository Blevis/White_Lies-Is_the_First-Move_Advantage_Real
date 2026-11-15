# White Lies website implementation

Completed and reviewed locally on **November 15, 2026**. The publication uses **MkDocs 1.6.1 and Material for MkDocs 9.8.1**. It preserves the March research and publishes precomputed aggregate evidence.

## Delivered experience

- An original editorial homepage with local Fraunces/Manrope typography, ivory/charcoal/gold colors, dark and light palettes, an original SVG chess composition, methodological metric cards, an accurate H1 confidence-interval graphic, H2 explanations, real-data chart preview, research timeline and visible limitations.
- Twenty-six navigable content pages, plus the generated 404 page: research, methodology, reproducibility, project reference, full report, interactive explorer, opening analysis and an eleven-figure gallery.
- Six explorer views: selected H1 score and interval, speed comparison, rating-band comparison, White/Draw/Black shares, H2 replies, and reported sensitivity estimates. Filtering and table sorting select existing records; the browser performs no inferential tests.
- A correctly oriented explanatory board with initial pieces, 1.e4 / 1.d4, observed legal pawn and knight replies, highlighted squares, reset/replay, and an accessible position description.
- Material navigation, search/highlighting, code copying, tabs, admonitions, table of contents, repository/source links and accessible theme controls. Formula rendering is local and loaded only on pages containing mathematics.
- Deterministic source synchronization, export validation, source SHA-256 hashes, original report downloads and final PNG/PDF figures. The aggregate file is approximately 256 KB and contains no game records or player identifiers.
- An official GitHub Actions Pages workflow with strict validation, a static artifact, a dependent deployment job, minimal permissions, and concurrency protection.

## Scientific integrity

The source values are unchanged: **836,070 sampled games**, **97,512,351 source games scanned**, **51.776% primary weighted White score**, **51.653%–51.899% primary 95% interval**, **+1.776 pp**, and separate H2 results of **14/35 score-spread** and **15/35 full-distribution** rejections. The Monte Carlo p-value is explicitly a 10,000-simulation resolution floor.

The interface distinguishes score from win probability, raw sample composition from weighting, and the equal-rating regression from primary inference. Raw H1 subgroup intervals are unavailable and cannot be selected. Sparse H1 groups are descriptive; unavailable H2 cells explain their eligibility restriction. Selected-reply views retain the whole-cell omnibus tests. Intervals are exported marginal intervals, not selection-adjusted rankings.

The ≥40-ply sensitivity is prominent: weighted score **50.769%**, materially below the primary magnitude, with a changed target population. Near-equal-rating H2 leaves **1/28** score-spread rejections. Observational selection, repeated players, rating limitations and one-month scope remain visible.

All **85 pre-existing files** tracked under `src/`, `data/`, `results/`, `figures/`, `reports/`, `tests/`, `website/`, plus the notebook and scientific requirements, were compared byte for byte against pre-website commit `d77ebfa`: **no changes**. New publication files are additions; README and `.gitignore` are intentionally updated.

The full report and research audit are synchronized rather than independently rewritten. Original report downloads retain their exact bytes. Historical Explorer figures are preserved in the repository and excluded from the publication gallery.

## Validation

Recorded commands:

```bash
# Independent documentation environment; no scientific dependencies required
python3 -m venv .venv-docs
.venv-docs/bin/python -m pip install -r requirements-docs.txt
.venv-docs/bin/python scripts/build_docs_assets.py --check
.venv-docs/bin/python -m mkdocs build --strict
.venv-docs/bin/python scripts/check_site.py

# Existing scientific environment
.venv/bin/python -m pytest -q
.venv/bin/python tests/mock_run.py
git diff --check
```

The clean documentation installation and strict build pass. The static checker validates **27 HTML pages, 5 CSS files and 1,935 local references**, including anchors, figure/PDF links, local CSS assets, raw Markdown downloads and publication-data restrictions. It checks all four metric-card values individually against exported summaries; a deliberately altered card in a temporary build is rejected.

The full suite passes: **70 tests** (65 existing research tests plus 5 publication tests). The frozen-data artifact smoke check passes. Website builds do not run the expensive analysis, execute the notebook, or overwrite scientific outputs.

Optional browser verification is separate from production dependencies:

```bash
python -m pip install playwright==1.58.0
python -m playwright install --with-deps chromium
python scripts/smoke_site.py

# Optional automated accessibility checks, using a local copy of axe-core 4.10.3
python scripts/smoke_site.py --axe-file /path/to/axe.min.js
```

In this environment, Chromium was already cached but three system libraries were absent. Their distribution packages were unpacked under `/tmp/white-lies-browser-libs`, without changing system packages. The executed browser command used:

```bash
LD_LIBRARY_PATH=/tmp/white-lies-browser-libs/unpacked/usr/lib/x86_64-linux-gnu \
  .venv/bin/python scripts/smoke_site.py --axe-file /tmp/white-lies-axe.min.js
```

**Browser result: PASS.** Results and screenshots are recorded in ignored `artifacts/browser/`. Automated checks cover a repository subpath, theme switching, search, weighted/raw filters, unavailable subgroup estimates, sparse H1 groups, H2 selection, pawn/knight moves, reset/replay, table search/sort, keyboard focus, math, reduced motion, request failure/retry, JavaScript exceptions and local HTTP failures. Layout checks cover **360, 390, 768, 1024 and 1440 px** on the homepage, explorer and full report.

Independent component review also checked all **54** H2 first-move/speed/band selections against the exported tested-reply counts and exercised each eligible reply in the default cell. The four headline cards and homepage interval coordinates were independently checked against the numerical sources.

**Accessibility result: all 12 scans passed, with zero reported violations.** Automated accessibility checks target WCAG A/AA rules on the homepage, explorer, report and statistical-methods page in both themes, plus the homepage and explorer at 390 px in both themes. Practical checks do not constitute formal accessibility certification or exhaustive screen-reader coverage.

## Local use

From the repository root:

```bash
source .venv-docs/bin/activate
python -m mkdocs serve
```

Open the address printed by MkDocs, normally `http://127.0.0.1:8000/`.

Windows PowerShell:

```powershell
py -3 -m venv .venv-docs
.\.venv-docs\Scripts\Activate.ps1
python -m pip install -r requirements-docs.txt
python -m mkdocs serve
```

A static preview can use `python -m http.server --directory site`. Do not open the explorer with `file://`; browsers restrict its JSON fetch in that mode.

## Deployment record and remaining setting

**Verified live:** [White Lies research publication](https://blevis.github.io/White_Lies-Is_the_First-Move_Advantage_Real/).

On November 15, 2026, the Pages API returned that URL, `status: built` and HTTPS enforcement. A direct HTTPS fetch returned the custom MkDocs homepage. The [successful main-branch workflow](https://github.com/Blevis/White_Lies-Is_the_First-Move_Advantage_Real/actions/runs/43626779084) contains successful `build` and `deploy` jobs for `da103f682cb76b3778f098df303fae4f732c3ffd`. The preceding [pull-request validation](https://github.com/Blevis/White_Lies-Is_the_First-Move_Advantage_Real/actions/runs/43626771367) also succeeded.

**One manual setting remains:** the API reports `build_type: legacy`, using `main` at `/`. Select **Settings → Pages → Build and deployment → Source → GitHub Actions** to prevent branch-based publishing from competing with the custom workflow. The attempted `PUT /repos/Blevis/White_Lies-Is_the_First-Move_Advantage_Real/pages` with `build_type=workflow` returned **HTTP 404** using the available credential. No setting change was made.

`mkdocs.yml` now defaults to the verified URL. Deployments override it with the actual Pages `base_url` from `actions/configure-pages`; the same mechanism accommodates a custom domain. Production canonical and social metadata were also checked in a separate build with a test URL and subpath.

The implementation was committed and merged during the session. Final refinements made after the published commit remain local until committed and merged: the verified canonical-URL default, current deployment notes, exact metric-card validation, repaired browser-check selectors with optional accessibility checks, the tablet hero overflow correction, and this report. No raw games or compiled site files are committed. GitHub Actions has been validated by the successful remote run; this report does not claim that subsequent local refinements are already published.

## Maintenance limits

- The website is a frozen March 2025 publication, not a live database or chess engine.
- The original analysis pipeline regenerates its research README on default execution. Use `--output-root /path/to/separate-output` for isolated reproduction, and review diffs after executing the notebook. This existing behavior is documented, not changed silently.
- Browser verification uses Chromium. Safari, Firefox, physical devices and a full manual assistive-technology audit were not exercised.
- Fonts and KaTeX retain their upstream licenses. No license, affiliation, author identity or endorsement was invented for the research project.
- Material is kept as explicitly requested. The customizations are confined to Markdown, CSS/JS, small template overrides and a standalone exporter, limiting framework coupling.

## Important files

| File | Purpose |
|---|---|
| `mkdocs.yml` | Framework configuration, navigation, extensions, metadata and build hook |
| `docs/index.md` | Complete editorial homepage |
| `docs/explore/index.md`, `docs/explore/openings.md` | Interactive entry points |
| `docs/assets/js/explorer.js` | Precomputed analytics and explanatory board |
| `docs/assets/css/site.css`, `docs/assets/css/explorer.css` | Publication and component styling |
| `scripts/build_docs_assets.py`, `scripts/docs_hook.py` | Deterministic synchronization and validation |
| `scripts/check_site.py`, `scripts/smoke_site.py` | Static and browser verification |
| `.github/workflows/docs.yml` | Validation and official Pages deployment |
| `README.md` | Research/developer entry point and live-site status |
| `docs/project/website.md` | Build, maintenance and deployment guide |

## Complete publication file structure

The tree below lists all added publication files. `README.md` and `.gitignore` are modified existing files. Generated `site/`, local environments, caches and verification screenshots are intentionally excluded.

```text
├── .github/
│   └── workflows/
│       └── docs.yml
├── docs/
│   ├── assets/
│   │   ├── css/
│   │   │   ├── explorer.css
│   │   │   └── site.css
│   │   ├── data/
│   │   │   └── research.json
│   │   ├── figures/
│   │   │   ├── fig01_game_outcomes.pdf
│   │   │   ├── fig01_game_outcomes.png
│   │   │   ├── fig02_score_by_band.pdf
│   │   │   ├── fig02_score_by_band.png
│   │   │   ├── fig03_score_by_speed.pdf
│   │   │   ├── fig03_score_by_speed.png
│   │   │   ├── fig04_draw_rate_by_band.pdf
│   │   │   ├── fig04_draw_rate_by_band.png
│   │   │   ├── fig05_rating_imbalance.pdf
│   │   │   ├── fig05_rating_imbalance.png
│   │   │   ├── fig06_sample_coverage.pdf
│   │   │   ├── fig06_sample_coverage.png
│   │   │   ├── fig07_replies_e4.pdf
│   │   │   ├── fig07_replies_e4.png
│   │   │   ├── fig08_replies_d4.pdf
│   │   │   ├── fig08_replies_d4.png
│   │   │   ├── fig09_reply_effect_heatmap.pdf
│   │   │   ├── fig09_reply_effect_heatmap.png
│   │   │   ├── fig10_h2_null_spread.pdf
│   │   │   ├── fig10_h2_null_spread.png
│   │   │   ├── h1_score_confidence_intervals.pdf
│   │   │   └── h1_score_confidence_intervals.png
│   │   ├── fonts/
│   │   │   ├── fraunces-OFL.txt
│   │   │   ├── fraunces-latin.woff2
│   │   │   ├── manrope-OFL.txt
│   │   │   └── manrope-latin.woff2
│   │   ├── images/
│   │   │   ├── hero-chess.svg
│   │   │   ├── mark.svg
│   │   │   └── social-card.png
│   │   ├── js/
│   │   │   ├── explorer.js
│   │   │   └── site.js
│   │   ├── reports/
│   │   │   ├── COMPLETION_CHECKLIST.md
│   │   │   ├── FINAL_CONCLUSION.md
│   │   │   ├── FINAL_RESEARCH_REPORT.md
│   │   │   └── implementation_audit.md
│   │   └── vendor/
│   │       └── katex/
│   │           ├── LICENSE
│   │           ├── fonts/
│   │           │   ├── KaTeX_AMS-Regular.woff2
│   │           │   ├── KaTeX_Caligraphic-Bold.woff2
│   │           │   ├── KaTeX_Caligraphic-Regular.woff2
│   │           │   ├── KaTeX_Fraktur-Bold.woff2
│   │           │   ├── KaTeX_Fraktur-Regular.woff2
│   │           │   ├── KaTeX_Main-Bold.woff2
│   │           │   ├── KaTeX_Main-BoldItalic.woff2
│   │           │   ├── KaTeX_Main-Italic.woff2
│   │           │   ├── KaTeX_Main-Regular.woff2
│   │           │   ├── KaTeX_Math-BoldItalic.woff2
│   │           │   ├── KaTeX_Math-Italic.woff2
│   │           │   ├── KaTeX_SansSerif-Bold.woff2
│   │           │   ├── KaTeX_SansSerif-Italic.woff2
│   │           │   ├── KaTeX_SansSerif-Regular.woff2
│   │           │   ├── KaTeX_Script-Regular.woff2
│   │           │   ├── KaTeX_Size1-Regular.woff2
│   │           │   ├── KaTeX_Size2-Regular.woff2
│   │           │   ├── KaTeX_Size3-Regular.woff2
│   │           │   ├── KaTeX_Size4-Regular.woff2
│   │           │   └── KaTeX_Typewriter-Regular.woff2
│   │           ├── katex.min.css
│   │           └── katex.min.js
│   ├── explore/
│   │   ├── figures.md
│   │   ├── index.md
│   │   └── openings.md
│   ├── index.md
│   ├── methodology/
│   │   ├── data.md
│   │   ├── ratings.md
│   │   ├── robustness.md
│   │   ├── sampling.md
│   │   ├── statistics.md
│   │   └── uncertainty.md
│   ├── project/
│   │   ├── about.md
│   │   ├── audit.md
│   │   ├── sources.md
│   │   ├── structure.md
│   │   └── website.md
│   ├── reproducibility/
│   │   ├── installation.md
│   │   ├── notebook.md
│   │   ├── outputs.md
│   │   ├── running.md
│   │   └── validation.md
│   └── research/
│       ├── findings.md
│       ├── h1.md
│       ├── h2.md
│       ├── limitations.md
│       ├── question.md
│       └── report.md
├── mkdocs.yml
├── overrides/
│   ├── home.html
│   ├── main.html
│   └── partials/
│       └── source.html
├── reports/
│   └── WEBSITE_IMPLEMENTATION.md
├── requirements-docs.txt
├── scripts/
│   ├── build_docs_assets.py
│   ├── check_site.py
│   ├── docs_hook.py
│   └── smoke_site.py
└── tests/
    └── test_docs_assets.py
```
