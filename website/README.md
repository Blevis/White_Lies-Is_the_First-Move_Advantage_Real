# White Lies Website & Interactive Dashboard

This is a **new, self-contained contribution** that adds a public-facing website and an interactive dashboard to the existing White Lies research repository.

## Safety and scope

- The website reads the existing files in `../results/` and `../figures/`.
- It does not edit the original research source code, dataset, reports, results, figures, or tests.
- It does not rerun the research pipeline or recalculate the scientific tests.
- H1/H2 filters select precomputed outputs. They are not new statistical tests.
- The four team member cards are placeholders. Replace them only after the team agrees on names and contribution descriptions.

## Pages

- **Home:** project introduction and headline results.
- **H1:** interactive filters for time control and rating band.
- **H2:** interactive first-move, time-control and rating-band exploration of Black replies.
- **Research & methodology:** hypotheses, sampling, weighting and limitations.
- **Figures:** original static research figures.
- **About the team:** project context and team credits.

## Run locally (Windows / Git Bash)

Open Git Bash in the repository root, then run:

```bash
py -m venv .venv-website
source .venv-website/Scripts/activate
py -m pip install -r website/requirements.txt
py -m streamlit run website/app.py
```

If `source` does not activate the environment in your Git Bash setup, use:

```bash
.venv-website/Scripts/activate
```

Streamlit prints a local URL, usually `http://localhost:8501`. Open it in your browser.

## Run locally (macOS / Linux)

```bash
python3 -m venv .venv-website
source .venv-website/bin/activate
python -m pip install -r website/requirements.txt
python -m streamlit run website/app.py
```

## Expected repository layout

The `website/` folder must be placed directly inside the existing repository root, next to `src/`, `results/`, and `figures/`:

```text
repository-root/
├── data/
├── figures/
├── results/
├── src/
├── tests/
└── website/
    ├── app.py
    ├── data_loader.py
    ├── requirements.txt
    └── README.md
```

## Before publishing

1. Confirm with the team that the website's wording matches the final research interpretation.
2. Replace the four team placeholders with approved credits.
3. Test every page and filter locally.
4. Check that all original results and figure files are still present.
5. Review the final diff before committing.

## Attribution

This website presents existing research outputs from the White Lies project. It should be credited as a separate website/dashboard contribution, not as authorship of the underlying statistical analysis or dataset collection.
