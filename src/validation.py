"""Fail-closed provenance validation and explicitly counted record exclusions."""
import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd

from .fetch_games import BANDS, COLUMNS, RESULTS, hash_unit, parse_overrides


class ValidationError(ValueError):
    """Input cannot be described as a validated collection."""


def validate_manifest(path, root=None):
    path = Path(path).resolve()
    root = Path(root or Path(__file__).resolve().parents[1]).resolve()
    manifest_path = Path(str(path) + ".manifest.json")
    if not path.is_file() or not manifest_path.is_file():
        raise ValidationError("Dataset or manifest is missing")
    m = json.loads(manifest_path.read_text())
    checks = {}
    checks["complete"] = m.get("complete") is True and m.get("error") is None
    a = m.get("args", {})
    checks["no_limit"] = a.get("limit") is None
    checks["path"] = (root / m.get("output", "")).resolve() == path
    checks["argument_path"] = (root / a.get("out", "")).resolve() == path
    with path.open("rb") as f:
        digest = hashlib.file_digest(f, "sha256").hexdigest()
    checks["checksum"] = digest == m.get("output_sha256")
    g = pd.read_parquet(path) if path.suffix == ".parquet" else pd.read_csv(path)
    checks["schema"] = set(COLUMNS).issubset(g.columns)
    checks["row_count"] = len(g) == m.get("games_kept") and len(g) > 0
    checks["accounting"] = (m.get("games_seen", -1) == m.get("games_kept", 0)
                            + m.get("games_not_sampled", 0) + sum(m.get("rejections", {}).values()))
    month = m.get("source_month")
    checks["source"] = (month == a.get("month") and m.get("url") ==
                         f"https://database.lichess.org/standard/lichess_db_standard_rated_{month}.pgn.zst")
    checks["rejection_rules"] = set(m.get("rejections", {})) == {
        "speed", "rating", "result", "termination", "bot", "min_plies"}
    checks["criteria"] = (a.get("min_plies") == 2 and a.get("band_by") in {"avg", "min", "max"}
                           and set(a.get("speeds", "").split(",")) == {"blitz", "rapid", "classical"}
                           and set(a.get("keep_terminations", "").split(",")) == {"Normal", "Time forfeit"})
    if checks["schema"]:
        checks["source_month"] = g.source_month.eq(month).all()
        dates = pd.to_datetime(g.utc_date, format="%Y-%m-%d", errors="coerce")
        checks["date_coverage"] = dates.notna().all() and dates.dt.strftime("%Y-%m").eq(month).all()
        counts = {f"{s}/{int(b)}": int(n) for (s, b), n in g.groupby(["speed", "band"]).size().items()}
        checks["cell_counts"] = counts == m.get("kept_per_speed_band")
        try:
            ospeed, oband = parse_overrides(a.get("rate_override", ""))
            checks["override_configuration"] = m.get("rate_overrides") == {
                "speed": ospeed, "band": {str(k): v for k, v in oband.items()}}
            expected = np.maximum(float(a["sample_rate"]), np.maximum(
                g.speed.map(ospeed).fillna(0), g.band.map(oband).fillna(0)))
            checks["sample_rates"] = bool(np.isfinite(g.sample_rate).all()
                and g.sample_rate.gt(0).all() and g.sample_rate.le(1).all()
                and np.allclose(expected, g.sample_rate, rtol=0, atol=1e-12))
            u = g.game_id.map(lambda x: hash_unit(str(x)))
            checks["hash_selection"] = bool((u < g.sample_rate).all())
        except (ValueError, KeyError, TypeError):
            checks["sample_rates"] = False
    failed = [k for k, v in checks.items() if not v]
    if failed:
        raise ValidationError("Provenance checks failed: " + ", ".join(failed))
    return g, {"validated": True, "checks": {k: bool(v) for k, v in checks.items()},
               "sha256": digest, "source_month": month, "manifest": m,
               "rows_on_disk": len(g), "date_min": str(dates.min().date()),
               "date_max": str(dates.max().date()),
               "sampling_method": "deterministic MD5 game-ID Bernoulli-style sampling"}


def clean_games(g, month="2025-03", band_by="avg"):
    """Return a copy and exclusion ledger; sequential counts never double-count a row.

    Missing titles mean untitled, not missing observations. Preserve all legitimate
    resignations and games with >=2 plies. Invalid provenance never reaches here.
    """
    g = g.copy()
    missing = set(COLUMNS) - set(g)
    if missing:
        raise ValidationError(f"Missing columns: {sorted(missing)}")
    dates = pd.to_datetime(g.utc_date, format="%Y-%m-%d", errors="coerce")
    we, be = (pd.to_numeric(g[c], errors="coerce") for c in ("white_elo", "black_elo"))
    r = {"avg": (we + be) // 2, "min": np.minimum(we, be), "max": np.maximum(we, be)}[band_by]
    expected_band = np.array(BANDS)[np.clip(np.searchsorted(BANDS, r, side="right") - 1, 0, len(BANDS)-1)]
    rates = pd.to_numeric(g.sample_rate, errors="coerce")
    rules = {
        "missing_game_id": g.game_id.isna() | g.game_id.eq(""),
        "duplicate_id_after_first": g.game_id.duplicated(),
        "invalid_ratings": ~np.isfinite(we) | ~np.isfinite(be) | we.le(0) | be.le(0)
                            | we.mod(1).ne(0) | be.mod(1).ne(0),
        "invalid_result": ~g.result.isin(RESULTS),
        "invalid_date_or_month": dates.isna() | dates.dt.strftime("%Y-%m").ne(month) | g.source_month.ne(month),
        "invalid_speed": ~g.speed.isin(["blitz", "rapid", "classical"]),
        "inconsistent_band": g.band.ne(expected_band),
        "invalid_sample_rate": ~np.isfinite(rates) | rates.le(0) | rates.gt(1),
        "bot": g.white_title.eq("BOT") | g.black_title.eq("BOT"),
        "invalid_termination": ~g.termination.isin(["Normal", "Time forfeit"]),
        "too_few_plies": pd.to_numeric(g.n_plies, errors="coerce").fillna(0).lt(2),
        "missing_first_move": g.first_move.isna() | g.first_move.eq(""),
        "missing_black_reply": g.black_reply.isna() | g.black_reply.eq(""),
        "missing_player": g.white.isna() | g.black.isna() | g.white.eq("") | g.black.eq(""),
        "same_player": g.white.str.lower().eq(g.black.str.lower()),
        "inconsistent_forfeit_flag": g.time_forfeit.ne(g.termination.eq("Time forfeit")),
    }
    remaining = pd.Series(True, index=g.index)
    ledger = []
    for name, bad in rules.items():
        bad = pd.Series(bad, index=g.index).fillna(True)
        ledger.append({"rule": name, "flagged": int(bad.sum()), "excluded": int((bad & remaining).sum())})
        remaining &= ~bad
    out = g.loc[remaining].copy()
    out["elo_difference"] = out.white_elo - out.black_elo
    out["rating_gap"] = pd.cut(out.elo_difference.abs(), [-1, 25, 100, np.inf],
                                labels=["near_equal_0_25", "moderate_26_100", "large_over_100"])
    out["white_score"] = out.result.map({"1-0": 1., "1/2-1/2": .5, "0-1": 0.})
    out["weight"] = 1. / out.sample_rate
    return out, {"input_rows": len(g), "retained_rows": len(out),
                 "excluded_total": int((~remaining).sum()), "rules": ledger}
