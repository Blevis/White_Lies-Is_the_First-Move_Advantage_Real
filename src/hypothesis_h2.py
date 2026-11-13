"""March-specific H2 orchestration; reuses the existing multinomial spread test."""
import numpy as np
import pandas as pd
from scipy.stats import norm

from .h2 import spread_test
from .hypothesis_h1 import N_SIM, SEED, dyadic_covariance
from .stats import benjamini_hochberg, multinomial_score_interval

MIN_N_REPLY_MARCH = 200
MIN_BAND_MARCH = 1200
REPRESENTATIVE_CELLS = [("e4", "blitz", 1600), ("d4", "blitz", 1600)]


def group_replies(g):
    selected = g[g.first_move.isin(["e4", "d4"])].copy()
    if selected.black_reply.isna().any() or selected.game_id.duplicated().any():
        raise ValueError("reply grouping requires unique games with nonmissing replies")
    if (~selected.result.isin(["1-0", "1/2-1/2", "0-1"])).any():
        raise ValueError("invalid result")
    selected = selected.rename(columns={"first_move": "first", "black_reply": "reply"})
    groups = selected.groupby(["first", "speed", "band", "reply", "result"], observed=True).size()
    out = groups.unstack("result", fill_value=0).reindex(columns=["1-0", "1/2-1/2", "0-1"], fill_value=0)
    out = out.rename(columns={"1-0": "W", "1/2-1/2": "D", "0-1": "B"}).reset_index()
    if int(out[list("WDB")].to_numpy().sum()) != len(selected):
        raise AssertionError("reply groups do not partition selected games")
    return out


def analyze_replies(g, min_n=MIN_N_REPLY_MARCH, min_band=MIN_BAND_MARCH,
                    n_sim=N_SIM, seed=SEED, contrasts=True):
    replies = group_replies(g)
    rows, tabs = [], []
    for (fm, sp, band), all_replies in replies.groupby(["first", "speed", "band"], sort=True):
        all_replies = all_replies.copy()
        all_replies["N"] = all_replies[list("WDB")].sum(axis=1)
        eligible = all_replies.N.ge(min_n) & (band >= min_band)
        cell = all_replies.loc[eligible]
        tested = len(cell) >= 2
        total = int(all_replies.N.sum())
        used = int(cell.N.sum()) if tested else 0
        r = dict(first=fm, speed=sp, band=band, total_games=total, eligible_replies=int(eligible.sum()),
                 included_games=used, coverage=used/total, min_n=min_n,
                 status="tested" if tested else "insufficient")
        if tested:
            r.update(spread_test(cell, n_sim=n_sim, seed=seed))
        rows.append(r)
        # Record all replies, including those not eligible. Sparse replies are flagged
        # and get conservative bounds; eligible replies get 10,000 bootstrap replicates.
        for index, reply in all_replies.iterrows():
            W, D, B = (int(reply[c]) for c in "WDB")
            ci = multinomial_score_interval(W, D, B, n_sim=n_sim, seed=seed)
            row = dict(first=fm, speed=sp, band=band, reply=reply.reply, W=W, D=D, B=B,
                       N=W+D+B, draw_rate=D/(W+D+B), eligible=bool(eligible.loc[index]),
                       tested=tested and bool(eligible.loc[index]), **ci)
            if tested and eligible.loc[index]:
                rest = cell[cell.reply.ne(reply.reply)][list("WDB")].sum()
                nr = int(rest.sum())
                rest_score = (rest.W+.5*rest.D)/nr
                row["rest_score"] = rest_score
                row["difference_from_rest_pp"] = 100*(ci["score"]-rest_score)
                # Disjoint reply versus remaining eligible games; not versus an
                # overlapping pooled sample. Independent-game descriptive CI.
                vr = max(0., (rest.W+.25*rest.D)/nr-rest_score**2)/nr
                se = np.sqrt(ci["se"]**2+vr)
                row["difference_rest_lo_pp"] = 100*(ci["score"]-rest_score-1.96*se)
                row["difference_rest_hi_pp"] = 100*(ci["score"]-rest_score+1.96*se)
            tabs.append(row)
    summary, scores = pd.DataFrame(rows), pd.DataFrame(tabs)
    if summary.empty:
        return summary, scores
    for p, q in [("p_sd", "q_score"), ("p_distribution", "q_distribution")]:
        if p not in summary:
            summary[p] = np.nan
        summary[q] = benjamini_hochberg(summary[p])
    summary["reject_score"] = summary.q_score.lt(.05)
    summary["reject_distribution"] = summary.q_distribution.lt(.05)
    # Dependence sensitivity for the two prespecified representative cells.
    # Fixed-sample score contrasts use a dyadic sandwich Wald test.
    if contrasts:
        for fm, sp, b in REPRESENTATIVE_CELLS:
            mask = summary["first"].eq(fm) & summary.speed.eq(sp) & summary.band.eq(b)
            if not mask.any() or summary.loc[mask, "status"].iloc[0] != "tested":
                continue
            names = scores.loc[(scores["first"] == fm)&(scores.speed == sp)&(scores.band == b)&scores.tested, "reply"].tolist()
            sub = g[(g.first_move == fm)&(g.speed == sp)&(g.band == b)&g.black_reply.isin(names)]
            cluster = clustered_reply_test(sub, names)
            for key, val in cluster.items():
                summary.loc[mask, key] = val
    return summary, scores


def clustered_reply_test(g, names):
    """Exploratory Wald sensitivity of score equality, clustering by either player."""
    from scipy.stats import chi2
    means = g.groupby("black_reply").white_score.mean().reindex(names).to_numpy()
    n = g.black_reply.value_counts().reindex(names).to_numpy()
    indicator = np.column_stack([g.black_reply.eq(r).to_numpy(float) for r in names])
    u = indicator*(g.white_score.to_numpy()[:, None]-means)/n
    cov = dyadic_covariance(u, g.white, g.black)
    contrast = np.column_stack([np.ones(len(names)-1), -np.eye(len(names)-1)])
    diff = contrast@means
    vc = contrast@cov@contrast.T
    if np.linalg.eigvalsh(vc).min() <= 0:
        return {"dyadic_status": "nonpositive_covariance"}
    stat = float(diff@np.linalg.solve(vc, diff))
    return {"dyadic_status": "exploratory", "dyadic_wald": stat,
            "dyadic_p": float(chi2.sf(stat, len(names)-1))}


def simulate_spreads(cell, n_sim=N_SIM, seed=SEED):
    """Return draws only for plotting the prespecified representative nulls."""
    from .h2 import _wsd
    counts = cell[list("WDB")].to_numpy(np.int64)
    sizes = counts.sum(axis=1)
    p = counts.sum(axis=0)/counts.sum()
    rng = np.random.default_rng(seed)
    sims = np.stack([rng.multinomial(int(n), p, size=n_sim) for n in sizes], axis=1)
    return _wsd(sizes.astype(float), (sims[:, :, 0]+.5*sims[:, :, 1])/sizes)
