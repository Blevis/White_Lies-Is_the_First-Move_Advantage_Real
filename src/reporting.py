"""Render research documents directly from executed tables; no hand-entered estimates."""
from pathlib import Path
import pandas as pd


def pct(value):
    return f'{100*value:.3f}%'


def ci(row):
    return f"{pct(row['lo'])}–{pct(row['hi'])}"


def pval(value):
    return f'{value:.4g}'


def h1_display(table):
    t = table.copy()
    return pd.DataFrame({
        'Group': t.group, 'N': t.N.map(lambda n: f'{int(n):,}'),
        'White score': t.score.map(pct), '95% CI': [ci(r) for _,r in t.iterrows()],
        'Above 50% (pp)': t.difference_pp.map(lambda n: f'{n:+.3f}'),
        'Adjusted p': t.p_adjusted.map(lambda p: pval(p) if pd.notna(p) else 'not tested'),
        'Interpretation': t.interpretation})


def h2_display(table):
    t=table[table.status=='tested'].copy()
    return pd.DataFrame({'First': t['first'], 'Speed': t.speed, 'Band': t.band,
        'Included N': t.N.astype(int), 'Replies': t.k.astype(int),
        'Coverage': t.coverage.map(lambda n:f'{n:.1%}'),
        'Range (pp)': (100*t.range_obs).map(lambda n:f'{n:.2f}'),
        'Excess SD (pp)': (100*t.sd_excess).map(lambda n:f'{n:.2f}'),
        'q score': t.q_score.map(pval), 'q W/D/B': t.q_distribution.map(pval),
        'Highest White score': t.best, 'Lowest White score': t.worst})


def write_reports(root, dataset, h1, summary, h2, replies, h2_summary, robust):
    root=Path(root)
    reports=root/'reports'
    reports.mkdir(exist_ok=True)
    primary=summary['primary']; raw=summary['raw']; near=summary['near_equal']
    adjusted=summary['rating_adjusted']; dyadic=summary['dyadic']; hs=h2_summary
    bands=h1[h1.group_type=='band'].sort_values('band')
    speeds=h1[h1.group_type=='speed'].sort_values('speed')
    minband=bands.loc[bands.score.idxmin()]; maxband=bands.loc[bands.score.idxmax()]
    speed_sentence='; '.join(f'{r.speed} {pct(r.score)} (95% CI {ci(r)})' for _,r in speeds.iterrows())
    h1_rob=robust[robust.hypothesis=='H1']
    near_h2=robust[(robust.hypothesis=='H2')&(robust.scenario=='Near equal <=25')].iloc[0]
    short=h1_rob[h1_rob.scenario=='At least 40 plies'].iloc[0]
    representative=h2[(h2['first']=='e4')&(h2.speed=='blitz')&(h2.band==1600)].iloc[0]
    d4rep=h2[(h2['first']=='d4')&(h2.speed=='blitz')&(h2.band==1600)].iloc[0]
    reply_example=replies[(replies['first']=='e4')&(replies.speed=='blitz')&(replies.band==1600)&replies.tested]
    high=reply_example.loc[reply_example.score.idxmax()]
    low=reply_example.loc[reply_example.score.idxmin()]
    rep_table=replies[replies['first'].isin(['e4','d4'])&(replies.speed=='blitz')&(replies.band==1600)&replies.tested].copy()
    rep_display=pd.DataFrame({'First':rep_table['first'],'Reply':rep_table.reply,'N':rep_table.N,
        'White score':rep_table.score.map(pct),'95% CI':[ci(r) for _,r in rep_table.iterrows()],
        'Reply − remaining replies (pp)':rep_table.difference_from_rest_pp.map(lambda n:f'{n:+.2f}'),
        'Contrast 95% CI (pp)':[f'{r.difference_rest_lo_pp:.2f}–{r.difference_rest_hi_pp:.2f}' for r in rep_table.itertuples()]})
    r1=pd.DataFrame({'Sensitivity':h1_rob.scenario,'N':h1_rob.N,'Score':h1_rob.score.map(pct),
        '95% CI':[ci(r) for _,r in h1_rob.iterrows()],
        'Change from primary (pp)':h1_rob.delta_primary_pp.map(lambda n:f'{n:+.3f}'),
        'One-sided MC p':h1_rob.p_mc.map(pval),'Material change ≥1 pp':h1_rob.material_change})
    rh=robust[robust.hypothesis=='H2']
    r2=pd.DataFrame({'Sensitivity':rh.scenario,'Cells':rh.tested_cells.astype(int),
        'Score rejections':rh.rejected_cells.astype(int),'W/D/B rejections':rh.distribution_rejected.astype(int),
        'Median range (pp)':rh.median_range_pp.map(lambda n:f'{n:.2f}'),
        'Any matched decision change':rh.significance_changed})
    outcomes=dataset['raw_metrics']; wm=dataset['weighted_metrics']; prov=dataset['provenance']
    report=f'''# White Lies: Is the First-Move Advantage Real?

## Abstract

We studied whether White scores above 50% and whether Black's immediate reply is associated with outcomes in observed Lichess games. The primary dataset is a validated deterministic sample of **{dataset['N']:,} rated standard games played March 1–31, 2025**, drawn from a stream of {prov['manifest']['games_seen']:,} source games before eligibility filtering. Inverse-probability weighting, 10,000-replicate bootstrap intervals and draw-preserving null simulations yield a White score of **{pct(primary['score'])} (95% CI {ci(primary)})**, **{primary['difference_pp']:.3f} percentage points above 50%**, with one-sided Monte Carlo p={pval(primary['p_mc'])}. Equal-rating standardization gives {pct(adjusted['score'])} (dyadic 95% CI {ci(adjusted)}). Among {hs['tested_cells']} eligible opening-reply cells, {hs['score_rejections']} show score-spread evidence and {hs['distribution_rejections']} show full-outcome-distribution evidence after separate Benjamini–Hochberg corrections. Reply-score ranges have a median {hs['median_range_pp']:.2f} pp, but rating restriction substantially weakens H2 evidence. These results establish observational scoring associations in this March population, not causal effects of moving first or choosing a defense.

## 1. Introduction

Chess allocates the first move to White. Outcome data can measure whether that color scores more points, but the observed difference can also reflect opponent strength, player selection and game conditions. Distinguishing score, outright win probability and decisive-game win rate is essential because draws contribute half a point. This study completes the repository's game-level case study without claiming unavailable full-year coverage.

## 2. Research questions

**H1:** H0: White's expected score is 0.50; H1: it is greater than 0.50. The primary test is one-sided at alpha=0.05 in the eligible March game population. Rating and speed comparisons are secondary.

**H2:** Within a White first-move, rating-band and speed cell, H0: eligible Black replies have the same W/D/B distribution; H1: at least two differ. A full-distribution omnibus test addresses this hypothesis. A score-spread test separately addresses the practically relevant scoring differences; equal scores need not imply equal draw rates. Individual reply contrasts and selected extremes are exploratory.

## 3. Dataset

The source is the [Lichess rated-standard monthly dump](https://database.lichess.org/). Local inputs are `data/games_2025-03.parquet` and its manifest. The collector streamed {prov['manifest']['compressed_bytes_read']:,} compressed bytes and scanned {prov['manifest']['games_seen']:,} games. It retained {dataset['N']:,}, not the complete month. Actual dates are **{prov['date_min']} to {prov['date_max']}**; collection happened in November 2026, which is distinct from the games' dates.

The checksum is `{prov['sha256']}`. The automated validator checks completion, source URL/month, output location, row count, per-cell counts, all selected IDs' hash thresholds, declared sampling probabilities and rejection accounting. All checks passed. Additional record cleaning excluded **{dataset['cleaning']['excluded_total']}** rows; the complete per-rule ledger is `results/cleaning_ledger.csv`. Untitled players have null title fields; these are legitimate records.

Eligible games are rated standard blitz/rapid/classical, both numeric ratings, valid outcomes, Normal or Time forfeit termination, no BOT titles, and at least two plies. Legitimate resignations and short games are retained. The resignation flag is a heuristic and is not used as an exclusion. Source rejections (sequential rules) are:

{pd.DataFrame(list(prov['manifest']['rejections'].items()), columns=['Rule','Rejected']).to_markdown(index=False)}

`min_plies` is checked only after hash selection, so its rejection count concerns sampled candidates. Other games are either retained or counted as not sampled; the manifest accounting balances exactly.

The nine bands use the lower bounds 0, 1000, 1200, 1400, 1600, 1800, 2000, 2200 and 2500 on floor((White Elo + Black Elo)/2); 0 means below 1000 and 2500 means 2500+. Ratings are platform/speed ratings, not FIDE strength. The base inclusion rate is 1%; classical and bands 2200/2500 have 10%. The sample contains {dataset['sample_rate_counts']['0.01']:,} at 1% and {dataset['sample_rate_counts']['0.1']:,} at 10%. The weighted estimated eligible total is {primary['weight_total']:,.0f}; this is an estimated total, **not an independent sample size**. Kish effective N is {primary['effective_n']:,.0f}, a weight-dispersion diagnostic rather than a player count.

Observed outcomes: {int(outcomes['W']):,} White wins, {int(outcomes['D']):,} draws and {int(outcomes['B']):,} Black wins. Raw draw rate is {pct(outcomes['draw_rate'])}; IPW draw rate is {pct(wm['draw_rate'])}. Average game length is {dataset['mean_plies']:.2f} plies ({dataset['mean_move_pairs']:.2f} move pairs); median is {dataset['median_plies']:.0f} plies. The rating difference has mean {dataset['elo_difference']['mean']:.3f} Elo, median {dataset['elo_difference']['50%']:.0f}, SD {dataset['elo_difference']['std']:.2f}. There are {dataset['unique_players']:,} distinct case-normalized player names and {dataset['players_with_multiple_games']:,} recurring players. Game counts do not imply the same number of independent players.

![Observed outcomes](../figures/fig01_game_outcomes.png)

![Rating imbalance](../figures/fig05_rating_imbalance.png)

![Observed sample coverage](../figures/fig06_sample_coverage.png)

First-move, immediate-reply and PGN ECO/opening frequencies are exported in `results/`. These PGN labels are descriptions supplied by the source, not a newly validated Wikipedia classification.

## 4. Methodology

### Score and weights

For game i, Y_i is 1 for a White win, 0.5 for a draw, and 0 for a Black win. Unweighted S=(W+D/2)/N. Also report P(W)=W/N, P(D)=D/N, P(B)=B/N and P(W|decisive)=W/(W+B), with undefined empty/zero-decisive quantities represented as missing. Weighted score is:

\\[\\widehat S=\\frac{{\\sum_i w_iY_i}}{{\\sum_i w_i}},\\quad w_i=1/p_i.\\]

Oversampling stronger/classical cells changes the raw mixture; inverse-probability weighting restores the estimated mixture of eligible source games. All precision calculations use observed counts.

### Bootstrap and H1 null

Seed **202503**, **10,000 replicates** throughout the final analyses. For weighted H1, compress counts by speed/band/outcome. Independent Poisson(count) multipliers are equivalent to Poisson(1) observation multipliers; rescale their centered deviations by sqrt(1-p) for the Bernoulli finite-population correction. Recalculate the weighted numerator **and denominator** per replicate. This represents stratum-mass uncertainty as well as outcome uncertainty under the independent pseudo-random-hash/Bernoulli sampling assumption. Report percentile 95% intervals and replicate SD. Unweighted sensitivity uses the analogous Poisson bootstrap without finite-population scaling. These are pointwise, not simultaneous intervals.

For each stratum, preserve its observed draw probability d and simulate Multinomial(n, ((1-d)/2, d, (1-d)/2)). Pool simulated scores using the original weights and observed stratum sizes. The one-sided Monte Carlo p is (1 + number of simulated scores at least observed)/(10000+1). Its resolution is **1/10001**: a value at that floor is not a zero p-value or a measurement of an extremely small exact probability. The null simulation treats sampled games as independent and is conservative with respect to the finite-population correction used in bootstrap intervals.

The [exact conditional binomial test](https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.binomtest.html) conditions on observed decisive games: W given W+B follows Binomial(W+B, 0.5) under color symmetry. It validates equal-weight/unweighted results, not the unequal-weight pooled test. Exact-test and simulated-null probabilities can differ slightly because one conditions on draws and one preserves their probability. The stratified simulation assumes color symmetry within every stratum, a stronger null than a pooled mean of 0.50 alone. A design-based Wald check uses sum((1-p_i)w_i²(Y_i-S)²)/(sum(w_i))² as its variance and tests the pooled mean directly; its one-sided p is {pval(primary['p_wald_design'])}. It supports the same H1 decision without requiring stratum-by-stratum color symmetry.

Subgroups require n>=200 and at least 20 decisive games. The {summary['subgroup_tests']} eligible speed, band and speed-band tests form one secondary BH family; the prespecified primary test is excluded. The [Benjamini–Hochberg procedure](https://doi.org/10.1111/j.2517-6161.1995.tb02031.x) is used with its usual independence/positive-dependence assumptions. Repeated players and overlapping subgroup tests limit literal FDR guarantees. Marginal intervals are not multiplicity-adjusted.

### Rating and dependence adjustments

Near-equal means absolute Elo difference <=25; 10, 50 and 100 are sensitivity cutoffs. A weighted score mean regression uses speed-band intercepts and a natural cubic spline of rating difference (interior knots -200,-50,0,50,200). Standardize predictions to rating difference zero over the observed IPW speed-band mixture. This directly models the 0/0.5/1 mean; draws are not forced into a binary logistic outcome. {adjusted['omitted_sparse_rows']} row in a cell below n=200 is omitted. The model is full rank ({adjusted['rank']}/{adjusted['parameters']}), and {adjusted['outside_unit_interval']} fitted predictions fall outside [0,1]. It remains a conditional-mean model with a shared rating curve and no player-skill fixed effects or causal identification.

Dyadic sandwich sensitivity permits covariance between games sharing a player in either color: covariance = sum over player totals of influence outer products, minus sum over unordered player-pair totals of influence outer products. The subtraction counts repeated-pair covariance once. Disjoint-player games are assumed independent. This follows the shared-member dependence structure of [Aronow, Samii and Assenova's dyadic variance estimator](https://arxiv.org/abs/1312.3398). We apply it to the primary score, the rating-adjusted standardized contrast, and two prespecified representative H2 cells; we do not claim that all H2 simulations have been clustered.

### H2

Every e4/d4 game enters exactly one first-move/speed/band/reply count. March uses **200 observed games/reply**, band >=1200, and >=2 eligible replies/cell. The Explorer floor remains 10,000. Thresholds were recorded before subgroup/reply outcomes were examined. Insufficient cells/replies remain flagged in exported tables; actual test coverage excludes cells with fewer than two replies.

Within each cell, under H0 simulate 10,000 independent multinomials at each reply's observed n using pooled W/D/B probabilities. The score statistic is the n-weighted SD across reply scores. Record observed range, null mean SD, and excess SD=sqrt(max(0, observed SD² − mean(null SD²))). Excess SD is a descriptive noise adjustment, not an unbiased effect estimator. The full-distribution statistic is Pearson's W/D/B statistic; its null calibration re-estimates the pooled mix in each simulated table. Separate BH families cover all {hs['tested_cells']} primary score-spread and full-distribution tests. Range p-values are supplementary, not a third confirmatory family.

Reply intervals use a 10,000-replicate multinomial bootstrap on independent observed games. Sparse/constant counts use conservative simultaneous exact binomial bounds for P(W) and P(B), transformed through S=(1+P(W)-P(B))/2. Individual replies are compared descriptively with the **remaining eligible replies**, which are disjoint. Their CIs are marginal and not valid as selection-adjusted intervals for the maximum/minimum. Highest/lowest White scores do not establish best/worst objective defenses.

## 5. Results — H1

**Reject H0 for the primary observed-population test.** White scores {pct(primary['score'])}, 95% CI {ci(primary)}, SE {100*primary['se']:.4f} pp; the effect above 50% is {primary['difference_pp']:.3f} pp. One-sided MC p={pval(primary['p_mc'])} (simulation floor). IPW White win probability is {pct(wm['white_win_rate'])}, draw probability {pct(wm['draw_rate'])}, Black win probability {pct(wm['black_win_rate'])}, and decisive White win rate {pct(wm['decisive_white_win_rate'])}. White's win probability and score are different quantities.

{h1_display(h1[h1.group_type.isin(['primary','speed','band'])]).to_markdown(index=False)}

All cells, including insufficient ones, are in `results/h1_results.csv`. The primary row's adjusted-p column repeats its unadjusted prespecified-test p. Raw sample score is {pct(raw['score'])} (95% CI {ci(raw)}), with exact conditional p={pval(raw['p_exact_unweighted'])}; this tiny exact p concerns the raw sample only. Sampling adjustment changes the score by {100*(primary['score']-raw['score']):+.3f} pp.

Near-equal games: n={near['N']:,}, weighted score **{pct(near['score'])}** (95% CI {ci(near)}), MC p={pval(near['p_mc'])}. Rating-standardized score: **{pct(adjusted['score'])}** (dyadic 95% CI {ci(adjusted)}; asymptotic one-sided p={pval(adjusted['p_one_sided'])}). Dyadic sensitivity for the original weighted mean gives CI {ci(dyadic)}, p={pval(dyadic['p_one_sided'])}. These secondary analyses support the direction of H1 while relying on their stated models.

Band-pooled scores range from {pct(minband.score)} (band {int(minband.band)}) to {pct(maxband.score)} (band {int(maxband.band)}). There is **no monotonic increase** across rating bands. Time-control estimates are {speed_sentence}. Their similar pooled point estimates do not prove equality; composition and within-band patterns differ, and this study does not claim a detected causal speed effect.

![White score intervals](../figures/h1_score_confidence_intervals.png)

![Score by band](../figures/fig02_score_by_band.png)

![Score by speed](../figures/fig03_score_by_speed.png)

![Draw rates](../figures/fig04_draw_rate_by_band.png)

## 6. Results — H2

There are {hs['selected_e4_d4_games']:,} e4/d4 games. Tested replies contribute {hs['included_games']:,} games: **{hs['total_selected_coverage']:.2%} of all e4/d4 games**, or **{hs['within_band_coverage']:.2%} within the eligible rating bands**. Individual-cell coverage is in the table below. Eligible replies vary by cell. Across tested cells, e4 replies are {', '.join(hs['eligible_by_first']['e4'])}; d4 replies are {', '.join(hs['eligible_by_first']['d4'])}. Eligibility somewhere does not imply eligibility everywhere.

Score equality is rejected in **{hs['score_rejections']}/{hs['tested_cells']} cells** after BH; full W/D/B equality in **{hs['distribution_rejections']}/{hs['tested_cells']}**. Thus H2 has evidence in some specified populations, not every rating/control group. Observed ranges span {hs['min_range_pp']:.2f}–{hs['max_range_pp']:.2f} pp (median {hs['median_range_pp']:.2f}); median excess SD is {hs['median_excess_sd_pp']:.2f} pp. Extreme ranges are sensitive to sparse replies and selection; central spread is a more stable effect summary.

{h2_display(h2).to_markdown(index=False)}

For the prespecified e4/blitz/1600 cell, n={int(representative.N):,}, {int(representative.k)} replies, coverage {representative.coverage:.1%}, observed SD {100*representative.sd_obs:.3f} pp, null mean SD {100*representative.sd_null_mean:.3f} pp, excess SD {100*representative.sd_excess:.3f} pp and range {100*representative.range_obs:.3f} pp. Score q={pval(representative.q_score)}; full-distribution q={pval(representative.q_distribution)}. The highest observed White score is after {high.reply}: {pct(high.score)} (CI {ci(high)}, n={int(high.N):,}); the lowest after {low.reply}: {pct(low.score)} (CI {ci(low)}, n={int(low.N):,}). These are selected descriptive extremes. Dyadic score-equality sensitivity p={pval(representative.dyadic_p)} is exploratory.

The d4/blitz/1600 score-spread q={pval(d4rep.q_score)} does not pass .05, while its full-distribution q={pval(d4rep.q_distribution)} does. Its exploratory dyadic score Wald p={pval(d4rep.dyadic_p)} is not BH-adjusted and does not override the primary score decision. Different score and distribution decisions illustrate why both statistics are needed.

Representative reply-level details (blitz, mean Elo 1600–1799):

{rep_display.to_markdown(index=False)}

All reply scores and exclusion flags are in `results/h2_reply_scores.csv`. Do not treat these selected contrasts as a confirmatory pairwise testing family.

![Replies after e4, band 1600, by speed](../figures/fig07_replies_e4.png)

![Replies after d4, band 1600, by speed](../figures/fig08_replies_d4.png)

![Reply ranges by cell](../figures/fig09_reply_effect_heatmap.png)

![Observed and simulated null spread](../figures/fig10_h2_null_spread.png)

## 7. Discussion and robustness

A {primary['difference_pp']:.2f} pp excess score is small for an individual game but meaningful as a population-level scoring imbalance. The small p-value measures incompatibility with a symmetry null under the model, not a large practical effect or proof of mechanism. Near-equal-rating and equal-rating model results indicate that measured rating imbalance alone does not remove H1.

The alternatives below are sensitivity analyses, not revisions to the primary sample. Their p-values are exploratory, unadjusted Monte Carlo values. A 1 pp change is a transparent material-change flag, not a universal chess importance threshold.

{r1.to_markdown(index=False)}

Every H1 sensitivity remains positive and detectable in this analysis. The 40-ply restriction reduces the score to {pct(short.score)} (95% CI {ci(short)}), a {short.delta_primary_pp:.3f} pp change. It removes legitimate short outcomes and conditions on a post-opening variable; it targets a different population and demonstrates sensitivity in magnitude, not a reason to discard short games. Forfeit exclusion also changes the mix. These results support the direction more strongly than a universal effect size.

{r2.to_markdown(index=False)}

H2 cell decisions and selected extremes change with reply thresholds; `results/h2_sensitivity_cells.csv` records matched-cell range changes, decision changes and extreme-reply changes. Near-equal ratings leave only **{int(near_h2.rejected_cells)}/{int(near_h2.tested_cells)} score rejections**. Both reduced sample size/coverage and confounding can explain this attenuation; the analysis cannot apportion them. A claim of a stable causal defense ranking is unsupported. The all-band sensitivity evaluates the existing lower-band restriction; within-cell weighting is constant and therefore cannot change H2. Speed subsets simply retain their corresponding cells rather than adding overlapping tests.

## 8. Limitations

- This is one site's rated-standard game population, one month, selected controls and recorded filters. It does not establish full-year, over-the-board or Masters outcomes.
- Hash sampling is treated as pseudo-random Bernoulli selection; population stratum totals are estimated. Bootstrap uncertainty depends on that design approximation and the observed-game outcome/dependence assumptions.
- Elo measurements have error and do not identify latent player strength. The mean-rating bands can contain uneven matches. The regression shares a spline across bands/speeds; it does not establish exchangeability or causal identification.
- Repeated players create dependence. Dyadic sensitivity permits shared-player covariance but assumes independent disjoint-player games and does not repair all possible temporal, tournament or network dependence. Most H2 tests remain independent-game simulations; BH guarantees are conditional on standard dependence assumptions.
- High-rating classical data are sparse (only one game in the 2500+ classical cell). Sparse groups are inconclusive, not evidence of equality.
- Reply selection is endogenous; different players choose different defenses. Marginal reply intervals and extreme ranks are not simultaneous or selection-adjusted. H2 weakens substantially after equal-rating restriction.
- Game-length and forfeit sensitivities change the target population. The 40-ply restriction materially reduces H1 magnitude.
- The archived Explorer aggregates have no authenticatable date configuration or cached responses. A current collector default cannot retroactively prove the period. No aligned numeric comparison is made; `source_comparison.csv` explicitly records unavailability. No API token is available in this environment. Original archive data are preserved.
- Explorer rating-bucket alignment with mean-Elo sample bands remains unverified. The [official query implementation](https://github.com/lichess-org/lila-openingexplorer/blob/master/src/api/query.rs) supports explicit month filters, but that alone does not authenticate historical collection or selection equivalence.
- No validated full ECO mapping is present. PGN opening labels are descriptive. Immediate Black replies require no ECO join; this limitation does not prevent H2.

## 9. Conclusion

In the eligible March 2025 Lichess population, White has an observed weighted score of **{pct(primary['score'])} (95% CI {ci(primary)})**, **{primary['difference_pp']:.3f} pp above 50%**, with one-sided MC p={pval(primary['p_mc'])}. H1 is statistically supported and remains supported by near-equal-rating and rating-standardized analyses ({pct(near['score'])} and {pct(adjusted['score'])}). Effects vary across rating categories without a monotonic trend; pooled speed scores are similar.

H2 finds score-distribution associations in some cells: **{hs['score_rejections']}/{hs['tested_cells']} score-spread and {hs['distribution_rejections']}/{hs['tested_cells']} full-outcome tests** pass their separate BH corrections. The median observed range is {hs['median_range_pp']:.2f} pp, with a median noise-adjusted SD of {hs['median_excess_sd_pp']:.2f} pp. Equal-rating restriction substantially weakens score evidence. These data demonstrate observational associations and conditional uncertainty, not that the first move or a named defense causes a specified change in outcomes.

## 10. Reproducibility

From the repository root:

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m src.run_analysis
python -m jupyter nbconvert --to notebook --execute --inplace analysis.ipynb --ExecutePreprocessor.timeout=600
python -m pytest -q
python tests/mock_run.py
```

No routine step downloads games or calls Explorer/Wikipedia. The notebook reruns the same offline pipeline and renders these exported results. Generated artifacts: `results/dataset_summary.json`, `h1_results.csv`, `h1_summary.json`, `h2_results.csv`, `h2_reply_scores.csv`, `h2_summary.json`, `robustness_results.csv`, `h2_sensitivity_cells.csv`, `source_comparison.csv`, EDA/frequency tables, model coefficients and `software_versions.json`. Source code provides every calculation. Figures 1–10 plus `h1_score_confidence_intervals` are exported as 300-dpi PNG and PDF. Legacy exploratory figures retain their names and are not evidence for this report.

The frozen seed is {summary['seed']}; final simulation count is {summary['n_sim']:,}. Dependency versions from the executed environment are in `results/software_versions.json`. The manifest hashes the source data; automated tests cover known score identities, invalid data, provenance tampering, null calibration, planted effects, weighting imbalance, sparse replies, full-distribution changes, dyadic covariance and artifact consistency. Verification results are recorded separately in `reports/COMPLETION_CHECKLIST.md` so regeneration does not invent test outcomes.

Optional future collection: stream each additional monthly dump with the same documented filters and ID rule, save/validate a separate manifest and checksum, then combine months with weights and month-aware sensitivity checks. Do not relabel March as a full year. For optional Explorer validation, explicitly query March 2025 (or a separately labeled full year), save full query/response sidecars and checksums, validate nested counts, and resolve rating/filter equivalence before numeric comparison. No such collection is required for the scoped March result.
'''
    (reports/'FINAL_RESEARCH_REPORT.md').write_text(report)
    conclusion=f'''# Final conclusion — White Lies

**1. Is White's advantage statistically detectable?** In the validated sample of {dataset['N']:,} eligible Lichess games played March 1–31, 2025, the inverse-probability-weighted White score is **{pct(primary['score'])}**, with a **95% bootstrap interval of {ci(primary)}**. The one-sided draw-preserving Monte Carlo p-value is **{pval(primary['p_mc'])}**, the resolution limit of 10,000 simulations. We reject the primary 50% null. The raw sample score is {pct(raw['score'])}; its exact conditional p={pval(raw['p_exact_unweighted'])} is an unweighted cross-check. Among {near['N']:,} games with ratings within 25 Elo, the weighted score is {pct(near['score'])} (CI {ci(near)}). Equal-rating standardization gives {pct(adjusted['score'])} (shared-player dyadic CI {ci(adjusted)}; asymptotic p={pval(adjusted['p_one_sided'])}). The direction survives these adjustments.

**2. Is it practically meaningful?** The primary excess is **{primary['difference_pp']:.3f} percentage points**, approximately {primary['difference_pp']:.2f} additional White points per 100 games relative to equal scoring. It is a modest association, not a guarantee for any individual game. Statistical detectability is stronger than evidence for a universal magnitude: restricting to games lasting at least 40 plies reduces the score to {pct(short.score)}.

**3. Does playing strength matter?** Weighted band scores range from {pct(minband.score)} in band {int(minband.band)} to {pct(maxband.score)} in band {int(maxband.band)}. The pattern is not monotonic. Sparse high-rated classical cells remain inconclusive. These are categories of platform ratings, not controlled comparisons of identical players.

**4. Does time control matter?** Pooled estimates are {speed_sentence}. They are very similar; these estimates do not demonstrate a general speed gradient or prove equivalence. Draw rates and rating compositions vary.

**5. Does Black's first reply matter?** With at least 200 games per reply and bands >=1200, **{hs['score_rejections']} of {hs['tested_cells']} cells** reject score equality and **{hs['distribution_rejections']}** reject full W/D/B equality after separate BH corrections. Tested replies cover {hs['total_selected_coverage']:.1%} of all e4/d4 games. Median observed score range is {hs['median_range_pp']:.2f} pp and median excess SD {hs['median_excess_sd_pp']:.2f} pp. However, the near-equal-rating sensitivity leaves only {int(near_h2.rejected_cells)}/{int(near_h2.tested_cells)} score rejections. Confounding, power, coverage and threshold sensitivity prevent a stable objective-defense ranking.

**6. What does the study demonstrate?** White scores slightly above half in this sampled March population even after measured rating adjustment. Opening replies carry observational outcome associations in some cells. Neither result establishes causation, full-year behavior, or universal chess strategy. Repeated players, model assumptions, unverified Explorer dates and incomplete ECO reconciliation delimit the evidence.
'''
    (reports/'FINAL_CONCLUSION.md').write_text(conclusion)
    # Preserve the original animated chess heading; replace aspirational claims with evidence.
    readme=root/'README.md'
    header='''<div align="center">

# ♟️ White Lies

<img src="https://readme-typing-svg.demolab.com?font=Fira+Code&weight=600&size=23&duration=2800&pause=1100&color=D4AF70&center=true&vCenter=true&width=850&height=65&lines=Is+the+First-Move+Advantage+Real%3F;One+extra+move.+A+measurable+edge%3F;Chess+%C3%97+Data+%C3%97+Probability" alt="Is the First-Move Advantage Real?" />

**Chess × Data × Probability**

</div>
'''
    readme.write_text(header+f'''
## The finding

White scores **{pct(primary['score'])}** (95% CI **{ci(primary)}**) in the weighted eligible March 2025 Lichess population: **+{primary['difference_pp']:.3f} percentage points** over 50%. One-sided Monte Carlo p={pval(primary['p_mc'])} (10,000-simulation resolution limit). Equal-rating standardization gives **{pct(adjusted['score'])}** (dyadic CI {ci(adjusted)}).

Black's immediate reply is associated with score differences in **{hs['score_rejections']}/{hs['tested_cells']} eligible cells** after BH correction; full W/D/B distributions differ in {hs['distribution_rejections']}. H2 weakens markedly under near-equal-rating restrictions. These are **observational associations**, not causal claims or defense recommendations.

Read the [full research report](reports/FINAL_RESEARCH_REPORT.md), [short conclusion](reports/FINAL_CONCLUSION.md), [audit](reports/implementation_audit.md), and [verification checklist](reports/COMPLETION_CHECKLIST.md).

## Questions and outcome

- **H1:** H0 expected White score =0.50; one-sided H1 >0.50. Test the weighted overall population, then rating and speed groups with multiplicity correction.
- **H2:** Within first-move/speed/rating cells after 1.e4 or 1.d4, test equality of Black replies' W/D/B distributions and separately their score spread.

A win is 1, draw 0.5, loss 0. White score is **(W + D/2)/N**, different from White win probability. Primary analysis uses weights **1/sample_rate**; weighted totals are never treated as observed sample sizes.

## Verified data and scope

**March 1–31, 2025 only:** {dataset['N']:,} sampled games from the [Lichess monthly rated-standard dump](https://database.lichess.org/), {prov['manifest']['games_seen']:,} source games scanned. All checksum, manifest, hash-selection, sampling-rate and record checks pass; {dataset['cleaning']['excluded_total']} additional rows excluded. Includes blitz, rapid and classical; BOT titles, invalid ratings/results, other terminations and games below two plies were excluded by the collector. Resignations and legitimate short games are retained.

The sample is deterministic by game ID, with 1% base sampling and 10% classical/2200/2500-band overrides. Bands use mean opponent Elo. All collected bands enter H1; H2 uses bands >=1200 and >=200 observed games/reply. The archived Explorer CSV has unverified dates and is excluded. The legacy game CSV drops resignations and is excluded.

## Method and results

10,000-replicate sampling-aware Poisson multiplier bootstrap, draw-preserving multinomial null simulations, exact decisive-game binomial cross-checks where applicable, BH adjustment, equal-rating spline score regression and shared-player dyadic sensitivity. Prespecified choices are recorded in the audit. Independent-game and disjoint-player assumptions are explicit in the report.

{h1_display(h1[h1.group_type.isin(['primary','speed'])]).to_markdown(index=False)}

Near-equal-rating score: **{pct(near['score'])}** (CI {ci(near)}, n={near['N']:,}). Band scores have no monotonic trend. Sensitivities preserve H1's direction, but the >=40-ply subset materially reduces its size. H2's median reply-score range is {hs['median_range_pp']:.2f} pp; ranges are selected extremes with uncertainty, not objective opening values.

![White score and confidence intervals](figures/h1_score_confidence_intervals.png)

![Black replies after e4, band 1600](figures/fig07_replies_e4.png)

## Reproduce offline

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m src.run_analysis
python -m jupyter nbconvert --to notebook --execute --inplace analysis.ipynb --ExecutePreprocessor.timeout=600
python -m pytest -q
python tests/mock_run.py
```

The pipeline validates inputs before analysis, performs EDA/H1/H2/robustness, writes numerical tables and reports, exports 11 scientific figures in PNG/PDF, and checks outputs. It makes no network calls or large downloads. `--output-root /path/to/output` writes a separate artifact bundle. The notebook runs from the repository root using `src` imports. Seed: **{summary['seed']}**. Executed package versions: [software_versions.json](results/software_versions.json).

## Repository guide

| Location | Content |
|---|---|
| `analysis.ipynb` | Executed scientific notebook with interpretation |
| `src/validation.py` | Fail-closed provenance and counted cleaning |
| `src/stats.py`, `hypothesis_h1.py` | Reusable scores, bootstrap/null tests, weighting and adjustment |
| `src/h2.py`, `hypothesis_h2.py` | Existing spread test plus March grouping, coverage, full-distribution tests and BH |
| `src/run_analysis.py`, `plotting.py`, `reporting.py` | Offline execution, figures and data-driven documents |
| `src/fetch_games.py`, `explorer.py`, `wiki_scrape.py` | Preserved optional collectors and metadata helpers |
| `results/` | Provenance, EDA, H1/H2, sensitivity, model and source-availability tables |
| `figures/fig01_*` through `fig10_*` | Final March figures, plus H1 interval plot; each PNG and PDF |
| `reports/` | Audit, full report, short conclusion and verification |
| `tests/` | Analytic, synthetic calibration/power, provenance and artifact checks |

Old `q1_*`, `q2_*`, `draw_rate_by_band.*` and LaTeX artifacts are retained exploratory Explorer outputs; their dates are unverified. They do not support the March conclusions. `original_project/build_notebook.py` is an archived historical generator and must not replace the repaired notebook.

## Limits and optional future work

The study covers one site/month with selected rated game types. Ratings and opening choices are observational; repeated players limit independent-game inference. Near-equal H2 has less evidence, threshold decisions change, and high-rating classical cells are sparse. Explorer source alignment and full ECO mapping remain unverified. Full-year collection, Masters analysis and a dashboard are optional future work and have not been implemented. None is needed to reproduce this March case study.
''')
