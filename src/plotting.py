"""Publication-style figures (colorblind palette, color + marker, no in-figure title)."""
import pathlib
import matplotlib as mpl
import matplotlib.pyplot as plt
import seaborn as sns

SINGLE_COL, DOUBLE_COL = 3.5, 7.16
MARKERS = ["o", "s", "^", "D", "v", "P"]
LINES = ["-", "--", "-.", ":", (0, (3, 1, 1, 1)), (0, (5, 1))]


def style():
    mpl.rcParams.update({
        "font.family": "serif", "font.serif": ["Times New Roman", "DejaVu Serif"],
        "mathtext.fontset": "cm", "font.size": 10, "axes.labelsize": 11,
        "legend.fontsize": 9, "xtick.labelsize": 9, "ytick.labelsize": 9,
        "figure.dpi": 150, "savefig.dpi": 300, "xtick.direction": "in",
        "ytick.direction": "in", "axes.grid": True, "grid.alpha": 0.3,
        "grid.linestyle": "--",
    })


def band_label(b):
    return {0: "<1000", 2500: "2500+"}.get(b, str(b))


def _save(fig, name, outdir="figures"):
    pathlib.Path(outdir).mkdir(exist_ok=True)
    fig.savefig(f"{outdir}/{name}.pdf", bbox_inches="tight")
    fig.savefig(f"{outdir}/{name}.png", bbox_inches="tight")


def plot_q1(q1, name="q1_score_by_band", min_band=0):
    style()
    pal = sns.color_palette("colorblind")
    fig, ax = plt.subplots(figsize=(SINGLE_COL * 1.6, SINGLE_COL * 1.1))
    speeds = list(q1.speed.unique())
    for i, sp in enumerate(speeds):
        d = q1[(q1.speed == sp) & (q1.band >= min_band)].sort_values("band")
        x = range(len(d))
        ax.errorbar(x, d.score, yerr=[d.score - d.lo, d.hi - d.score], color=pal[i],
                    marker=MARKERS[i], ls=LINES[i], ms=4, capsize=2, lw=1, label=sp)
    ax.axhline(0.5, color="k", lw=0.8, ls=":")
    ax.set_xticks(list(range(len(d))))
    ax.set_xticklabels([band_label(b) for b in d.band], rotation=30)
    ax.set_xlabel("Rating band (lower bound)")
    ax.set_ylabel("White score $(W + D/2)/N$")
    ax.legend(title="Speed")
    _save(fig, name)
    return fig


def plot_q2(est, fams, name="q2_families_by_band", min_band=1000):
    style()
    pal = sns.color_palette("colorblind")
    speeds = list(est.speed.unique())
    fig, axes = plt.subplots(2, 2, figsize=(DOUBLE_COL, DOUBLE_COL * 0.7), sharey=True)
    for ax, sp in zip(axes.ravel(), speeds):
        for i, f in enumerate(fams):
            d = est[(est.speed == sp) & (est.family == f) & (est.band >= min_band)].sort_values("band")
            x = range(len(d))
            ax.errorbar(x, d.score, yerr=[d.score - d.lo, d.hi - d.score], color=pal[i],
                        marker=MARKERS[i], ls=LINES[i], ms=3.5, capsize=1.5, lw=1, label=f)
        ax.axhline(0.5, color="k", lw=0.8, ls=":")
        ax.set_xticks(list(range(len(d))))
        ax.set_xticklabels([band_label(b) for b in d.band], rotation=30)
        ax.text(0.03, 0.05, sp, transform=ax.transAxes, fontsize=9)
    axes[0, 0].legend(fontsize=7, ncol=1)
    for ax in axes[1]:
        ax.set_xlabel("Rating band")
    for ax in axes[:, 0]:
        ax.set_ylabel("White score")
    fig.tight_layout()
    _save(fig, name)
    return fig


def plot_draw_rate(q1, name="draw_rate_by_band"):
    style()
    pal = sns.color_palette("colorblind")
    fig, ax = plt.subplots(figsize=(SINGLE_COL * 1.6, SINGLE_COL * 1.1))
    for i, sp in enumerate(q1.speed.unique()):
        d = q1[q1.speed == sp].sort_values("band")
        ax.plot(range(len(d)), d.draw_rate, color=pal[i], marker=MARKERS[i], ls=LINES[i], ms=4, label=sp)
    ax.set_xticks(list(range(len(d))))
    ax.set_xticklabels([band_label(b) for b in d.band], rotation=30)
    ax.set_xlabel("Rating band (lower bound)")
    ax.set_ylabel("Draw rate")
    ax.legend(title="Speed")
    _save(fig, name)
    return fig


def study_figures(g, h1, h2, replies, outdir, eda, n_sim=10000, seed=202503):
    """Final March figures. Legacy exploratory artifacts are left untouched."""
    import numpy as np
    import pandas as pd
    from .hypothesis_h2 import REPRESENTATIVE_CELLS, simulate_spreads
    style()
    pal = sns.color_palette("colorblind")
    outdir = pathlib.Path(outdir)

    def save(fig, name):
        fig.tight_layout()
        _save(fig, name, outdir)
        plt.close(fig)

    def interval(ax, table, labels, horizontal=False):
        positions = np.arange(len(table))
        score = table.score.to_numpy()*100
        lo, hi = table.lo.to_numpy()*100, table.hi.to_numpy()*100
        # Percentile intervals can miss the point by tiny Monte Carlo error.
        errors = [np.maximum(0, score-lo), np.maximum(0, hi-score)]
        if horizontal:
            ax.errorbar(score, positions, xerr=errors, fmt="o", color=pal[0], capsize=3, ms=4)
            ax.set_yticks(positions, labels)
            ax.axvline(50, color="0.4", ls=":")
            ax.set_xlabel("White score (%) with marginal 95% CI")
        else:
            ax.errorbar(positions, score, yerr=errors, fmt="o", color=pal[0], capsize=3, ms=5)
            ax.set_xticks(positions, labels)
            ax.axhline(50, color="0.4", ls=":")
            ax.set_ylabel("White score (%) with 95% CI")

    fig, ax = plt.subplots(figsize=(6, 4))
    counts = [g.result.eq(v).sum() for v in ["1-0", "1/2-1/2", "0-1"]]
    ax.bar(["White wins", "Draws", "Black wins"], np.array(counts)/len(g)*100, color=[pal[0], pal[7], pal[1]])
    for i, n in enumerate(counts):
        ax.text(i, n/len(g)*100+.8, f"{n:,}\n{n/len(g):.1%}", ha="center", fontsize=9)
    ax.set_ylim(0, max(counts)/len(g)*100+8)
    ax.set_ylabel("Observed sample games (%)")
    ax.set_title(f"March 2025 sample: N = {len(g):,}")
    save(fig, "fig01_game_outcomes")

    band = h1[h1.group_type == "band"].sort_values("band")
    fig, ax = plt.subplots(figsize=(8.5, 4.5))
    labels = [f"{band_label(int(b))}\nn={int(n):,}" for b, n in zip(band.band, band.N)]
    interval(ax, band, labels)
    ax.set_xlabel("Mean-opponent rating band (lower bound); IPW pooled over speeds")
    save(fig, "fig02_score_by_band")
    speed = h1[h1.group_type == "speed"].sort_values("speed")
    fig, ax = plt.subplots(figsize=(6.5, 4.5))
    interval(ax, speed, [f"{s}\nn={int(n):,}" for s, n in zip(speed.speed, speed.N)])
    ax.set_xlabel("Time control; IPW pooled over rating bands")
    save(fig, "fig03_score_by_speed")

    fig, ax = plt.subplots(figsize=(8, 4.5))
    for i, sp in enumerate(["blitz", "rapid", "classical"]):
        d = h1[(h1.group_type == "cell")&(h1.speed == sp)&(h1.N >= 200)].sort_values("band")
        ax.plot(d.band, d.draw_rate*100, marker=MARKERS[i], color=pal[i], label=sp)
    ax.set_xticks(sorted(g.band.unique()), [band_label(int(b)) for b in sorted(g.band.unique())], rotation=30)
    ax.set_ylabel("Draws (%)")
    ax.set_xlabel("Mean-opponent rating band (lower bound); cells with n ≥ 200")
    ax.legend()
    save(fig, "fig04_draw_rate_by_band")

    fig, ax = plt.subplots(figsize=(8, 4.2))
    ax.hist(g.elo_difference, bins=np.arange(-1500, 1526, 25), color=pal[0], alpha=.8)
    for x, ls in [(0, "-"), (-25, ":"), (25, ":"), (-100, "--"), (100, "--")]:
        ax.axvline(x, color="0.25", ls=ls, lw=.8)
    ax.set_xlabel("White Elo − Black Elo")
    ax.set_ylabel("Observed sampled games")
    ax.text(.02, .95, f"Mean {g.elo_difference.mean():.1f}; median {g.elo_difference.median():.0f}\n"
            f"Within 25 Elo: {g.elo_difference.abs().le(25).mean():.1%}",
            va="top", transform=ax.transAxes)
    save(fig, "fig05_rating_imbalance")

    coverage = g.groupby(["band", "speed"], observed=True).size().unstack().reindex(columns=["blitz", "rapid", "classical"])
    fig, ax = plt.subplots(figsize=(6, 5.5))
    sns.heatmap(np.log10(coverage.clip(lower=1)), annot=coverage.map(lambda n: f"{n:,}"), fmt="",
                cmap="cividis", cbar_kws={"label": "log10 observed games"}, ax=ax)
    ax.set_yticklabels([band_label(int(b)) for b in coverage.index], rotation=0)
    ax.set_xlabel("Time control")
    ax.set_ylabel("Mean-opponent rating band")
    save(fig, "fig06_sample_coverage")

    for fm, name in [("e4", "fig07_replies_e4"), ("d4", "fig08_replies_d4")]:
        fig, axes = plt.subplots(1, 3, figsize=(12.5, 5.2), sharex=True)
        for ax, sp in zip(axes, ["blitz", "rapid", "classical"]):
            d = replies[(replies["first"] == fm)&(replies.band == 1600)&(replies.speed == sp)&replies.tested].sort_values("score")
            if len(d):
                interval(ax, d, [f"{r} (n={n:,})" for r, n in zip(d.reply, d.N)], horizontal=True)
                c = h2[(h2["first"] == fm)&(h2.band == 1600)&(h2.speed == sp)].iloc[0]
                ax.set_title(f"{sp}; coverage {c.coverage:.1%}")
            else:
                ax.text(.5, .5, "Insufficient eligible replies", ha="center", transform=ax.transAxes)
        fig.suptitle(f"After 1.{fm}: mean rating 1600–1799; ≥200 games/reply", fontsize=12)
        save(fig, name)

    fig, axes = plt.subplots(1, 2, figsize=(10.5, 5.4), sharey=True)
    for ax, fm in zip(axes, ["e4", "d4"]):
        d = h2[(h2["first"] == fm)&h2.status.eq("tested")]
        heat = d.pivot(index="band", columns="speed", values="range_obs").reindex(
            index=sorted(g.loc[g.band >= 1200, "band"].unique()), columns=["blitz", "rapid", "classical"])*100
        annotations = heat.map(lambda v: "" if pd.isna(v) else f"{v:.1f}")
        sns.heatmap(heat, annot=annotations, fmt="", cmap="cividis", vmin=0, vmax=h2.range_obs.max()*100,
                    cbar_kws={"label": "Max − min eligible White score (pp)"}, ax=ax)
        ax.set_title(f"After 1.{fm}; blank = insufficient")
        ax.set_xlabel("Time control")
        ax.set_ylabel("Mean rating band (lower bound)")
    save(fig, "fig09_reply_effect_heatmap")

    fig, axes = plt.subplots(1, 2, figsize=(10.5, 4.4))
    for ax, (fm, sp, band_id) in zip(axes, REPRESENTATIVE_CELLS):
        cell = replies[(replies["first"] == fm)&(replies.speed == sp)&(replies.band == band_id)&replies.tested]
        null = simulate_spreads(cell, n_sim, seed)*100
        r = h2[(h2["first"] == fm)&(h2.speed == sp)&(h2.band == band_id)].iloc[0]
        ax.hist(null, bins=40, color=pal[0], alpha=.7, label="Shared-distribution null")
        ax.axvline(r.sd_obs*100, color=pal[1], lw=2, label=f"Observed {r.sd_obs*100:.2f} pp")
        ax.set_xlabel("N-weighted SD of reply scores (pp)")
        ax.set_ylabel("Simulated tables")
        ax.set_title(f"1.{fm}, {sp}, rating {band_id}–{band_id+199}\nq={r.q_score:.4g}; included n={int(r.N):,}")
        ax.legend(fontsize=8)
    save(fig, "fig10_h2_null_spread")

    selected = h1[h1.group_type.isin(["primary", "speed", "band"])].copy()
    fig, ax = plt.subplots(figsize=(9, 7))
    interval(ax, selected, [f"{r.group} (n={int(r.N):,})" for r in selected.itertuples()], horizontal=True)
    ax.set_title("March 2025 IPW White score; 10,000 bootstrap replicates")
    save(fig, "h1_score_confidence_intervals")
