---
title: Opening reply analysis
description: Inspect observed Black reply groups after 1.e4 and 1.d4 using an explanatory chessboard, exported intervals, and separate H2 omnibus tests.
hide:
  - toc
---

# The second move, in context

After **1.e4** or **1.d4**, Black's immediate reply identifies an observed group of games. Select a time control and mean-rating band to see which replies meet the study's prespecified eligibility rules, then select a reply to place that move on the board.

The board is an explanation of the grouping. It does not evaluate positions or recommend a defense.

<div data-wl-openings>
  <p role="status">Loading verified opening-reply groups…</p>
  <noscript><p>Enable JavaScript to use the explanatory board. The <a href="../../research/h2/">H2 research page</a> describes the same grouping, results, and uncertainty.</p></noscript>
</div>

## Two tests, two different questions

The **score-spread test** asks whether differences in White score across the eligible replies exceed the spread expected under the cell's null model. The **full-distribution test** also detects changes in the mix of White wins, draws, and Black wins that can leave average scores unchanged.

Across the primary study, **14 of 35** cells show score-spread evidence and **15 of 35** show full-distribution evidence after their separate Benjamini–Hochberg corrections. The adjusted p-values shown here belong to those whole-cell tests. They are not tests of the selected individual reply.

For example, after 1.d4 in blitz at mean rating 1600–1799, the score test does not pass the .05 threshold, while the full-distribution test does. Neither result identifies a universally better defense.

## What enters a cell

Each eligible game belongs to one first-move / speed / mean-rating / immediate-reply group. Primary H2 requires a mean-rating band of at least 1200, **at least 200 observed games per reply**, and **at least two eligible replies in the cell**. Eligibility in one cell does not imply eligibility in another. Sparse and out-of-scope combinations remain available as explanatory empty states.

The table starts in alphabetical notation order. You can search notation, sort by sample size or score, and select a reply to view its exact opening position. Sorting is descriptive; selected extremes have additional uncertainty that these marginal intervals do not adjust for.

!!! warning "Why a defense ranking is unsupported"
    Different players select different openings. The near-equal-rating restriction leaves only **1 of 28** score-spread rejections, with both reduced coverage and possible confounding contributing to the change. This study cannot separate those explanations or identify causal opening effects.

Read the [full H2 analysis](../research/h2.md), [statistical methods](../methodology/statistics.md), and [limitations](../research/limitations.md). The [figures gallery](figures.md) includes the prespecified e4/blitz/1600 and d4/blitz/1600 reply plots and null-spread figures.
