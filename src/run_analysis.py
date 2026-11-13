"""Offline March study: python -m src.run_analysis (no routine downloads)."""
import argparse
import importlib.metadata
import json
import platform
from pathlib import Path

import numpy as np
import pandas as pd

from . import stats
from .hypothesis_h1 import h1_test, run_h1, clustered_score, rating_adjustment, N_SIM, SEED
from .hypothesis_h2 import analyze_replies, MIN_N_REPLY_MARCH
from .validation import validate_manifest, clean_games

ROOT = Path(__file__).resolve().parents[1]


def write_json(path, obj):
    def clean(x):
        if isinstance(x, dict):
            return {str(k): clean(v) for k, v in x.items()}
        if isinstance(x, (list, tuple)):
            return [clean(v) for v in x]
        if isinstance(x, np.generic):
            return clean(x.item())
        if isinstance(x, float) and not np.isfinite(x):
            return None
        return x
    Path(path).write_text(json.dumps(clean(obj), indent=2, allow_nan=False)+"\n")


def explorer_status(root):
    path = root/"data/raw/explorer_raw.csv"
    status = {"status": "unavailable", "reason": "No archived Explorer CSV"}
    if path.exists():
        raw = pd.read_csv(path)
        nested_valid = False
        try:
            fam = stats.derive_families(raw)
            nested_valid = bool((fam[list("WDB")] >= 0).all().all())
        except (AssertionError, KeyError, ValueError):
            pass
        status = dict(status="unverified_legacy", rows=len(raw), nested_totals_nonnegative=nested_valid,
                      has_date_columns={"since", "until"}.issubset(raw),
                      reason="Missing original query-period sidecar and response cache; dates cannot be authenticated",
                      comparison_permitted=False,
                      rating_semantics="Game sample uses floor of mean opponent Elo; Explorer alignment unverified")
    return status


def descriptive(g, provenance, cleaning, root):
    metrics = stats.outcome_metrics(g.result)
    weighted = stats.outcome_metrics(g.result, g.weight)
    counts = pd.concat([g.white, g.black], ignore_index=True).str.lower().value_counts()
    summary = dict(provenance=provenance, cleaning=cleaning, N=len(g), raw_metrics=metrics,
                   weighted_metrics=weighted, mean_plies=float(g.n_plies.mean()), median_plies=float(g.n_plies.median()),
                   mean_move_pairs=float(g.n_plies.mean()/2), median_move_pairs=float(g.n_plies.median()/2),
                   elo_difference=g.elo_difference.describe(percentiles=[.01, .05, .25, .5, .75, .95, .99]).to_dict(),
                   unique_players=len(counts), players_with_multiple_games=int(counts.gt(1).sum()),
                   max_games_per_player=int(counts.max()),
                   missing_titles={c: int(g[c].isna().sum()) for c in ["white_title", "black_title"]},
                   terminations={str(k): int(v) for k, v in g.termination.value_counts().items()},
                   resignations_heuristic=int(g.is_resignation.sum()),
                   short_games_under_10_plies=int(g.n_plies.lt(10).sum()),
                   sample_rate_counts={str(k): int(v) for k, v in g.sample_rate.value_counts().items()},
                   explorer=explorer_status(root))
    return summary


def eda_tables(g, out):
    rows = []
    for col in ["band", "speed", "rating_gap"]:
        for key, cell in g.groupby(col, observed=True):
            raw = stats.outcome_metrics(cell.result)
            weighted = stats.outcome_metrics(cell.result, cell.weight)
            rows.append(dict(dimension=col, group=str(key), **raw,
                             weighted_score=weighted["score"], weighted_draw_rate=weighted["draw_rate"]))
    diff = g.elo_difference
    signed = g.assign(signed_rating_gap=np.select(
        [diff < -100, diff < -25, diff <= 25, diff <= 100],
        ["White lower >100", "White lower 26-100", "Within 25", "White higher 26-100"],
        default="White higher >100"))
    for key, cell in signed.groupby("signed_rating_gap", observed=True):
        raw = stats.outcome_metrics(cell.result)
        weighted = stats.outcome_metrics(cell.result, cell.weight)
        rows.append(dict(dimension="signed_rating_gap", group=str(key), **raw,
                         weighted_score=weighted["score"], weighted_draw_rate=weighted["draw_rate"]))
    eda = pd.DataFrame(rows)
    eda.to_csv(out/"eda_summary.csv", index=False)
    g.groupby(["band", "speed"], observed=True).size().rename("N").to_csv(out/"sample_coverage.csv")
    for name, cols in [("opening_distribution", ["eco", "opening"]),
                       ("first_move_distribution", ["first_move"]),
                       ("black_reply_distribution", ["first_move", "black_reply"])]:
        freq = g.groupby(cols, observed=True).agg(N=("game_id", "size"), weighted_total=("weight", "sum"))
        freq.sort_values("N", ascending=False).to_csv(out/f"{name}.csv")
    g.groupby("utc_date").size().rename("N").to_csv(out/"daily_coverage.csv")
    return eda


def robustness(g, primary, h2_primary, n_sim=N_SIM, seed=SEED):
    rows = []
    scenarios = [("Unweighted sample", g, False)]
    for threshold in [10, 25, 50, 100]:
        scenarios.append((f"Absolute rating difference <= {threshold}", g[g.elo_difference.abs() <= threshold], True))
    scenarios.extend([
        ("Exclude time forfeits", g[g.termination != "Time forfeit"], True),
        ("At least 10 plies", g[g.n_plies >= 10], True),
        ("At least 40 plies", g[g.n_plies >= 40], True),
        ("Bands >=1200", g[g.band >= 1200], True),
        ("Bands <2200", g[g.band < 2200], True),
        ("Exclude classical", g[g.speed != "classical"], True),
    ])
    for name, cell, weighted in scenarios:
        r = h1_test(cell, weighted, n_sim, seed)
        rows.append(dict(hypothesis="H1", scenario=name, **r,
                         delta_primary_pp=100*(r["score"]-primary["score"]),
                         material_change=abs(r["score"]-primary["score"]) >= .01,
                         direction_changed=(r["score"] > .5) != (primary["score"] > .5),
                         significance_changed=(r["p_mc"] < .05) != (primary["p_mc"] < .05),
                         interpretation_stable=(r["score"] > .5 and r["p_mc"] < .05)))
    h2_scenarios = [(f"Reply floor {k}", g, k, 1200) for k in [100, 500, 1000]]
    h2_scenarios.extend([
        ("All rating bands", g, MIN_N_REPLY_MARCH, 0),
        ("Near equal <=25", g[g.elo_difference.abs() <= 25], MIN_N_REPLY_MARCH, 1200),
        ("Exclude time forfeits", g[g.termination != "Time forfeit"], MIN_N_REPLY_MARCH, 1200),
        ("At least 10 plies", g[g.n_plies >= 10], MIN_N_REPLY_MARCH, 1200),
    ])
    detail = []
    keys = ["first", "speed", "band"]
    base = h2_primary[h2_primary.status == "tested"]
    for name, cell, floor, band in h2_scenarios:
        summary, _ = analyze_replies(cell, floor, band, n_sim=n_sim, seed=seed, contrasts=False)
        tested = summary[summary.status == "tested"]
        merged = tested.merge(base[keys+["range_obs", "best", "worst", "reject_score"]], on=keys, suffixes=("", "_primary"))
        merged["range_change_pp"] = 100*(merged.range_obs-merged.range_obs_primary)
        merged["material_change"] = merged.range_change_pp.abs() >= 1.
        merged["significance_changed"] = merged.reject_score != merged.reject_score_primary
        merged["extreme_reply_changed"] = (merged.best != merged.best_primary)|(merged.worst != merged.worst_primary)
        merged["scenario"] = name
        detail.append(merged)
        rows.append(dict(hypothesis="H2", scenario=name, N=len(cell),
                         tested_cells=len(tested), rejected_cells=int(tested.reject_score.sum()),
                         distribution_rejected=int(tested.reject_distribution.sum()),
                         median_range_pp=float(tested.range_obs.median()*100) if len(tested) else np.nan,
                         matched_cells=len(merged), material_change=bool(merged.material_change.any()),
                         significance_changed=bool(merged.significance_changed.any()),
                         direction_changed=np.nan,  # spread is unsigned; extreme-reply stability is in detail table
                         interpretation_stable=bool(tested.reject_score.any()),
                         note="Exploratory; each scenario has its own BH family. Unsigned spread has no direction. interpretation_stable means at least one cell rejects, not stable cell decisions or ranks."))
    return pd.DataFrame(rows), pd.concat(detail, ignore_index=True)


def run_analysis(root=ROOT, output_root=None, n_sim=N_SIM, seed=SEED, make_reports=True):
    root = Path(root).resolve()
    dest = Path(output_root).resolve() if output_root else root
    out, figures, reports = [dest/d for d in ["results", "figures", "reports"]]
    for p in [out, figures, reports]:
        p.mkdir(parents=True, exist_ok=True)
    print("Validating March dataset and manifest...", flush=True)
    original, provenance = validate_manifest(root/"data/games_2025-03.parquet", root)
    g, cleaning = clean_games(original, band_by=provenance["manifest"]["args"]["band_by"])
    del original
    dataset = descriptive(g, provenance, cleaning, root)
    write_json(out/"dataset_summary.json", dataset)
    pd.DataFrame(cleaning["rules"]).to_csv(out/"cleaning_ledger.csv", index=False)
    eda = eda_tables(g, out)
    # EDA precedes H1/H2; major figures are assembled together after their inputs exist.
    print(f"Validated {len(g):,} games; running H1 ({n_sim:,} replicates)...", flush=True)
    h1 = run_h1(g, n_sim, seed)
    h1.to_csv(out/"h1_results.csv", index=False)
    primary = h1.iloc[0].to_dict()
    print("Running rating adjustment and shared-player sensitivity...", flush=True)
    adjusted, coefficients = rating_adjustment(g)
    coefficients.to_csv(out/"rating_model_coefficients.csv", index=False)
    clustered = clustered_score(g)
    h1_summary = dict(primary=primary, raw=h1_test(g, False, n_sim, seed),
                      near_equal=h1_test(g[g.elo_difference.abs() <= 25], True, n_sim, seed),
                      rating_adjusted=adjusted, dyadic=clustered,
                      alpha=.05, alternative="greater", seed=seed, n_sim=n_sim,
                      subgroup_tests=int(((h1.group_type != "primary")&(h1.status == "tested")).sum()),
                      adjustment="BH over speed, band and speed-band tests; primary excluded",
                      uncertainty="Poisson multiplier ratio bootstrap with Bernoulli finite-population correction",
                      exact_test="Unweighted decisive games only; not an exact weighted-pool test")
    write_json(out/"h1_summary.json", h1_summary)
    print("Running H2 reply simulations...", flush=True)
    h2, reply_scores = analyze_replies(g, n_sim=n_sim, seed=seed)
    h2.to_csv(out/"h2_results.csv", index=False)
    reply_scores.to_csv(out/"h2_reply_scores.csv", index=False)
    tested = h2[h2.status == "tested"]
    included = int(tested.included_games.sum())
    selected_n = int(g.first_move.isin(["e4", "d4"]).sum())
    h2_summary = dict(min_n=MIN_N_REPLY_MARCH, min_band=1200, n_sim=n_sim, seed=seed,
                      selected_e4_d4_games=selected_n, included_games=included,
                      total_selected_coverage=included/selected_n,
                      within_band_coverage=included/int(g[g.band >= 1200].first_move.isin(["e4", "d4"]).sum()),
                      tested_cells=len(tested), score_rejections=int(tested.reject_score.sum()),
                      distribution_rejections=int(tested.reject_distribution.sum()),
                      eligible_replies=sorted(reply_scores.loc[reply_scores.tested, "reply"].unique().tolist()),
                      eligible_by_first={fm: sorted(reply_scores.loc[reply_scores.tested & reply_scores["first"].eq(fm), "reply"].unique().tolist()) for fm in ["e4", "d4"]},
                      median_range_pp=float(tested.range_obs.median()*100),
                      min_range_pp=float(tested.range_obs.min()*100), max_range_pp=float(tested.range_obs.max()*100),
                      median_excess_sd_pp=float(tested.sd_excess.median()*100),
                      adjustment="Separate BH families for score-spread and full W/D/B-distribution omnibus tests",
                      assumptions="Independent games within each cell; representative dyadic sensitivity reported separately")
    write_json(out/"h2_summary.json", h2_summary)
    print("Running sensitivity analyses...", flush=True)
    robust, h2_sensitivity = robustness(g, primary, h2, n_sim, seed)
    robust.to_csv(out/"robustness_results.csv", index=False)
    h2_sensitivity.to_csv(out/"h2_sensitivity_cells.csv", index=False)
    pd.DataFrame([dict(source="Archived Explorer", status=dataset["explorer"]["status"],
                       comparison="unavailable", reason=dataset["explorer"]["reason"],
                       primary_period="2025-03", explorer_period="unverified",
                       rating_alignment="unverified; no numeric comparison made")]).to_csv(out/"source_comparison.csv", index=False)
    versions = {name: importlib.metadata.version(name) for name in
                ["numpy", "pandas", "scipy", "matplotlib", "seaborn", "pyarrow", "patsy", "nbclient", "pytest",
                 "requests", "lxml", "python-dotenv", "jupyter", "zstandard", "tabulate", "nbformat"]}
    versions["python"] = platform.python_version()
    write_json(out/"software_versions.json", versions)
    print("Generating figures and evidence-based reports...", flush=True)
    from .plotting import study_figures
    study_figures(g, h1, h2, reply_scores, figures, eda, n_sim=n_sim, seed=seed)
    if make_reports:
        from .reporting import write_reports
        write_reports(dest, dataset, h1, h1_summary, h2, reply_scores, h2_summary, robust)
    verify_artifacts(dest)
    print(f"Complete: {len(g):,} games; weighted score {primary['score']:.4%}; "
          f"H2 score tests {h2_summary['score_rejections']}/{len(tested)} rejected after BH. Outputs: {dest}", flush=True)
    return dict(dataset=dataset, h1=h1_summary, h2=h2_summary)


def verify_artifacts(root):
    """Smoke assertions on actual output content, not only file existence."""
    root = Path(root)
    for file in ["h1_results.csv", "h2_results.csv", "h2_reply_scores.csv", "robustness_results.csv", "source_comparison.csv"]:
        table = pd.read_csv(root/"results"/file)
        assert len(table), file
    h1 = pd.read_csv(root/"results/h1_results.csv")
    assert h1.iloc[0].N > 0 and 0 <= h1.iloc[0].lo <= h1.iloc[0].score <= h1.iloc[0].hi <= 1
    assert h1.loc[h1.status.eq("tested"), "p_mc"].between(0, 1).all()
    h2 = pd.read_csv(root/"results/h2_results.csv")
    tested = h2[h2.status == "tested"]
    assert len(tested) and tested.coverage.between(0, 1).all()
    assert tested.q_score.between(0, 1).all()
    for name in ["fig01_game_outcomes", "fig02_score_by_band", "fig03_score_by_speed", "fig04_draw_rate_by_band",
                 "fig05_rating_imbalance", "fig06_sample_coverage", "fig07_replies_e4", "fig08_replies_d4",
                 "fig09_reply_effect_heatmap", "fig10_h2_null_spread", "h1_score_confidence_intervals"]:
        for suffix in ["png", "pdf"]:
            assert (root/"figures"/f"{name}.{suffix}").stat().st_size > 1000
    dataset = json.loads((root/"results/dataset_summary.json").read_text())
    assert dataset["provenance"]["validated"] is True
    return True


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-root", type=Path, help="Alternate directory for generated artifacts")
    args = parser.parse_args()
    run_analysis(output_root=args.output_root)


if __name__ == "__main__":
    main()
