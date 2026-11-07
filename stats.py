"""Estimation: score, CIs, family derivation, contrasts, Q2 ranges."""
import numpy as np
import pandas as pd

FAMILIES = ["open", "semi_open", "closed", "semi_closed", "flank"]


def score_ci(W, D, B, z=1.96):
    """White score s=(W+D/2)/N with a normal CI from the per-game variance of {1, .5, 0}.
    (Trinomial outcome: a Wilson interval on a 'win-equivalent rate' is not exactly right.)"""
    W, D, B = (pd.Series(x, dtype=float) if not isinstance(x, pd.Series) else x.astype(float)
               for x in (W, D, B))
    N = W + D + B
    s = (W + 0.5 * D) / N
    var = (W + 0.25 * D) / N - s ** 2
    se = np.sqrt(var / N)
    return pd.DataFrame(dict(N=N, score=s, se=se, lo=s - z * se, hi=s + z * se,
                             draw_rate=D / N, z_vs_half=(s - 0.5) / se))


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
