import nbformat as nbf
md = nbf.v4.new_markdown_cell
code = nbf.v4.new_code_cell
cells = []

cells.append(md("""# Chess: is playing White really an advantage?

**Pipeline** (modules live next to this notebook):

| Module | Role |
|---|---|
| `explorer.py` | Authenticated Lichess opening-explorer client: serial requests, 429 backoff, on-disk cache, `collect()` |
| `wiki_scrape.py` | Scrapes Wikipedia *List of chess openings* -> `(eco, name, family)`; fixed a-priori family map |
| `stats.py` | Score + CI (per-game variance), family derivation by subtraction, contrasts, Q2 ranges |
| `plotting.py` | Paper-style figures (PDF + PNG into `figures/`) |

**Questions.** Q1: White's score vs. 0.5 by rating band (per speed). Q2: does the edge differ between open and closed opening families (ranges across bands).

**Setup.** Create a free, scope-less token at <https://lichess.org/account/oauth/token> and put `LICHESS_TOKEN=...` in a `.env` file next to this notebook (git-ignored)."""))

cells.append(code("""import os, warnings
import numpy as np, pandas as pd
from IPython.display import display
try:
    from dotenv import load_dotenv; load_dotenv()
except ImportError:
    pass

import explorer, wiki_scrape, stats, plotting
from explorer import Explorer, collect, RATINGS, SPEEDS

np.random.seed(0)
pd.options.display.float_format = "{:.4f}".format

# ---- analysis config (fix BEFORE looking at results) ----
MIN_BAND = 1200      # bands below this are flagged/excluded from Q2 ranges (noisy, provisional ratings)
MIN_N    = 10_000    # minimum games per cell for inclusion in Q2 ranges
RELOAD   = False     # True -> ignore data/explorer_raw.csv and re-collect (cache still applies)
print("speeds:", SPEEDS, "| bands:", RATINGS)"""))

cells.append(md("## 1. Collect (Lichess explorer API)\n180 requests at 1 req/s on a cold cache; everything is cached in `.cache/`, so re-runs are free."))
cells.append(code("""RAW = "data/explorer_raw.csv"
if os.path.exists(RAW) and not RELOAD:
    raw = pd.read_csv(RAW)
    print("loaded", RAW)
else:
    ex = Explorer()
    raw = collect(ex, out=RAW)
    print("HTTP requests made:", ex.n_http)
raw.head()"""))

cells.append(md("## 2. Sanity checks\nNested-position subtraction must give non-negative counts; N per cell tells us where the estimates are thin."))
cells.append(code("""fam_long = stats.derive_families(raw)          # asserts non-negativity
est = stats.estimate(fam_long)

n_root = est[est.family == "all"].pivot(index="band", columns="speed", values="N")
display(n_root.map(lambda v: f"{v:,.0f}"))

# the five derived families + the named subsets should partition 'all'
chk = (fam_long[fam_long.family.isin(stats.FAMILIES)].groupby(["speed", "band"])[["W", "D", "B"]].sum()
       - fam_long[fam_long.family == "all"].set_index(["speed", "band"])[["W", "D", "B"]])
assert (chk.abs().max().max() == 0), "families do not partition the root counts"
print("partition check OK")"""))

cells.append(md("## 3. Q1: White score vs. 0.5 by rating band\nWith explorer-scale N every cell rejects 0.5, so the deliverable is the **effect size and CI**; `z_vs_half` is included for completeness. Draw rate is reported next to the score because the same score can come from very different W/D/L mixes."))
cells.append(code("""q1 = stats.q1_table(est)
display(q1.assign(N=q1.N.map("{:,.0f}".format)))
fig = plotting.plot_q1(q1)
fig = plotting.plot_draw_rate(q1)"""))
cells.append(code("""# Pooled-over-bands view per speed (N-weighted), restricted to the analysis set
a = q1[q1.band >= MIN_BAND].copy()
a["w_pts"] = a.score * a.N
pooled = a.groupby("speed").apply(lambda d: pd.Series({
    "N": d.N.sum(), "score": d.w_pts.sum() / d.N.sum(),
    "score_min_band": d.score.min(), "score_max_band": d.score.max()}), include_groups=False)
pooled"""))

cells.append(md("## 4. Q2: open vs. closed families\nFamilies (fixed a priori): **open** 1.e4 e5; **semi-open** 1.e4 other; **closed** 1.d4 d5; **semi-closed** 1.d4 other; **flank** everything else. Ranges = min/max of the White score across rating bands in the analysis set, per speed."))
cells.append(code("""ranges = stats.q2_ranges(est, min_band=MIN_BAND, min_n=MIN_N)
display(ranges.pivot(index="family", columns="speed", values=["min", "max"]).round(4))"""))
cells.append(code("""# Contrasts between disjoint families (difference in White score with 95% CI)
contrasts = pd.concat({
    "open - closed":          stats.contrast(est, "open", "closed"),
    "open - semi_open":       stats.contrast(est, "open", "semi_open"),
    "closed - semi_closed":   stats.contrast(est, "closed", "semi_closed"),
}, names=["contrast"]).reset_index(level=0)
contrasts = contrasts[contrasts.band >= MIN_BAND]
display(contrasts.pivot_table(index=["contrast", "speed"], columns="band", values="diff").round(4))
display(contrasts.assign(sig=lambda d: (d.lo > 0) | (d.hi < 0)).groupby(["contrast", "speed"]).sig.mean().unstack())"""))
cells.append(code("""fig = plotting.plot_q2(est, stats.FAMILIES, min_band=1000)"""))

cells.append(md("## 5. Wikipedia scrape (taxonomy coverage)\nThe explorer gives outcomes; Wikipedia gives the named-opening taxonomy. This checks how many catalogued openings fall in each family under the ECO-range mapping."))
cells.append(code("""wiki = wiki_scrape.load_openings()
print(len(wiki), "ECO rows scraped")
display(wiki.family.value_counts().rename("named openings").to_frame())
wiki.head(10)"""))

cells.append(md("""## 6. Threats to validity (write these up)
- **Selection / endogeneity.** Black chooses the defense and strong players self-select into lines, so family differences are partly selection, not intrinsic opening strength. The contrasts are descriptive, not causal.
- **Rating buckets.** Verify in the current API docs whether buckets use per-player or average game rating; interpretation of "band" depends on it.
- **Low bands.** Provisional ratings and blunder-driven results; hence `MIN_BAND`. Raw bottom bands are kept in the data but excluded from Q2 ranges.
- **Speed is a first-order moderator.** Never pool bullet with classical. Pooled numbers above are within speed only.
- **Family map is approximate.** ECO is structural; the explorer-derived families are first-move based.
- **Multiple dependent cells.** Bands/speeds are not independent tests; CIs are per-cell, not simultaneous."""))

cells.append(code("""# Export LaTeX (booktabs) tables for the paper
os.makedirs("figures", exist_ok=True)
t1 = q1[["speed", "band", "N", "score", "lo", "hi", "draw_rate"]].copy()
t1["band"] = t1.band.map(plotting.band_label)
t1.to_latex("figures/table_q1.tex", index=False, float_format="%.4f", longtable=False)
ranges.to_latex("figures/table_q2_ranges.tex", index=False, float_format="%.4f")
print("wrote figures/table_q1.tex, figures/table_q2_ranges.tex")"""))

nb = nbf.v4.new_notebook(cells=cells)
nb.metadata["kernelspec"] = {"display_name": "Python 3", "language": "python", "name": "python3"}
nbf.write(nb, "main.ipynb")
print("wrote main.ipynb with", len(cells), "cells")
