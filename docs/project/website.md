---
title: Website maintenance
description: Preview, check and publish the MkDocs website using the saved analysis outputs.
---

# Maintain the website

The website uses the versions pinned in `requirements-docs.txt`: **MkDocs 1.6.1** and **Material for MkDocs 9.8.1**. It reads saved study results. Building it does not run the research analysis or download games.

## Preview and check

Use **Python 3.11 or newer**. Follow [Set up Python](../reproducibility/installation.md) to create the documentation environment, then run from the repository root:

```bash
python -m mkdocs serve
```

Open the local address printed by MkDocs, usually `http://127.0.0.1:8000/`. Serve the site over HTTP so the explorer can load its data file.

Before publishing, run:

```bash
python scripts/build_docs_assets.py --check
python -m mkdocs build --strict
python scripts/check_site.py
git diff --check
```

The compiled pages go to `site/`, which is ignored by Git.

## Where to edit

| Change | Source to edit |
| --- | --- |
| Main story and study reference | `docs/research/`, except the generated report page |
| Homepage | `docs/index.md` |
| Menu and reading order | `mkdocs.yml` |
| Chart explanations and supporting guides | Other Markdown pages under `docs/` |
| Full report or research audit | Original files in `reports/`, then regenerate the site copies |
| Explorer labels and behavior | `docs/assets/js/explorer.js` |
| Layout and colors | `docs/assets/css/site.css` and `explorer.css` |

The main story follows **questions → approach → White's score → Black's replies → checks and limits → conclusion**. Keep short explanations in that order, define terms before using them, and link to the detailed methods for formulas. The [study reference](../research/reference.md) collects the graph index, formulas, glossary and code map. Keep Study pages written for readers: no speaker prompts, timing plans or presentation instructions.

## Generated files

`scripts/build_docs_assets.py` copies reports and the eleven final PNG/PDF figure pairs, and exports group summaries to `docs/assets/data/research.json`. The MkDocs build runs this step automatically. The export contains no individual games or player names.

To refresh these files explicitly:

```bash
python scripts/build_docs_assets.py
```

Edit source reports and results before regenerating their copies. Original report downloads and figures are kept byte for byte. Source-file checksums record which analysis outputs were used.

!!! note "Running the analysis can rewrite documentation"
    The scientific pipeline's default run regenerates a research README. For a separate reproduction, use `python -m src.run_analysis --output-root /path/to/separate-output`. See [Run the analysis](../reproducibility/running.md).

## Publish with GitHub Pages

The workflow in `.github/workflows/docs.yml` checks pull requests. Pushes to `main`, or manual runs from `main`, also build and deploy the website through GitHub Actions.

In the repository's **Settings → Pages → Build and deployment → Source**, use **GitHub Actions**. Make sure the `github-pages` environment allows deployment from `main`.

The configured default address is [the White Lies website](https://blevis.github.io/White_Lies-Is_the_First-Move_Advantage_Real/). During deployment, the workflow supplies the Pages base URL through `SITE_URL`. It uploads the built `site/` folder without committing compiled pages or raw games. Local edits appear online after they are committed, merged and successfully deployed.

## Browser checks

The optional `scripts/smoke_site.py` script checks themes, search, filters, opening moves and layouts at several widths. It requires Playwright separately from the website dependencies; its header gives setup instructions.

Also read through the six study pages in order. Check mobile tables, menu labels, next-page links, the study reference and any expandable technical details. The [validation guide](../reproducibility/validation.md) explains the difference between research checks and website checks.

## Fonts and other assets

The site bundles Fraunces and Manrope fonts with their SIL Open Font Licenses. Formula rendering uses KaTeX 0.16.22 with its MIT license. Those licenses apply to the bundled third-party assets; they do not assign a new license to the research project.
