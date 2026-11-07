<div align="center">

# ♟️ White Lies

<img src="https://readme-typing-svg.demolab.com?font=Fira+Code&weight=600&size=23&duration=2800&pause=1100&color=D4AF70&center=true&vCenter=true&width=850&height=65&lines=Is+the+First-Move+Advantage+Real%3F;One+extra+move.+A+measurable+edge%3F;Chess+%C3%97+Data+%C3%97+Probability" alt="Animated headline: Is the First-Move Advantage Real?" />

**Does playing White actually increase your chances of success in chess — or is the advantage smaller than we think?**

A data-driven investigation of chess outcomes, opening choices, rating levels, and the role of chance.

![Python](https://img.shields.io/badge/Python-3776AB?style=flat-square&logo=python&logoColor=white)
![Jupyter](https://img.shields.io/badge/Jupyter-F37626?style=flat-square&logo=jupyter&logoColor=white)
![Chess](https://img.shields.io/badge/Chess-Research-D4AF70?style=flat-square)
![Status](https://img.shields.io/badge/Status-Work_in_Progress-6B7280?style=flat-square)

</div>

---

## 🎯 The purpose

In chess, White always moves first. That single move is often described as an advantage, but **how large is it, how confidently can we measure it, and does it depend on what happens next?**

**White Lies** turns that familiar claim into a testable research question. Rather than relying on intuition or a few famous games, we compare large collections of game outcomes, account for draws, measure uncertainty, and examine the opening decisions that shape the result.

Our aim is not just to say *"White wins more often."* It is to show **how much White scores, when the difference is larger than chance, and where the evidence is less certain.**

## 🔍 Two hypotheses

| Hypothesis | What we want to find out |
|:--|:--|
| **H1 — Does White have a real edge?** | Does White score above **50%** across rating levels, and how does that advantage change with playing strength? |
| **H2 — Does Black's first reply matter?** | After **1.e4** and **1.d4**, do different Black replies lead to meaningfully different outcomes for White? |

## ♙ What counts as an advantage?

A draw is worth half a point. We therefore measure White's *score per game*, not just the percentage of games White wins:

$$
\text{White score} = \frac{\text{White wins} + 0.5\times\text{Draws}}{\text{White wins} + \text{Draws} + \text{Black wins}}
$$

- **50%** represents an even score.
- **Above 50%** means White scores more points per game than Black in the observed sample.
- **Confidence intervals and simulations** help us distinguish a measured difference from random variation.

We also examine the **draw rate** and **the probability that White wins given that a game is decisive**.

## 📚 The data behind the question

The project brings together two sources:

- **[Lichess Opening Explorer](https://lichess.org/analysis)** — aggregated White-win, draw, and Black-win counts for chess positions, with comparisons by rating and time control, plus a Masters database.
- **[Wikipedia — List of ECO codes](https://en.wikipedia.org/wiki/List_of_ECO_codes)** — opening classifications and names used to connect chess move sequences with recognizable opening families and variations.

**Target study design:** games from **January–December 2025**, rating bands from **1000 to 2500**, and **blitz, rapid, and classical** time controls, with Masters results for comparison. Opening positions are matched to ECO definitions through their moves.

## 🧪 How we test the ideas

1. **Collect and validate** game counts and ECO opening definitions.
2. **Explore** White's score, draws, sample sizes, rating differences, and opening coverage.
3. **Estimate uncertainty** using **10,000 bootstrap simulations** of the observed win/draw/loss mix.
4. **Test H1 against chance** by simulating equally matched players while preserving the draw rate.
5. **Test H2** by comparing individual Black replies to **1.e4** and **1.d4**, using a simulated spread test rather than overlapping opening-family counts.
6. **Compare with Masters** and present results in an offline notebook and interactive dashboard.

> **Important distinction:** The methods above describe the intended complete study. The repository currently includes preliminary collection and exploratory analysis; the full 2025 dataset, simulation tests, and dashboard are in progress.

## 📊 What we want to make visible

- White's score **with a 95% uncertainty interval**, not just a single percentage.
- Differences across rating bands and the role of draws.
- How many games are needed before an advantage becomes detectable.
- Which first Black replies are associated with stronger or weaker White scores.
- Why conclusions based on rare openings or smaller Masters samples need wider uncertainty ranges.

## 🚧 Progress

- [x] Initial Lichess data collection and exploratory dataset
- [x] Basic Wikipedia ECO extraction
- [x] White-score and draw-rate calculations
- [x] Preliminary charts and Jupyter analysis
- [ ] Complete ECO move parsing and source join
- [ ] Frozen 2025 dataset and raw-response cache
- [ ] H1 bootstrap, chance test, and sample-size analysis
- [ ] H2 reply-level spread tests and Masters comparison
- [ ] Fully offline notebook and Streamlit dashboard

## ⚖️ How to interpret the results

A statistically detectable pattern does **not** automatically prove that moving first *causes* a particular outcome. These are observational chess games: opponents, ratings, time controls, and opening choices all influence what we observe. Deeper ECO positions may also contain overlapping games, so they must **not** be added together as independent samples.

The goal is to make conclusions that are **measurable, reproducible, and appropriately cautious**.

---

<div align="center">

*One move first. Thousands of games. How real is the edge?*

**♔ White Lies — Chess × Statistics × Critical Thinking ♚**

</div>
