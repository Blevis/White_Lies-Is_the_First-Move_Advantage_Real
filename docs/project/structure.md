---
title: Repository structure
description: How the scientific pipeline, frozen outputs, documentation and static website implementation fit together.
---

# A research repository, with a reading layer

The scientific inputs, analysis and generated evidence retain their existing locations. MkDocs adds a static publication and explorer over those artifacts.

```text
White_Lies-Is_the_First-Move_Advantage_Real/
├── analysis.ipynb              # Executed research notebook
├── data/                       # Retained sample, manifest, legacy inputs
├── src/                        # Collection, validation, statistics, reporting
├── results/                    # Authoritative aggregate CSV / JSON outputs
├── figures/                    # Final figures and preserved historical figures
├── reports/                    # Full report, conclusion, audit, checklist
├── tests/                      # Scientific and artifact checks
├── docs/
│   ├── index.md                # Research landing page
│   ├── research/               # Questions, results, limits, synced full report
│   ├── explore/                # Dashboard, opening board and figure gallery
│   ├── methodology/            # Data, sampling, uncertainty and sensitivity
│   ├── reproducibility/        # Installation, commands and validation
│   ├── project/                # Source references, audit and project context
│   └── assets/                 # CSS, JavaScript, aggregate data and figures
├── overrides/                  # Material template customizations
├── scripts/build_docs_assets.py
├── scripts/docs_hook.py        # Lightweight pre-build synchronization
├── mkdocs.yml                  # Material theme, navigation and extensions
├── requirements.txt            # Existing scientific dependencies
├── requirements-docs.txt       # Website dependencies
├── .github/workflows/          # Validation and GitHub Pages delivery
└── website/                    # Preserved earlier Streamlit interface
```

## Scientific implementation

`src/validation.py` validates provenance and records cleaning. `src/stats.py` supplies shared numerical helpers; `src/hypothesis_h1.py` and `src/hypothesis_h2.py` organize the final analyses. `src/h2.py` preserves the underlying score-spread simulation. `src/run_analysis.py`, `src/plotting.py` and `src/reporting.py` orchestrate execution and output.

Optional collectors and metadata helpers remain in `src/fetch_games.py`, `src/explorer.py` and `src/wiki_scrape.py`. The archived `original_project/build_notebook.py` is historical and must not regenerate the current notebook.

## Website maintenance

Edit explanatory pages under `docs/`. Edit authoritative reports in their scientific source location, then regenerate their website copies; do not maintain independent report text. The asset generator exports validated aggregates and only the eleven final figure pairs. Browser filters read those exports without a server or statistical recomputation.

`site/` is a disposable build directory and is not committed. [Installation](../reproducibility/installation.md) explains local preview; [output provenance](../reproducibility/outputs.md) explains generated artifacts.
