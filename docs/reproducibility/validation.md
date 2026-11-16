---
title: Validation and testing
description: Separate scientific, artifact and website checks, with explicit limits on what passing checks establish.
---

# Check the analysis and website

Check the analysis results and the website separately. A successful website build shows that the pages work, not that every research claim is valid.

## Analysis checks

With the scientific environment active, run:

```bash
python -m pytest -q
python tests/mock_run.py
```

The suite covers outcome identities, invalid inputs, provenance tampering, null calibration, planted effects, weighting imbalance, sparse replies, draw-only distribution changes, rating adjustment, dyadic covariance and artifact consistency. `tests/mock_run.py` checks frozen output artifacts; it does not rerun the entire analysis or download source data.

The original research [completion checklist](../assets/reports/COMPLETION_CHECKLIST.md) records **65 passing tests** on November 13, 2026. That is a historical scientific-run result, not an automatically updated assertion about every future checkout. Use current command output when evaluating a new change.

## Website checks

With documentation dependencies installed:

```bash
python scripts/build_docs_assets.py --check
python -m mkdocs build --strict
git diff --check
```

If aggregate outputs have intentionally changed, regenerate first with `python scripts/build_docs_assets.py`, inspect the source differences, then repeat the checks. Strict MkDocs validation detects documentation warnings such as missing referenced files and invalid navigation.

## What to inspect in the browser

Check the homepage, report and explorer at narrow and wide widths. Operate filters and the opening board with a keyboard; inspect empty states, chart intervals, table scrolling and the 50% benchmark. Confirm search, theme switching, navigation and reduced-motion behavior. Source and figure links must resolve from the GitHub Pages repository subpath.

Filters should display only saved estimates. Missing groups should explain why no result is available. Keep weighted percentages separate from actual game counts. Selecting one reply should not make the whole-group test look like a test of that move.

## Limits of validation

A matching checksum confirms agreement with the local manifest, without rescanning the original archive. Passing checks does not prove cause and effect, remove assumptions about related games, or verify the dates of the older Explorer data.

See [provenance](../methodology/data.md), [uncertainty](../methodology/uncertainty.md) and the [research audit](../project/audit.md).
