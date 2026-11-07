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
