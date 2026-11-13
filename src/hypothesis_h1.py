"""Sampling-aware H1 estimates, null simulations and score adjustment.

The primary estimand is a ratio of inverse-inclusion-probability totals. Counts
are compressed by sampling stratum/outcome, never expanded to population totals.
"""
import numpy as np
import pandas as pd
from scipy.stats import binomtest, norm

from .stats import benjamini_hochberg, outcome_metrics, multinomial_score_interval

SEED = 202503
N_SIM = 10000
MIN_N = 200


def stratum_counts(g, weighted=True):
    if not len(g):
        return np.empty((0, 3), dtype=int), np.array([]), np.array([])
    rates = g.groupby(["speed", "band"], observed=True).sample_rate.nunique()
    if (rates != 1).any():
        raise ValueError("sample rate must be constant within each speed/band stratum")
    c = (g.groupby(["speed", "band", "sample_rate", "result"], observed=True)
         .size().unstack("result", fill_value=0).reindex(columns=["1-0", "1/2-1/2", "0-1"], fill_value=0))
    p = c.index.get_level_values("sample_rate").to_numpy(float)
    if np.any(~np.isfinite(p) | (p <= 0) | (p > 1)):
        raise ValueError("invalid sample rates")
    return c.to_numpy(np.int64), (1/p if weighted else np.ones(len(p))), p


def h1_test(g, weighted=True, n_sim=N_SIM, seed=SEED):
    if n_sim < 2:
        raise ValueError("need at least two simulations")
    # Also validates outcome labels rather than quietly losing invalid records.
    raw = outcome_metrics(g.result)
    counts, weights, rates = stratum_counts(g, weighted)
    n = len(g)
    if not n:
        return dict(N=0, score=np.nan, lo=np.nan, hi=np.nan, se=np.nan,
                    p_mc=np.nan, p_exact_unweighted=np.nan, status="insufficient")
    totals = counts.sum(axis=1)
    den = float(totals @ weights)
    obs = float((counts @ np.array([1., .5, 0.])) @ weights / den)
    rng = np.random.default_rng(seed)
    # Poisson(1) multipliers on individual observations are equivalent to independent
    # Poisson(count) draws on these sufficient statistics. sqrt(1-p) is the
    # Bernoulli-sampling FPC; variable stratum masses enter numerator AND denominator.
    boot_num = np.zeros(n_sim)
    boot_den = np.zeros(n_sim)
    null_num = np.zeros(n_sim)
    for c, w, p in zip(counts, weights, rates):
        mult = rng.poisson(c, size=(n_sim, 3))
        factor = np.sqrt(1-p) if weighted else 1.
        boot = c + factor * (mult-c)
        boot_num += w*(boot[:, 0]+.5*boot[:, 1])
        boot_den += w*boot.sum(axis=1)
        d = c[1]/c.sum()
        null = rng.multinomial(int(c.sum()), [(1-d)/2, d, (1-d)/2], size=n_sim)
        null_num += w*(null[:, 0]+.5*null[:, 1])
    boot_scores = boot_num[boot_den > 0]/boot_den[boot_den > 0]
    null_scores = null_num/den
    lo, hi = np.quantile(boot_scores, [.025, .975])
    eligible = n >= MIN_N and raw["W"]+raw["B"] >= 20
    if not eligible or np.count_nonzero(counts.sum(axis=0)) < 2:
        if np.ptp(weights) == 0:
            ci = multinomial_score_interval(raw["W"], raw["D"], raw["B"], n_sim, seed)
            lo, hi = ci["lo"], ci["hi"]
        else:
            lo, hi = 0., 1.  # do not pretend a sparse weighted group is precise
    p_mc = float((1+np.sum(null_scores >= obs-1e-14))/(n_sim+1))
    # A moment-based design Wald check tests the weaker pooled-mean null without
    # requiring color symmetry in every stratum (as the null simulation does).
    fpc = 1-rates if weighted else np.ones(len(rates))
    variance = float(np.sum(counts*(np.array([1., .5, 0.])-obs)**2
                              * (fpc*weights**2)[:, None])/den**2)
    design_se = np.sqrt(variance)
    exact = float(binomtest(int(raw["W"]), int(raw["W"]+raw["B"]), .5,
                           alternative="greater").pvalue) if raw["W"]+raw["B"] else 1.
    metrics = outcome_metrics(g.result, 1/g.sample_rate if weighted else None)
    return dict(N=n, score=obs, lo=float(lo), hi=float(hi), se=float(boot_scores.std(ddof=1)),
                difference_pp=100*(obs-.5), weight_total=den,
                effective_n=float(den**2/(totals @ weights**2)),
                white_wins=int(raw["W"]), draws=int(raw["D"]), black_wins=int(raw["B"]),
                draw_rate=metrics["draw_rate"], white_win_rate=metrics["white_win_rate"],
                black_win_rate=metrics["black_win_rate"],
                decisive_white_win_rate=metrics["decisive_white_win_rate"],
                p_mc=p_mc if eligible else np.nan, p_exact_unweighted=exact if eligible else np.nan,
                design_se=float(design_se),
                p_wald_design=float(norm.sf((obs-.5)/design_se)) if eligible and design_se > 0 else np.nan,
                exact_applies_to_estimate=bool(np.ptp(weights) == 0),
                null_mean=float(null_scores.mean()), null_sd=float(null_scores.std(ddof=1)),
                test_statistic=obs, z_null=float((obs-.5)/null_scores.std(ddof=1)) if null_scores.std(ddof=1) > 0 else np.nan,
                weighted=weighted, n_sim=n_sim, seed=seed,
                status="tested" if eligible else "insufficient")


def run_h1(g, n_sim=N_SIM, seed=SEED):
    rows = [dict(group="Overall (primary weighted)", group_type="primary", speed="all", band=-1,
                 **h1_test(g, n_sim=n_sim, seed=seed))]
    for cols, kind in [(["speed"], "speed"), (["band"], "band"), (["speed", "band"], "cell")]:
        for keys, cell in g.groupby(cols, observed=True, sort=True):
            keys = keys if isinstance(keys, tuple) else (keys,)
            meta = dict(zip(cols, keys))
            label = "/".join(str(x) for x in keys)
            rows.append(dict(group=label, group_type=kind, speed=meta.get("speed", "all"),
                             band=meta.get("band", -1), **h1_test(cell, n_sim=n_sim, seed=seed)))
    out = pd.DataFrame(rows)
    out["p_adjusted"] = np.nan
    family = (out.group_type != "primary") & (out.status == "tested")
    out.loc[family, "p_adjusted"] = benjamini_hochberg(out.loc[family, "p_mc"])
    out.loc[out.group_type == "primary", "p_adjusted"] = out.loc[out.group_type == "primary", "p_mc"]
    out["reject"] = out.p_adjusted.lt(.05) & out.score.gt(.5)
    out["interpretation"] = np.where(out.status != "tested", "Insufficient data",
                           np.where(out.reject, "Score above 50% detected", "Above-50% evidence insufficient"))
    return out


def dyadic_covariance(influence, white, black):
    """Shared-player sandwich: sum vertex totals squared minus unordered-pair totals.

    Each game contributes to both players, including players switching colors.
    Subtracting the unordered-pair term counts covariance within a repeated pair
    once. Assumes independence for games with no shared player; sensitivity only.
    Influence must already include inverse bread if regression-adjusted.
    """
    u = np.asarray(influence, dtype=float)
    if u.ndim == 1:
        u = u[:, None]
    w = pd.Series(np.asarray(white)).str.lower()
    b = pd.Series(np.asarray(black)).str.lower()
    if w.isna().any() or b.isna().any() or w.eq(b).any():
        raise ValueError("dyadic covariance requires distinct, nonmissing endpoints")
    codes, players = pd.factorize(pd.concat([w, b], ignore_index=True), sort=False)
    wc, bc = codes[:len(w)], codes[len(w):]
    pair_index = pd.MultiIndex.from_arrays([np.minimum(wc, bc), np.maximum(wc, bc)])
    pc, pairs = pd.factorize(pair_index, sort=False)
    vertices = np.column_stack([np.bincount(wc, u[:, j], minlength=len(players))
                               + np.bincount(bc, u[:, j], minlength=len(players)) for j in range(u.shape[1])])
    edges = np.column_stack([np.bincount(pc, u[:, j], minlength=len(pairs)) for j in range(u.shape[1])])
    return vertices.T @ vertices - edges.T @ edges


def clustered_score(g):
    w = g.weight.to_numpy(float)
    y = g.white_score.to_numpy(float)
    score = float(np.average(y, weights=w))
    influence = w*(y-score)/w.sum()
    variance = float(dyadic_covariance(influence, g.white, g.black)[0, 0])
    if variance <= 0:
        return dict(score=score, status="nonpositive_dyadic_variance", N=len(g))
    se = np.sqrt(variance)
    return dict(score=score, se=float(se), lo=float(score-1.96*se), hi=float(score+1.96*se),
                p_one_sided=float(norm.sf((score-.5)/se)), N=len(g),
                unique_players=int(pd.concat([g.white, g.black]).str.lower().nunique()),
                status="sensitivity")


def rating_adjustment(g):
    """Weighted score regression standardized to equal rating within speed/band.

    A natural cubic spline handles nonlinear rating imbalance; a score mean model
    is valid for 0/.5/1 outcomes without collapsing draws into binary outcomes.
    Covariance uses shared-player dyadic influence functions. Small cells omitted.
    """
    from patsy import dmatrix, build_design_matrices
    g = g.copy()
    g["cell"] = g.speed + "/" + g.band.astype(str)
    counts = g.cell.value_counts()
    g = g[g.cell.isin(counts[counts >= MIN_N].index)].copy()
    design = dmatrix("0 + C(cell) + cr(elo_difference, knots=(-200,-50,0,50,200), constraints='center')",
                     g, return_type="dataframe")
    x = np.asarray(design)
    w, y = g.weight.to_numpy(float), g.white_score.to_numpy(float)
    bread = np.linalg.pinv(x.T @ (w[:, None]*x))
    beta = bread @ (x.T @ (w*y))
    resid = y-x@beta
    counter = g[["cell", "weight"]].groupby("cell", as_index=False).weight.sum()
    counter["elo_difference"] = 0.
    x0 = np.asarray(build_design_matrices([design.design_info], counter)[0])
    target = np.average(x0, axis=0, weights=counter.weight)
    score = float(target@beta)
    # Only scalar contrast influences are required, avoiding a large covariance matrix.
    influence = w*resid*(x@(bread@target))
    variance = float(dyadic_covariance(influence, g.white, g.black)[0, 0])
    se = float(np.sqrt(max(0., variance)))
    predictions = x@beta
    summary = dict(N=len(g), omitted_sparse_rows=int(counts.sum()-len(g)), score=score, se=se,
                   lo=score-1.96*se, hi=score+1.96*se,
                   p_one_sided=float(norm.sf((score-.5)/se)) if se > 0 else None,
                   model="IPW score mean regression: speed-band intercepts + natural cubic rating-difference spline",
                   standardization="elo_difference=0, observed IPW speed-band composition",
                   covariance="dyadic shared-player sandwich", rank=int(np.linalg.matrix_rank(x.T@x)),
                   parameters=x.shape[1], outside_unit_interval=int(((predictions < 0)|(predictions > 1)).sum()))
    coefficients = pd.DataFrame({"term": design.columns, "coefficient": beta})
    return summary, coefficients
