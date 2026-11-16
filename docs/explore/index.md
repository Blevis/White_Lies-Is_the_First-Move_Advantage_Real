---
title: Data explorer
description: Compare White's score, opening replies and analysis checks using the saved study results.
hide:
  - toc
---

# Explore the results

Use the filters to compare **White's score**, **Black's opening replies**, and **checks using different game selections**. Start with all games, then look at a speed or rating group.

**Score includes half a point for each draw. It is different from win rate.** The explorer displays saved results from the March 2025 study; filters do not run new tests.

<div data-wl-explorer>
  <p role="status">Loading the study results…</p>
  <noscript><p>This explorer needs JavaScript. Read the <a href="../research/findings/">conclusion</a> or the <a href="figures/">chart guide</a> for the findings without interactive controls.</p></noscript>
</div>

## How to use the explorer

1. **Choose a view:** White's score, opening replies, or both.
2. **Choose a game speed and rating band.** Rating bands use the average of both players' ratings. The speed chart holds the selected rating band fixed; the rating chart holds the selected speed fixed.
3. **Read the point and line together.** The point is the score and the line is its 95% confidence interval. The dashed line marks 50%. Focus or hover a row for the exact interval.
4. **Compare replies separately.** The opening section has its own first-move, speed and rating filters. Only replies with at least 200 sampled games in a tested group appear.
5. **Check the alternative analyses.** The final White-score chart compares the whole-study checks. It does not change with the filters above.

The main estimate is **weighted** to account for different sampling rates. The unweighted option describes the collected sample and is available only for all games together. The speed and rating comparison charts always use weighted results.

## What to keep in mind

The charts rescale to fit the intervals, so read the axis labels before comparing distances. Some groups have too little data for a test. A missing or inconclusive result does not mean equal scores.

Players choose their openings, and some players appear repeatedly. A high or low reply score does not establish the best defense. The [checks and limits](../research/limitations.md) explain why.

## Where the numbers come from

The [downloadable data file](../assets/data/research.json) contains group summaries and source-file checksums, without individual games or player names. The website reads completed analysis outputs.

See the [output-file guide](../reproducibility/outputs.md) to trace a number back to its source. For the statistical details, read [scores, weights and tests](../methodology/statistics.md) and [understanding uncertainty](../methodology/uncertainty.md).
