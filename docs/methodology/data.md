---
title: Dataset and provenance
description: Where the March 2025 games came from, how source accounting is validated and which historical data are excluded.
---

# A sample with an audit trail

The primary input is a deterministic sample of the [Lichess March 2025 rated-standard monthly dump](https://database.lichess.org/standard/lichess_db_standard_rated_2025-03.pgn.zst). The games were played **March 1–31, 2025**. Collection occurred in November 2026; collection dates do not change the game period.

## Three quantities to keep separate

| Quantity | Value | Meaning |
| --- | ---: | --- |
| Source games scanned | 97,512,351 | Games encountered before eligibility and sampling |
| Observed sampled games | 836,070 | Validated game records entering the primary analysis |
| Estimated eligible population total | 59,802,180 | Sum of inverse-probability weights; an estimate, not observed N |

The collector streamed **31,787,738,173 compressed bytes**. The complete compressed monthly dump is not included in the repository. Routine analysis reads the retained Parquet sample and manifest, and does not download the dump.

## Validated local inputs

The required pair is `data/games_2025-03.parquet` and `data/games_2025-03.parquet.manifest.json`. The recorded SHA-256 of the Parquet file is:

```text
e055e8f921b3b242188c0493d57acc8fe83a2200ee0223e6cb817dc5a627ffaa
```

`src/validation.py` checks completion, source month and URL, file location and checksum, row count, per-cell counts, deterministic hash thresholds, declared sampling rates and source accounting. The exported `results/dataset_summary.json` records the results of those checks. All 836,070 retained records passed additional cleaning, with **zero further exclusions**.

!!! note "What a checksum establishes"
    The checksum verifies agreement between the local data and local manifest. It does not independently authenticate the original remote dump or repeat the source scan.

## What is absent from the confirmatory evidence?

The archived `data/raw/explorer_raw.csv` lacks an authenticatable query period and cached responses. The legacy game CSV excludes resignations and has a different selection mechanism. Neither supplies the final March estimates. `results/source_comparison.csv` explicitly records that the aligned Explorer comparison is unavailable.

Continue with [sampling and exclusions](sampling.md), [output provenance](../reproducibility/outputs.md) or the [authoritative report](../research/report.md#3-dataset).
