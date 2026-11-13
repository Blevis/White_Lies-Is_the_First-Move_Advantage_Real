"""Estimation: score, CIs, family derivation, contrasts, Q2 ranges."""
import numpy as np
import pandas as pd

FAMILIES = ["open", "semi_open", "closed", "semi_closed", "flank"]


def score_ci(W, D, B, z=1.96):
    """White score s=(W+D/2)/N with a normal CI from the per-game variance of {1, .5, 0}.
    (Trinomial outcome: a Wilson interval on a 'win-equivalent rate' is not exactly right.)"""
    W, D, B = (pd.Series(x, dtype=float) if not isinstance(x, pd.Series) else x.astype(float)
               for x in (W, D, B))
    if any((~np.isfinite(x) | (x < 0)).any() for x in (W, D, B)):
        raise ValueError("outcome counts must be finite and nonnegative")
    N = W + D + B
    den = N.replace(0, np.nan)
    s = (W + 0.5 * D) / den
    var = ((W + 0.25 * D) / den - s ** 2).clip(lower=0)
    se = np.sqrt(var / (N - 1).where(N > 1))
    return pd.DataFrame(dict(N=N, score=s, se=se, lo=(s - z * se).clip(0, 1),
                             hi=(s + z * se).clip(0, 1), draw_rate=D / den,
                             z_vs_half=(s - 0.5) / se.replace(0, np.nan)))


def inverse_probability_weights(rates):
    rates = np.asarray(rates, dtype=float)
    if np.any(~np.isfinite(rates) | (rates <= 0) | (rates > 1)):
        raise ValueError("sampling probabilities must be finite and in (0,1]")
    return 1. / rates


def outcome_metrics(results, weights=None):
    """Empirical score, outcome rates and decisive win rate; empty means are NaN."""
    results = pd.Series(results)
    if not results.isin(["1-0", "1/2-1/2", "0-1"]).all():
        raise ValueError("invalid game outcome")
    w = np.ones(len(results)) if weights is None else np.asarray(weights, dtype=float)
    if len(w) != len(results) or np.any(~np.isfinite(w) | (w <= 0)):
        raise ValueError("weights must be positive, finite and match outcomes")
    W, D, B = (float(w[results.eq(r).to_numpy()].sum()) for r in ["1-0", "1/2-1/2", "0-1"])
    n = W + D + B
    return dict(N=len(results), weight_total=n, W=W, D=D, B=B,
                score=(W + D / 2) / n if n else np.nan,
                white_win_rate=W / n if n else np.nan, draw_rate=D / n if n else np.nan,
                black_win_rate=B / n if n else np.nan,
                decisive_white_win_rate=W / (W + B) if W + B else np.nan)


def benjamini_hochberg(p_values):
    """BH adjusted p-values; NaN positions are outside the tested family."""
    p = np.asarray(p_values, dtype=float)
    valid = np.isfinite(p)
    if ((p[valid] < 0) | (p[valid] > 1)).any():
        raise ValueError("p-values must be in [0,1]")
    out = np.full(p.shape, np.nan)
    v = p[valid]
    if len(v):
        order = np.argsort(v)
        q = np.minimum.accumulate((v[order] * len(v) / np.arange(1, len(v)+1))[::-1])[::-1]
        q_unsorted = np.empty_like(q)
        q_unsorted[order] = np.minimum(q, 1)
        out[valid] = q_unsorted
    return out


def multinomial_score_interval(W, D, B, n_sim=10000, seed=202503):
    """Independent-game percentile bootstrap for an unweighted three-outcome score.

    Below N=200 or at a degenerate empirical distribution, use a conservative
    simultaneous Clopper–Pearson bound on P(W) and P(B), then S=(1+P(W)-P(B))/2.
    This avoids zero-width intervals for tiny/constant samples.
    """
    from scipy.stats import beta
    counts = np.asarray([W, D, B], dtype=float)
    if np.any(~np.isfinite(counts) | (counts < 0) | (counts % 1 != 0)):
        raise ValueError("bootstrap requires nonnegative integer counts")
    n = int(counts.sum())
    if not n:
        return dict(score=np.nan, lo=np.nan, hi=np.nan, se=np.nan)
    score = (W + D/2) / n
    if n < 200 or np.count_nonzero(counts) < 2:
        # Two two-sided 97.5% intervals give >=95% simultaneous coverage.
        def cp(k):
            return (0. if k == 0 else beta.ppf(.0125, k, n-k+1),
                    1. if k == n else beta.ppf(.9875, k+1, n-k))
        wl, wh = cp(W)
        bl, bh = cp(B)
        return dict(score=score, lo=max(0., (1+wl-bh)/2), hi=min(1., (1+wh-bl)/2),
                    se=float(np.sqrt(max(0., (W+.25*D)/n-score**2)/n)))
    sim = np.random.default_rng(seed).multinomial(n, counts/n, size=n_sim)
    scores = (sim[:, 0] + .5*sim[:, 1]) / n
    lo, hi = np.quantile(scores, [.025, .975])
    return dict(score=float(score), lo=float(lo), hi=float(hi), se=float(scores.std(ddof=1)))


def _g(df, pos):
    return df[df.pos == pos].set_index(["speed", "band"])[["W", "D", "B"]]


def derive_families(df):
    """Long df: family, speed, band, W, D, B. Families are disjoint except 'all'.
    Derived by subtraction of nested positions; asserts counts stay non-negative."""
    fam = {
        "all":         _g(df, "root"),
        "open":        _g(df, "e4e5"),                       # 1.e4 e5
        "semi_open":   _g(df, "e4") - _g(df, "e4e5"),        # 1.e4, not ...e5
        "closed":      _g(df, "d4d5"),                       # 1.d4 d5
        "semi_closed": _g(df, "d4") - _g(df, "d4d5"),        # 1.d4, not ...d5
        "flank":       _g(df, "root") - _g(df, "e4") - _g(df, "d4"),  # everything else
    }
    for k, v in fam.items():
        assert (v >= 0).all().all(), f"negative counts in '{k}': cache/response inconsistency"
    return pd.concat(fam, names=["family"]).reset_index()


def estimate(fam_long):
    est = score_ci(fam_long.W, fam_long.D, fam_long.B)
    return pd.concat([fam_long[["family", "speed", "band"]].reset_index(drop=True),
                      est.reset_index(drop=True)], axis=1)


def q1_table(est):
    return est[est.family == "all"].drop(columns="family").reset_index(drop=True)


def q2_ranges(est, min_band=1200, min_n=10_000):
    """Min-max of White score across rating bands, per (speed, family)."""
    e = est[(est.family != "all") & (est.band >= min_band) & (est.N >= min_n)]
    g = e.groupby(["speed", "family"]).score.agg(["min", "max", "count"])
    g["range"] = g["max"] - g["min"]
    return g.reset_index()


def contrast(est, fa, fb):
    """Score difference fa - fb per (speed, band); valid only for disjoint families."""
    a = est[est.family == fa].set_index(["speed", "band"])
    b = est[est.family == fb].set_index(["speed", "band"])
    d = pd.DataFrame(index=a.index)
    d["diff"] = a.score - b.score
    d["se"] = np.sqrt(a.se ** 2 + b.se ** 2)
    d["lo"], d["hi"] = d["diff"] - 1.96 * d.se, d["diff"] + 1.96 * d.se
    return d.reset_index()
