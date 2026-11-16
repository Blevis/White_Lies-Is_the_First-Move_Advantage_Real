---
title: Research sources
description: The primary Lichess data, authoritative project reports, methodological references and excluded historical sources.
---

# Sources and attribution

The website explains the completed March 2025 analysis. Its numbers and charts come from the saved project outputs. The [full report](../research/report.md) contains the complete technical record.

## Primary data

The [Lichess database](https://database.lichess.org/) supplies the [March 2025 rated-standard dump](https://database.lichess.org/standard/lichess_db_standard_rated_2025-03.pgn.zst). The saved sample and its manifest record how the games were collected and checked. The site displays group summaries and final charts, without individual game records or player names.

## Project evidence

| Document | Role |
| --- | --- |
| [Full research report](../research/report.md) | Questions, data, methods, results, robustness and limits |
| [Original report Markdown](../assets/reports/FINAL_RESEARCH_REPORT.md) | Direct access to the source narrative |
| [Short conclusion](../assets/reports/FINAL_CONCLUSION.md) | Condensed interpretation |
| [Implementation audit](audit.md) | Baseline findings and recorded analysis choices |
| [Research completion checklist](../assets/reports/COMPLETION_CHECKLIST.md) | Historical scientific validation record |
| [Output map](../reproducibility/outputs.md) | CSV and JSON evidence for displayed findings |

## References for the statistical methods

- [Benjamini and Hochberg, controlling the false discovery rate](https://doi.org/10.1111/j.2517-6161.1995.tb02031.x): the adjustment used when running many tests.
- [Aronow, Samii and Assenova, dyadic variance estimation](https://arxiv.org/abs/1312.3398): a method for estimating uncertainty when games share players.
- [SciPy exact binomial test documentation](https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.binomtest.html): the additional check using games with a winner, where weights are equal or absent.

These references provide methodological context. They do not independently validate this dataset or imply endorsement of the project.

## Historical sources are kept separate

The repository also contains older Lichess Opening Explorer results. The original queries and saved responses are unavailable, so their dates and rating groups cannot be verified. These results are excluded from the March evidence.

The study does not claim a verified comparison with those older results or a complete mapping to standard opening codes. See [limitations](../research/limitations.md) and [provenance](../methodology/data.md).
