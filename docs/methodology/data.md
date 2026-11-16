---
title: Data and source checks
description: Where the games came from, what the sample contains, and how the local files were checked.
---

# Where the games came from

We used the [Lichess March 2025 archive of rated standard games](https://database.lichess.org/standard/lichess_db_standard_rated_2025-03.pgn.zst). The games were played **March 1–31, 2025** and collected in November 2026.

## Which game count should I use?

| Count | Value | Meaning |
| --- | ---: | --- |
| Games scanned | 97,512,351 | All games the collector read, before exclusions and sampling |
| Games studied | **836,070** | The sampled game records used in the main analysis |
| Estimated eligible total | 59,802,180 | The total represented by the sampling weights; not an observed count |

Use **836,070** when describing the study's sample size. The sample is not the full month of Lichess games.

The collector read 31,787,738,173 compressed bytes. The full monthly archive is not bundled with the project. Running the analysis uses the saved sample and does not download the archive again.

## How were the saved files checked?

The analysis requires both:

- `data/games_2025-03.parquet`: the sampled games.
- `data/games_2025-03.parquet.manifest.json`: a record of the source, sampling rules, counts and file checksum.

The validator checks the source month and URL, file location, checksum, number of games, group counts and sampling rules. It also checks that the recorded exclusions and sampling counts add up to the scanned total.

All **836,070 records** passed the later cleaning checks, with **zero additional exclusions**. Results are saved in `results/dataset_summary.json` and `results/cleaning_ledger.csv`.

??? info "File checksum and its limits"
    A checksum is a fingerprint of a file. The recorded SHA-256 is:

    ```text
    e055e8f921b3b242188c0493d57acc8fe83a2200ee0223e6cb817dc5a627ffaa
    ```

    A match confirms that the local file agrees with the local manifest. It does not independently verify the original remote archive or repeat the source collection.

## Why not use the older data too?

The archived Opening Explorer CSV has no verifiable query period or saved responses. The legacy game CSV excludes resignations and was collected differently. Neither is used for the final March findings.

Continue with [sampling and exclusions](sampling.md), or return to [the study overview](../research/approach.md).
