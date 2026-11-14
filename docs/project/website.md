---
title: Website maintenance
description: Build, validate and deploy the White Lies MkDocs publication without running or modifying the scientific analysis.
---
# Website maintenance

The publication uses **MkDocs 1.6.1 and Material for MkDocs 9.8.1**, with local fonts, modular CSS, vanilla JavaScript and precomputed aggregate results. There is no server, live chess engine, analytics service or game-level download in the site. Python **3.11 or newer** is required.

## Preview locally

From the repository root, use a separate documentation environment:

=== "Linux / macOS"

    ```bash
    python3 -m venv .venv-docs
    source .venv-docs/bin/activate
    python -m pip install -r requirements-docs.txt
    python -m mkdocs serve
    ```

=== "Windows PowerShell"

    ```powershell
    py -3 -m venv .venv-docs
    .\.venv-docs\Scripts\Activate.ps1
    python -m pip install -r requirements-docs.txt
    python -m mkdocs serve
    ```

Open `http://127.0.0.1:8000/`. Search, theme switching, the explorer and board work from the static build too. Serve the output over HTTP; browser `file://` access does not permit the explorer's JSON request.

## Synchronized publication assets

`scripts/build_docs_assets.py` reads only existing result tables, reports and final figure files. A MkDocs hook calls it before every build. It never imports the research pipeline or reads the game-level Parquet input.

- The report and audit reading pages are synchronized from their authoritative Markdown sources.
- Original Markdown reports remain downloadable, byte for byte.
- The eleven final figure pairs are copied with their original PNG and PDF bytes.
- `assets/data/research.json` contains typed aggregate rows, explicit nulls and SHA-256 hashes of its inputs.
- Validation checks confirm the primary estimate, confidence interval, sample count, H2 decision families and source accounting before publishing.

Do not edit generated assets to change a research result. Update and validate the authoritative outputs first, then regenerate:

```bash
python scripts/build_docs_assets.py
python scripts/build_docs_assets.py --check
python -m mkdocs build --strict
python scripts/check_site.py
```

The last command checks internal pages, anchors and local assets in the built site. `site/`, `.venv-docs/` and browser screenshots in `artifacts/` are ignored by Git.

!!! note "Research regeneration and the README"
    The existing research pipeline's default run writes a generated research README. To preserve publication documentation while reproducing the study, use `python -m src.run_analysis --output-root /path/to/separate-output`. The scientific pipeline has been preserved unchanged. See [Running the analysis](../reproducibility/running.md).

## GitHub Pages

The repository's default branch is **`main`**. At the implementation audit on **November 14, 2026**, the GitHub API reported `has_pages: false`; the Pages endpoint returned 404. No live site URL is claimed.

The workflow in `.github/workflows/docs.yml` validates pull requests and builds deployments on pushes to `main` or manual runs from `main`. It uses the official checkout, Python setup, Pages configuration, artifact upload and Pages deployment actions. Only the deployment job has Pages write and identity-token permissions. Its concurrency group prevents competing deployments.

To enable the first deployment:

1. In the GitHub repository, open **Settings → Pages → Build and deployment** and select **GitHub Actions**.
2. Merge the website implementation into `main`, or run the documentation workflow from `main` once it contains these files.
3. Confirm that the `github-pages` environment permits deployment from `main` and review the workflow's successful deployment URL.

With GitHub's standard project-site configuration, the expected address is `https://blevis.github.io/White_Lies-Is_the_First-Move_Advantage_Real/`. This is an **expected address, not a verified deployment**.

Canonical and social URLs are deliberately omitted from local and pull-request builds. The deployment workflow passes the **verified `base_url` output of `actions/configure-pages`** through `SITE_URL`. It accommodates a custom domain without hardcoding an unverified address. For a verified deployment, a local release preview can use that same `SITE_URL` value.

The workflow uploads `site/`; it never commits compiled pages or raw games. It installs documentation dependencies only and does not run the expensive analysis. See GitHub's [official custom Pages workflow documentation](https://docs.github.com/en/pages/getting-started-with-github-pages/using-custom-workflows-with-github-pages).

## Browser verification

Browser tooling is optional and separate from production dependencies. The browser smoke script exercises responsive layout, search, themes, filters, sparse cells and board moves against a served build. See the [website implementation report](https://github.com/Blevis/White_Lies-Is_the_First-Move_Advantage_Real/blob/main/reports/WEBSITE_IMPLEMENTATION.md) for the exact executed checks and screenshots.

Accessibility features include semantic regions, visible focus, explicit chart labels and interval text, keyboard-operable native controls, reduced motion, local fonts and dark/light palettes. These checks are practical verification, not a claim of formal WCAG certification.

## Modular customization

| Location | Responsibility |
|---|---|
| `mkdocs.yml` | Navigation, Material features, Markdown extensions and asset hook |
| `docs/index.md` | Editorial landing page |
| `docs/assets/css/site.css` | Publication tokens, typography and responsive composition |
| `docs/assets/css/explorer.css` | Dashboard and chessboard components |
| `docs/assets/js/site.js` | Progressive reveal and on-demand local formula rendering |
| `docs/assets/js/explorer.js` | Aggregate filtering, charts, tables and explanatory moves |
| `overrides/` | Thin Material templates and social metadata |
| `scripts/build_docs_assets.py` | Deterministic source synchronization and checks |

Fonts are local subsets of **Fraunces** and **Manrope**, obtained from the [Google Fonts repository](https://github.com/google/fonts); their SIL Open Font License files are alongside the fonts. Formula rendering uses local **KaTeX 0.16.22** with its MIT license retained. The hero illustration and chess identity mark were created for this site. These third-party asset licenses do not imply a new license for the research repository.
