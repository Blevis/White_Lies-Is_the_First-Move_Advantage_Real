"""H2 -- does Black's first reply matter?  Reply-level analysis after 1.e4 and 1.d4.

Unit of analysis = the individual Black reply (1...c5, 1...e5, 1...Nf6, ...). Replies to a given
first move are DISJOINT (every game has exactly one), so counts may be compared directly; this is
the "individual reply, not overlapping opening family" design the README commits to.

Null model ("spread test"): within one (first move, speed, rating band) cell, all replies share the
same outcome distribution -- the pooled (W, D, B) mix of the cell, so the draw rate is preserved.
Each reply i is re-drawn as Multinomial(N_i, pooled mix); the statistic is the N-weighted standard
deviation of reply scores (and the min-max range). p = (1 + #{sim >= obs}) / (n_sim + 1).

With explorer-scale N the null spread is ~0, so p is always ~1/(n_sim+1) and says almost nothing.
The informative output is the effect size: `sd_obs`, the noise-free `sd_excess` (sqrt(sd_obs^2 -
mean sim sd^2)) and `range_obs`, in score points. Judge those, not p.

Two data paths feed the same test:
  * collect_replies()      -- optional verified Explorer aggregates,
  * replies_from_games()   -- individual game records (parquet or csv) from fetch_games.py: a
    deterministic hash sample of ONE whole monthly dump, with resignations kept and BOT games
    excluded. The sampling rate depends only on (speed, band), so it is constant inside every
    cell and the spread test needs no weighting. The validated March sample is the primary
    study; absolute scores pooled across cells require sampling weights.
"""
import pathlib
import numpy as np
import pandas as pd

try:
    from . import stats as S
    from .explorer import RATINGS, SPEEDS, SINCE, UNTIL
except ImportError:  # flat layout (notebook adds src/ to sys.path)
    import stats as S
    from explorer import RATINGS, SPEEDS, SINCE, UNTIL

FIRST_MOVES = {"e4": "e2e4", "d4": "d2d4"}
MIN_BAND = 1200          # same fixed config as Q1/Q2
MIN_N_REPLY = 10_000     # per-reply floor on the explorer path; EXTENSION of the fixed MIN_N,
                         # register it with the team before looking at H2 results
N_SIM = 10_000
TOP_REPLIES = 12         # explorer returns the most common continuations; rest -> "_other"


# ----------------------------------------------------------------------------- collection
def collect_replies(ex, first_moves=FIRST_MOVES, speeds=SPEEDS, ratings=RATINGS,
                    min_band=MIN_BAND, since=SINCE, until=UNTIL, top=TOP_REPLIES,
                    out="data/raw/explorer_replies.csv", verbose=True):
    """Long df: first, speed, band, reply(SAN), uci, W, D, B, since, until.

    One request per (first move, speed, band): 2 x 4 x 7 = 56 at the default config. Replies
    outside the top-N are pooled as '_other' (position total minus listed moves), so each
    cell sums to the position total; '_other' is never tested."""
    rows, bands = [], [b for b in ratings if b >= min_band]
    for sp in speeds:
        for r in bands:
            for fm, play in first_moves.items():
                d = ex.get(play, sp, str(r), since=since, until=until, moves=top)
                tot = np.array([d["white"], d["draws"], d["black"]])
                listed = np.zeros(3, dtype=np.int64)
                for m in d.get("moves", []):
                    wdb = np.array([m["white"], m["draws"], m["black"]])
                    listed += wdb
                    rows.append(dict(first=fm, speed=sp, band=r, reply=m["san"], uci=m["uci"],
                                     W=wdb[0], D=wdb[1], B=wdb[2], since=since, until=until))
                rest = tot - listed
                if (rest < 0).any():
                    raise AssertionError(f"listed replies exceed position total: {fm} {sp} {r}")
                rows.append(dict(first=fm, speed=sp, band=r, reply="_other", uci="",
                                 W=rest[0], D=rest[1], B=rest[2], since=since, until=until))
        if verbose:
            print(f"replies {sp}: {len(rows)} rows (HTTP so far: {ex.n_http})")
    df = pd.DataFrame(rows)
    if out:
        pathlib.Path(out).parent.mkdir(parents=True, exist_ok=True)
        df.to_csv(out, index=False)
    return df


def replies_from_games(games_path="data/games.parquet", min_band=MIN_BAND):
    """Individual game records (fetch_games.py output, .parquet or .csv) -> the same long format.
    Uses `first_move` / `black_reply`; keeps only games starting 1.e4 / 1.d4 that have a reply;
    BOT games are excluded. See module caveat before using."""
    cols = ["speed", "band", "result", "first_move", "black_reply", "white_title", "black_title"]
    path = str(games_path)
    g = pd.read_parquet(path, columns=cols) if path.endswith(".parquet") else pd.read_csv(path, usecols=cols)
    g = g[(g.white_title != "BOT") & (g.black_title != "BOT")]
    g = g.rename(columns={"first_move": "first", "black_reply": "reply"})
    g = g[g["first"].isin(FIRST_MOVES) & g.reply.notna() & (g.band >= min_band)]
    for col, val in (("W", "1-0"), ("D", "1/2-1/2"), ("B", "0-1")):
        g[col] = (g.result == val).astype(int)
    return (g.groupby(["first", "speed", "band", "reply"], as_index=False)[["W", "D", "B"]].sum())


# ----------------------------------------------------------------------------- statistics
def reply_table(cell, z=1.96):
    """Per-reply score and CI plus difference from the cell's pooled score (reply vs rest-of-cell
    would be exact; vs pooled is shown because it is what the null model uses)."""
    est = S.score_ci(cell.W, cell.D, cell.B).reset_index(drop=True)
    out = pd.concat([cell[["first", "speed", "band", "reply"]].reset_index(drop=True), est], axis=1)
    W, D, B = cell.W.sum(), cell.D.sum(), cell.B.sum()
    pooled = (W + D / 2) / (W + D + B)
    out["pooled"] = pooled
    out["diff"] = out.score - pooled
    return out


def _wsd(n, s):
    """N-weighted SD of scores; works on (k,) or (n_sim, k) arrays."""
    m = (n * s).sum(-1, keepdims=True) / n.sum(-1, keepdims=True)
    return np.sqrt((n * (s - m) ** 2).sum(-1) / n.sum(-1))


def spread_test(cell, n_sim=N_SIM, seed=0):
    """Simulated spread test for ONE cell (rows = disjoint replies with W, D, B). -> dict."""
    arr = cell[list("WDB")].to_numpy(dtype=float)
    if np.any(~np.isfinite(arr) | (arr < 0) | (arr % 1 != 0)):
        raise ValueError("counts must be finite nonnegative integers")
    W, D, B = arr.astype(np.int64).T
    N = W + D + B
    if len(N) < 2:
        raise ValueError("need >= 2 replies")
    if (N <= 0).any() or n_sim < 2:
        raise ValueError("positive reply totals and >=2 simulations required")
    p = np.array([W.sum(), D.sum(), B.sum()], dtype=float)
    p /= p.sum()                                    # pooled mix => draw rate preserved under H0
    rng = np.random.default_rng(seed)
    sim = np.stack([rng.multinomial(n, p, size=n_sim) for n in N], axis=1)  # (n_sim, k, 3)
    s_sim = (sim[..., 0] + 0.5 * sim[..., 1]) / N                           # (n_sim, k)
    s_obs = (W + 0.5 * D) / N
    nf = N.astype(float)
    sd_obs, sd_sim = _wsd(nf, s_obs), _wsd(nf, s_sim)
    rg_obs, rg_sim = s_obs.max() - s_obs.min(), s_sim.max(1) - s_sim.min(1)
    expected = N[:, None]*p
    chi_obs = np.sum(np.divide((arr-expected)**2, expected,
                              out=np.zeros_like(expected), where=expected > 0))
    # Refit the shared outcome mix for each simulated table: nuisance parameters
    # are estimated in the same way for observed and null Pearson statistics.
    pooled_sim = sim.sum(axis=1)/N.sum()
    exp_sim = N[None, :, None]*pooled_sim[:, None, :]
    chi_sim = np.sum(np.divide((sim-exp_sim)**2, exp_sim,
                              out=np.zeros_like(exp_sim), where=exp_sim > 0), axis=(1, 2))
    return dict(k=len(N), N=int(N.sum()), pooled=float(p[0] + p[1] / 2),
                sd_obs=float(sd_obs), sd_null_mean=float(sd_sim.mean()),
                sd_null_q95=float(np.quantile(sd_sim, .95)),
                sd_excess=float(np.sqrt(max(0.0, sd_obs ** 2 - (sd_sim ** 2).mean()))),
                range_obs=float(rg_obs), range_null_q95=float(np.quantile(rg_sim, .95)),
                best=cell.reply.iloc[int(s_obs.argmax())], worst=cell.reply.iloc[int(s_obs.argmin())],
                p_sd=float((1 + (sd_sim >= sd_obs).sum()) / (n_sim + 1)),
                p_range=float((1 + (rg_sim >= rg_obs-1e-14).sum()) / (n_sim + 1)),
                chi2_observed=float(chi_obs),
                p_distribution=float((1 + (chi_sim >= chi_obs-1e-14).sum())/(n_sim+1)), n_sim=n_sim)


def run_h2(replies, min_n=MIN_N_REPLY, min_band=MIN_BAND, n_sim=N_SIM, seed=0):
    """Spread test per (first, speed, band) cell. '_other' and replies with N < min_n are
    excluded; cells left with < 2 replies are skipped. Returns (summary, per-reply table)."""
    df = replies[(replies.reply != "_other") & (replies.band >= min_band)].copy()
    df = df[(df.W + df.D + df.B) >= min_n]
    summ, tabs = [], []
    for (fm, sp, b), cell in df.groupby(["first", "speed", "band"]):
        if len(cell) < 2:
            continue
        r = spread_test(cell, n_sim=n_sim, seed=seed)
        summ.append(dict(first=fm, speed=sp, band=b, **r))
        tabs.append(reply_table(cell))
    return pd.DataFrame(summ), (pd.concat(tabs, ignore_index=True) if tabs else pd.DataFrame())


def coverage(replies, min_n=MIN_N_REPLY):
    """Share of each cell's games that enters the test (tested replies / cell total)."""
    r = replies.assign(N=replies.W + replies.D + replies.B)
    r["tested"] = (r.reply != "_other") & (r.N >= min_n)
    r["included"] = r.N.where(r.tested, 0)
    g = r.groupby(["first", "speed", "band"])[["N", "included"]].sum()
    return (g.included/g.N.replace(0, np.nan)).rename("coverage").reset_index()
