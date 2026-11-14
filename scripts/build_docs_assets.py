"""Export the frozen March research for MkDocs, without running any analysis.

Only aggregate outputs, final figures and reports are read. No game-level data,
scientific packages, network access or random numbers are involved. Run with
``--check`` to detect stale/missing generated files without writing anything.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
FIGURES = (
    "fig01_game_outcomes", "fig02_score_by_band", "fig03_score_by_speed",
    "fig04_draw_rate_by_band", "fig05_rating_imbalance", "fig06_sample_coverage",
    "fig07_replies_e4", "fig08_replies_d4", "fig09_reply_effect_heatmap",
    "fig10_h2_null_spread", "h1_score_confidence_intervals",
)
REPORTS = (
    "FINAL_RESEARCH_REPORT.md", "FINAL_CONCLUSION.md",
    "implementation_audit.md", "COMPLETION_CHECKLIST.md",
)
RESULTS = (
    "dataset_summary.json", "h1_summary.json", "h1_results.csv",
    "h2_summary.json", "h2_results.csv", "h2_reply_scores.csv",
    "robustness_results.csv",
)
H1_FIELDS = (
    "group", "group_type", "speed", "band", "N", "score", "lo", "hi",
    "difference_pp", "weight_total", "effective_n", "white_wins", "draws",
    "black_wins", "draw_rate", "white_win_rate", "black_win_rate", "p_mc",
    "weighted", "n_sim", "status", "p_adjusted", "reject", "interpretation",
)
H2_FIELDS = (
    "first", "speed", "band", "total_games", "eligible_replies",
    "included_games", "coverage", "min_n", "status", "k", "N", "pooled",
    "sd_obs", "sd_null_mean", "sd_excess", "range_obs", "n_sim", "q_score",
    "q_distribution", "reject_score", "reject_distribution",
)
REPLY_FIELDS = (
    "first", "speed", "band", "reply", "W", "D", "B", "N", "draw_rate",
    "eligible", "tested", "score", "lo", "hi",
)
ROBUSTNESS_FIELDS = (
    "hypothesis", "scenario", "N", "score", "lo", "hi", "difference_pp",
    "weighted", "status", "delta_primary_pp", "material_change",
    "direction_changed", "significance_changed", "interpretation_stable",
    "tested_cells", "rejected_cells", "distribution_rejected", "median_range_pp",
    "note",
)


def source_paths() -> tuple[str, ...]:
    return (
        *(f"results/{name}" for name in RESULTS),
        *(f"reports/{name}" for name in REPORTS),
        *(f"figures/{name}.{ext}" for name in FIGURES for ext in ("png", "pdf")),
    )


def typed_value(value: str | None) -> Any:
    """Parse CSV scalars without converting notation such as e4 into a number."""
    if value is None or value == "":
        return None
    if value in ("True", "False"):
        return value == "True"
    try:
        number = float(value)
    except ValueError:
        return value
    if not math.isfinite(number):
        return None
    return int(number) if number.is_integer() else number


def read_rows(root: Path, name: str, fields: tuple[str, ...]) -> list[dict]:
    with (root / "results" / name).open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        missing = set(fields) - set(reader.fieldnames or ())
        if missing:
            raise ValueError(f"{name}: missing required columns {sorted(missing)}")
        return [{field: typed_value(row[field]) for field in fields} for row in reader]


def read_json(root: Path, name: str) -> dict:
    return json.loads((root / "results" / name).read_text(encoding="utf-8"))


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(f"Research asset validation failed: {message}")


def validate_payload(payload: dict, dataset: dict) -> None:
    """Fail closed on inconsistent outputs; never create replacement findings."""
    summary = payload["h1"]["summary"]
    primary = summary["primary"]
    h1_rows = payload["h1"]["rows"]
    h2 = payload["h2"]
    require(dataset["provenance"]["validated"], "dataset provenance is not validated")
    require(all(dataset["provenance"]["checks"].values()), "a provenance check failed")
    require(dataset["N"] == primary["N"] == 836070, "primary sample count changed")
    require(dataset["provenance"]["manifest"]["games_seen"] == 97512351,
            "source scan count changed")
    require(dataset["provenance"]["date_min"] == "2025-03-01" and
            dataset["provenance"]["date_max"] == "2025-03-31", "study dates changed")
    require(summary["n_sim"] == h2["summary"]["n_sim"] == 10000,
            "Monte Carlo replicate count changed")
    require(primary["score"] == dataset["weighted_metrics"]["score"],
            "weighted score differs between exported summaries")
    expected = {"score": "51.776", "lo": "51.653", "hi": "51.899"}
    for key, rounded in expected.items():
        require(f"{100 * primary[key]:.3f}" == rounded,
                f"primary {key} no longer agrees with the publication")
    require(f"{primary['difference_pp']:.3f}" == "1.776", "primary excess changed")
    require(math.isclose(primary["p_mc"], 1 / (summary["n_sim"] + 1), rel_tol=1e-12),
            "primary Monte Carlo value no longer equals the resolution floor")
    require(f"{100 * summary['rating_adjusted']['score']:.3f}" == "51.886",
            "rating-standardized result changed")
    require(len([row for row in h1_rows if row["group_type"] == "primary"]) == 1,
            "H1 needs exactly one primary row")
    for row in h1_rows:
        require(row["N"] == row["white_wins"] + row["draws"] + row["black_wins"],
                "H1 observed outcome counts do not sum to N")
        require(math.isclose(row["score"], row["white_win_rate"] + row["draw_rate"] / 2,
                             abs_tol=1e-12), "H1 score and outcome probabilities disagree")
        require(math.isclose(row["white_win_rate"] + row["draw_rate"] +
                             row["black_win_rate"], 1, abs_tol=1e-12),
                "H1 outcome probabilities do not sum to one")
        for key in ("N", "score", "lo", "hi"):
            if row["group_type"] == "primary":
                require(row[key] == primary[key], f"primary H1 CSV {key} differs from JSON")
    for kind in ("speed", "band", "cell"):
        subset = [row for row in h1_rows if row["group_type"] == kind]
        require(sum(row["N"] for row in subset) == primary["N"],
                f"{kind} sample accounting differs from primary N")
        total = sum(row["weight_total"] for row in subset)
        combined = sum(row["score"] * row["weight_total"] for row in subset) / total
        require(math.isclose(combined, primary["score"], abs_tol=1e-12),
                f"weighted {kind} estimates do not reconstruct the primary score")
    tested = [row for row in h2["cells"] if row["status"] == "tested"]
    require(len(tested) == h2["summary"]["tested_cells"] == 35, "H2 tested-cell count changed")
    for field, count, expected_count in (("reject_score", "score_rejections", 14),
                                         ("reject_distribution", "distribution_rejections", 15)):
        require(sum(row[field] for row in tested) == h2["summary"][count] == expected_count,
                f"H2 {count} differs between CSV, summary and publication")
    require(sum(row["N"] for row in h2["replies"]) ==
            sum(row["total_games"] for row in h2["cells"]) == h2["summary"]["selected_e4_d4_games"],
            "H2 reply partitions do not account for the selected e4/d4 games")
    require(sum(row["N"] for row in h2["replies"] if row["tested"]) ==
            h2["summary"]["included_games"], "H2 included-game count disagrees")
    for row in h2["replies"]:
        require(row["N"] == row["W"] + row["D"] + row["B"], "H2 outcome counts disagree")
        require(math.isclose(row["score"], (row["W"] + row["D"] / 2) / row["N"],
                             abs_tol=1e-12), "H2 reply score differs from observed counts")
        require(not row["tested"] or (row["eligible"] and row["N"] >= 200 and row["band"] >= 1200),
                "tested reply violates primary eligibility")
    for row in (*h1_rows, *h2["replies"], *payload["robustness"]):
        if row["lo"] is not None and row["hi"] is not None:
            require(0 <= row["lo"] <= row["score"] <= row["hi"] <= 1,
                    "exported confidence interval does not contain its estimate")
    length = next(row for row in payload["robustness"]
                  if row["hypothesis"] == "H1" and row["scenario"] == "At least 40 plies")
    require(length["material_change"] and length["score"] < primary["score"],
            "game-length sensitivity no longer matches the publication caveat")


def research_payload(root: Path) -> dict:
    dataset = read_json(root, "dataset_summary.json")
    provenance = dataset["provenance"]
    payload = {
        "schema_version": 1,
        "provenance": {
            "period": "March 1–31, 2025",
            "start": provenance["date_min"], "end": provenance["date_max"],
            "sampled_games": dataset["N"],
            "scanned_games": provenance["manifest"]["games_seen"],
            "source": provenance["manifest"]["url"],
            "source_files": list(source_paths()),
            "sha256": {name: hashlib.sha256((root / name).read_bytes()).hexdigest()
                       for name in source_paths()},
            "scope": "Validated aggregate outputs only; no game-level records or new inference.",
            "intervals": "Marginal 95% intervals; see the research report for assumptions.",
        },
        "h1": {
            "summary": read_json(root, "h1_summary.json"),
            "rows": read_rows(root, "h1_results.csv", H1_FIELDS),
        },
        "h2": {
            "summary": read_json(root, "h2_summary.json"),
            "cells": read_rows(root, "h2_results.csv", H2_FIELDS),
            "replies": read_rows(root, "h2_reply_scores.csv", REPLY_FIELDS),
        },
        "robustness": read_rows(root, "robustness_results.csv", ROBUSTNESS_FIELDS),
    }
    validate_payload(payload, dataset)
    return payload


def report_page(root: Path, source_name: str, title: str, description: str) -> bytes:
    source = (root / "reports" / source_name).read_text(encoding="utf-8")
    source = source.replace("](../figures/", "](../assets/figures/")
    # These are reading aids only; the scientific body remains synchronized.
    front = (
        f"---\ntitle: {title}\ndescription: {description}\n---\n\n"
        "<!-- Generated by scripts/build_docs_assets.py; edit the original report. -->\n\n"
        f"[Download the original Markdown](../assets/reports/{source_name})"
        f" · [View research source](https://github.com/Blevis/White_Lies-Is_the_First-Move_Advantage_Real/blob/main/reports/{source_name})\n\n"
        "> This page is synchronized from the repository's authoritative research record. "
        "Its verification statements describe the scientific study at the recorded date; "
        "website validation is documented separately.\n\n"
    )
    return (front + source).encode("utf-8")


def expected_assets(root: Path) -> dict[Path, bytes]:
    payload = research_payload(root)
    assets = {
        Path("docs/assets/data/research.json"): (
            json.dumps(payload, ensure_ascii=False, allow_nan=False, separators=(",", ":")) + "\n"
        ).encode("utf-8"),
        Path("docs/research/report.md"): report_page(
            root, "FINAL_RESEARCH_REPORT.md", "Full research report",
            "The authoritative March 2025 study, including data, methods, results and limitations.",
        ),
        Path("docs/project/audit.md"): report_page(
            root, "implementation_audit.md", "Research audit",
            "The original scientific audit, prespecified analysis decisions and verification record.",
        ),
    }
    for name in REPORTS:
        assets[Path("docs/assets/reports") / name] = (root / "reports" / name).read_bytes()
    for name in FIGURES:
        for ext in ("png", "pdf"):
            assets[Path("docs/assets/figures") / f"{name}.{ext}"] = (
                root / "figures" / f"{name}.{ext}"
            ).read_bytes()
    return assets


def build_assets(root: Path = ROOT, *, check: bool = False) -> list[str]:
    """Return changed paths; --check mode never writes files."""
    changed = []
    for relative, content in expected_assets(root).items():
        path = root / relative
        if not path.exists() or path.read_bytes() != content:
            changed.append(relative.as_posix())
            if not check:
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(content)
    return changed


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="Fail on stale exports without writing")
    args = parser.parse_args()
    try:
        changed = build_assets(check=args.check)
    except (OSError, ValueError, KeyError, StopIteration) as exc:
        parser.exit(1, f"Documentation asset error: {exc}\n")
    if args.check and changed:
        print("Stale or missing documentation assets:")
        print("\n".join(changed))
        return 1
    print(f"Documentation assets {'verified' if args.check else 'synchronized'}; "
          f"{len(changed)} file(s) {'stale' if args.check else 'updated'}.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
