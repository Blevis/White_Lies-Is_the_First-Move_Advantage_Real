---
title: Research sources
description: The primary Lichess data, authoritative project reports, methodological references and excluded historical sources.
---

# Sources and attribution

The website is an interface to the repository's completed March analysis. Its figures and numerical findings come from the recorded outputs, with the [full research report](../research/report.md) serving as the authoritative narrative.

## Primary data

The [Lichess database](https://database.lichess.org/) supplies the [March 2025 rated-standard dump](https://database.lichess.org/standard/lichess_db_standard_rated_2025-03.pgn.zst). The retained sample and local collection manifest establish the study's documented provenance. The site publishes small aggregate exports and final figures, not individual game or player records.

## Project evidence

| Document | Role |
| --- | --- |
| [Full research report](../research/report.md) | Questions, data, methods, results, robustness and limits |
| [Original report Markdown](../assets/reports/FINAL_RESEARCH_REPORT.md) | Direct access to the source narrative |
| [Short conclusion](../assets/reports/FINAL_CONCLUSION.md) | Condensed interpretation |
| [Implementation audit](audit.md) | Baseline findings and recorded analysis choices |
| [Research completion checklist](../assets/reports/COMPLETION_CHECKLIST.md) | Historical scientific validation record |
| [Output map](../reproducibility/outputs.md) | CSV and JSON evidence for displayed findings |

## Methodological references cited by the report

- [Benjamini and Hochberg, controlling the false discovery rate](https://doi.org/10.1111/j.2517-6161.1995.tb02031.x): the multiple-testing procedure used in the specified families.
- [Aronow, Samii and Assenova, dyadic variance estimation](https://arxiv.org/abs/1312.3398): shared-member dependence structure used for covariance sensitivity.
- [SciPy exact binomial test documentation](https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.binomtest.html): the decisive-game conditional cross-check for equal-weight or unweighted estimates.

These references provide methodological context. They do not independently validate this dataset or imply endorsement of the project.

## Historical sources are kept separate

The [official Lichess Opening Explorer query implementation](https://github.com/lichess-org/lila-openingexplorer/blob/master/src/api/query.rs) supports explicit month filters. That current capability does not authenticate the period of the repository's archived Explorer CSV. Its original query sidecars and response cache are unavailable, and its rating buckets are not verified as equivalent to this study's mean-Elo bands.

No aligned numeric Explorer comparison or validated full ECO join is claimed. See [limitations](../research/limitations.md) and [provenance](../methodology/data.md).
