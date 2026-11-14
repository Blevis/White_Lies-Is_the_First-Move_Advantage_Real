"""White Lies public website and interactive research dashboard."""
from __future__ import annotations

import json
from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from data_loader import (
    load_h1_results,
    load_h2_results,
    load_h2_reply_scores,
    load_json,
)

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"
FIGURES = ROOT / "figures"

st.set_page_config(
    page_title="White Lies | Chess × Data × Probability",
    page_icon="♟️",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
      @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Playfair+Display:wght@600;700&display=swap');
      .stApp { background: #f5f2e9; color: #182820; }
      [data-testid="stSidebar"] { background: #172820; }
      [data-testid="stSidebar"] * { color: #f4eddb !important; }
      h1, h2, h3 { font-family: 'Playfair Display', Georgia, serif !important; color: #193126; }
      p, label, div { font-family: 'DM Sans', sans-serif; }
      .hero { background: linear-gradient(120deg,#172820,#294638); padding: 2.5rem 2.6rem; border-radius: 22px; color: #f5efdf; margin-bottom: 1.2rem; }
      .hero h1 { color: #f5efdf !important; font-size: clamp(2.2rem,5vw,4rem); margin: 0; }
      .hero p { color: #d8dfd4; font-size: 1.08rem; max-width: 780px; }
      .eyebrow { color: #d4b56b; text-transform: uppercase; letter-spacing: .16em; font-size: .75rem; font-weight: 700; }
      .metric-card { background: #fffdf7; border: 1px solid #e6dfcf; border-radius: 16px; padding: 1.1rem 1.2rem; min-height: 112px; }
      .metric-label { color: #66756a; font-size: .8rem; text-transform: uppercase; letter-spacing: .08em; }
      .metric-value { color: #1b3829; font-size: 1.8rem; font-weight: 700; margin-top: .25rem; }
      .metric-note { color: #66756a; font-size: .78rem; }
      .section-note { color: #58695d; font-size: .95rem; }
      .callout { background: #e9eee6; border-left: 4px solid #55765d; padding: .9rem 1.1rem; border-radius: 8px; }
      .small-muted { color: #6a766c; font-size: .82rem; }
      footer { visibility: hidden; }
    </style>
    """,
    unsafe_allow_html=True,
)


def metric_card(label: str, value: str, note: str = "") -> None:
    st.markdown(
        f'<div class="metric-card"><div class="metric-label">{label}</div>'
        f'<div class="metric-value">{value}</div><div class="metric-note">{note}</div></div>',
        unsafe_allow_html=True,
    )


def show_home() -> None:
    summary = load_json(RESULTS / "h1_summary.json")
    dataset = load_json(RESULTS / "dataset_summary.json")
    h2_summary = load_json(RESULTS / "h2_summary.json")
    primary = summary["primary"]
    weighted = dataset["weighted_metrics"]

    st.markdown(
        """
        <div class="hero">
          <div class="eyebrow">Chess × Data × Probability</div>
          <h1>White Lies</h1>
          <p><b>Is the First-Move Advantage Real?</b><br>
          A data-driven investigation of the first-move advantage in online chess.
          Explore the evidence, understand the methods, and inspect the results yourself.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.subheader("The finding")
    st.write(
        "In the weighted eligible March 2025 Lichess population, White scores "
        "slightly above an equal 50% share. The result is statistically detectable "
        "in this study, but it is an observational finding—not a guarantee for an individual game."
    )
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        metric_card("Weighted White score", f"{primary['score']:.3%}", "95% confidence interval")
    with c2:
        metric_card("Games analyzed", f"{int(primary['N']):,}", "March 1–31, 2025")
    with c3:
        metric_card("Above 50%", f"+{primary['difference_pp']:.3f} pp", "Percentage points")
    with c4:
        metric_card("Black replies", f"{h2_summary['score_rejections']} / {h2_summary['tested_cells']}", "H2 score-spread cells rejected after BH correction")

    st.markdown("### What does the score mean?")
    left, right = st.columns([1.15, 1])
    with left:
        st.markdown(
            "The White Score is not the same as White's win rate. A White win counts as 1 point, "
            "a draw as 0.5 points, and a Black win as 0 points. The score is the average share "
            "of points earned by White."
        )
        st.latex(r"\text{White Score} = \frac{W + D/2}{N}")
        st.markdown(
            '<div class="callout"><b>Important:</b> 51.776% means White earned 51.776% of the available '
            'points in the weighted analysis. It does not mean White won 51.776% of games.</div>',
            unsafe_allow_html=True,
        )
    with right:
        outcomes = pd.DataFrame({
            "Outcome": ["White wins", "Draws", "Black wins"],
            "Games": [weighted["W"], weighted["D"], weighted["B"]],
        })
        fig = px.pie(outcomes, names="Outcome", values="Games", hole=.55,
                     color="Outcome", color_discrete_map={
                         "White wins": "#d7c79b", "Draws": "#7c927d", "Black wins": "#263f32"})
        fig.update_layout(margin=dict(t=10,b=10,l=10,r=10), paper_bgcolor="rgba(0,0,0,0)",
                          legend_title_text="", height=300)
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("### Explore the study")
    a, b, c = st.columns(3)
    with a:
        st.markdown("**H1 · First-move advantage**")
        st.caption("Compare White's score with the 50% equal-score benchmark.")
    with b:
        st.markdown("**H2 · Black's first reply**")
        st.caption("Explore reply-level outcomes after 1.e4 and 1.d4.")
    with c:
        st.markdown("**Methods · How it was tested**")
        st.caption("Understand sampling, weighting, confidence intervals and limitations.")

    st.markdown("<div class='small-muted'>Source: Lichess monthly rated-standard game database, March 2025. "
                "The analysis is observational and limited to the study's stated sample and filters.</div>",
                unsafe_allow_html=True)


def show_h1() -> None:
    st.title("H1 · Is White's score above 50%?")
    st.write("Explore the weighted White Score by time control, rating band, or their intersection.")
    h1 = load_h1_results()
    speed_options = ["All time controls", "blitz", "rapid", "classical"]
    speeds = st.selectbox("Time control", speed_options, key="h1_speed")
    bands = sorted(int(x) for x in h1.loc[h1.group_type == "band", "band"].unique())
    band_options = ["All rating bands"] + bands
    selected_band = st.selectbox("Mean-opponent Elo band (lower bound)", band_options, key="h1_band")

    if speeds == "All time controls" and selected_band == "All rating bands":
        row = h1[h1.group_type == "primary"]
        title = "Overall weighted result"
    elif speeds != "All time controls" and selected_band == "All rating bands":
        row = h1[(h1.group_type == "speed") & (h1.speed == speeds)]
        title = f"All rating bands · {speeds.title()}"
    elif speeds == "All time controls" and selected_band != "All rating bands":
        row = h1[(h1.group_type == "band") & (h1.band == selected_band)]
        title = f"All time controls · rating band {selected_band}+"
    else:
        row = h1[(h1.group_type == "cell") & (h1.speed == speeds) & (h1.band == selected_band)]
        title = f"{speeds.title()} · rating band {selected_band}+"

    if row.empty:
        st.warning("No result is available for this filter combination.")
        return
    result = row.iloc[0]
    m1, m2, m3 = st.columns(3)
    with m1:
        metric_card("White Score", f"{result.score:.3%}", title)
    with m2:
        metric_card("95% interval", f"{result.lo:.3%} – {result.hi:.3%}", "Bootstrap interval")
    with m3:
        metric_card("Observed games", f"{int(result.N):,}", "Unweighted observed sample count")

    chart_rows = h1[h1.group_type == "speed"].copy() if speeds == "All time controls" and selected_band == "All rating bands" else None
    if chart_rows is not None:
        fig = px.bar(chart_rows, x="speed", y=chart_rows.score * 100, error_y=(chart_rows.hi-chart_rows.score)*100,
                     error_y_minus=(chart_rows.score-chart_rows.lo)*100,
                     labels={"x": "Time control", "y": "White Score (%)"},
                     title="Weighted White Score by time control",
                     color="speed", color_discrete_sequence=["#244735", "#82977d", "#c9aa64"])
        fig.add_hline(y=50, line_dash="dash", line_color="#9b5d45", annotation_text="50% benchmark")
        fig.update_layout(showlegend=False, paper_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig, use_container_width=True)

    band_rows = h1[h1.group_type == "band"].sort_values("band")
    if speeds == "All time controls" and selected_band == "All rating bands":
        fig2 = go.Figure()
        fig2.add_trace(go.Scatter(
            x=band_rows.band.astype(str), y=band_rows.score * 100, mode="lines+markers",
            name="White Score", line=dict(color="#315b43", width=3),
            error_y=dict(type="data", symmetric=False,
                         array=(band_rows.hi-band_rows.score)*100,
                         arrayminus=(band_rows.score-band_rows.lo)*100),
        ))
        fig2.add_hline(y=50, line_dash="dash", line_color="#9b5d45")
        fig2.update_layout(title="White Score by rating band", xaxis_title="Mean-opponent Elo band (lower bound)",
                           yaxis_title="White Score (%)", paper_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig2, use_container_width=True)

    st.markdown("### Statistical interpretation")
    if bool(result.get("reject", False)) if "reject" in result.index else False:
        st.success("The corresponding test rejects the 50% null after the study's stated adjustment, where applicable.")
    else:
        st.info("This subgroup estimate should be interpreted with its confidence interval and the study's testing rules.")
    st.caption("The filters select already-computed study results. They do not rerun the original statistical tests.")


def show_h2() -> None:
    st.title("H2 · Does Black's first reply matter?")
    st.write("Compare the observed White Score for eligible Black replies within a selected study cell.")
    replies = load_h2_reply_scores()
    h2 = load_h2_results()
    c1, c2, c3 = st.columns(3)
    with c1:
        first = st.selectbox("White's first move", ["e4", "d4"], format_func=lambda x: f"1.{x}")
    with c2:
        speed = st.selectbox("Time control", ["blitz", "rapid", "classical"], key="h2_speed")
    with c3:
        bands = sorted(int(x) for x in replies.loc[replies.tested, "band"].unique())
        band = st.selectbox("Rating band", bands, index=bands.index(1600) if 1600 in bands else 0)

    cell = h2[(h2["first"] == first) & (h2.speed == speed) & (h2.band == band)]
    selected = replies[(replies["first"] == first) & (replies.speed == speed) &
                       (replies.band == band) & replies.tested].copy()
    if cell.empty or selected.empty:
        st.warning("The selected cell does not meet the study's eligibility requirements.")
        return
    info = cell.iloc[0]
    x1, x2, x3 = st.columns(3)
    with x1:
        metric_card("Included games", f"{int(info.N):,}", "Eligible replies only")
    with x2:
        metric_card("Coverage", f"{info.coverage:.1%}", "Of games in this cell")
    with x3:
        metric_card("Eligible replies", f"{int(info.k)}", "Replies meeting the minimum count")

    selected = selected.sort_values("score")
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=selected.reply, y=selected.score * 100,
        marker_color="#66836b", name="White Score",
        error_y=dict(type="data", symmetric=False,
                     array=(selected.hi-selected.score)*100,
                     arrayminus=(selected.score-selected.lo)*100),
        customdata=selected[["N", "W", "D", "B"]],
        hovertemplate="Reply: %{x}<br>White Score: %{y:.2f}%<br>Games: %{customdata[0]:,}<br>W/D/B: %{customdata[1]:,}/%{customdata[2]:,}/%{customdata[3]:,}<extra></extra>",
    ))
    fig.add_hline(y=50, line_dash="dash", line_color="#9b5d45", annotation_text="50% benchmark")
    fig.update_layout(title=f"White Score after 1.{first} · {speed.title()} · Elo {band}–{band+199}",
                      xaxis_title="Black's first reply", yaxis_title="White Score (%)",
                      paper_bgcolor="rgba(0,0,0,0)")
    st.plotly_chart(fig, use_container_width=True)

    display = selected[["reply", "N", "W", "D", "B", "score", "lo", "hi", "difference_from_rest_pp"]].copy()
    display["score"] = (display.score * 100).round(2)
    display["lo"] = (display.lo * 100).round(2)
    display["hi"] = (display.hi * 100).round(2)
    display["difference_from_rest_pp"] = display.difference_from_rest_pp.round(2)
    display = display.rename(columns={"reply":"Black reply", "N":"Games", "W":"White wins", "D":"Draws", "B":"Black wins",
                                      "score":"White score (%)", "lo":"CI lower (%)", "hi":"CI upper (%)",
                                      "difference_from_rest_pp":"Difference vs other replies (pp)"})
    st.dataframe(display, hide_index=True, use_container_width=True)
    st.info(f"For this cell, the study's omnibus score-spread test has adjusted q={info.q_score:.4g}; "
            f"the full W/D/B distribution test has adjusted q={info.q_distribution:.4g}. "
            "These are observational associations, not proof that a reply causes a result.")
    st.caption("Eligibility in the underlying study: at least 200 observed games per reply and rating bands >=1200.")


def show_research() -> None:
    st.title("Research design")
    st.write("The project evaluates two questions using sampled rated-standard Lichess games from March 2025.")
    with st.expander("H1 · First-move advantage", expanded=True):
        st.markdown("**Null hypothesis (H0):** White's expected score is 50%.  \n"
                    "**Alternative (H1):** White's expected score is greater than 50%.")
        st.latex(r"\text{White Score} = \frac{W + D/2}{N}")
        st.write("The primary estimate uses inverse-probability weights to account for the sampling design. "
                 "The analysis also reports bootstrap confidence intervals, null simulations, rating and speed subgroups, "
                 "and shared-player sensitivity analyses.")
    with st.expander("H2 · Black's immediate reply", expanded=True):
        st.write("Within first-move, speed and rating-band cells after 1.e4 or 1.d4, the study compares eligible Black replies. "
                 "It tests both the spread in White scores and the full win/draw/loss distribution. Separate "
                 "Benjamini–Hochberg corrections are used for the two families of tests.")
    with st.expander("Data collection and sampling"):
        st.write("The validated dataset contains 836,070 sampled games from March 1–31, 2025. "
                 "The source dump contained 97,512,351 games scanned. Sampling used a 1% base rate with "
                 "10% overrides for Classical and selected rating bands. The primary analysis uses inverse-probability weighting.")
    with st.expander("Important limitations"):
        st.markdown("- One platform and one month of rated-standard online games.\n"
                    "- Observational data: opening choice and player characteristics are not randomly assigned.\n"
                    "- Repeated players can make games statistically dependent.\n"
                    "- H2 findings are sensitive to rating restrictions, coverage and reply thresholds.\n"
                    "- The study does not establish causal opening recommendations or full-year results.")
    st.markdown("### Data source")
    st.markdown("[Lichess monthly game database](https://database.lichess.org/)")
    st.caption("This website presents the existing research outputs. It does not modify or rerun the original study pipeline.")


def show_figures() -> None:
    st.title("Research figures")
    st.write("The following figures are the original visual outputs exported by the research pipeline.")
    figures = [
        ("fig01_game_outcomes.png", "Game outcomes"),
        ("h1_score_confidence_intervals.png", "H1 · White Score confidence intervals"),
        ("fig02_score_by_band.png", "White Score by rating band"),
        ("fig03_score_by_speed.png", "White Score by time control"),
        ("fig07_replies_e4.png", "H2 · Black replies after 1.e4"),
        ("fig08_replies_d4.png", "H2 · Black replies after 1.d4"),
        ("fig09_reply_effect_heatmap.png", "H2 · Reply score spread heatmap"),
        ("fig10_h2_null_spread.png", "H2 · Null simulation examples"),
    ]
    for i in range(0, len(figures), 2):
        cols = st.columns(2)
        for col, (filename, caption) in zip(cols, figures[i:i+2]):
            with col:
                path = FIGURES / filename
                if path.exists():
                    st.image(str(path), caption=caption, use_container_width=True)
                else:
                    st.warning(f"Missing figure: {filename}")


def show_about() -> None:
    st.title("About the project")
    st.write("White Lies is a collaborative research project combining chess, statistics and data analysis.")
    st.markdown("### The team")
    st.info("Replace the four placeholders below with the names and agreed contribution descriptions of all team members before publishing.")
    team = ["Team member 1", "Team member 2", "Team member 3", "Team member 4"]
    cols = st.columns(4)
    for col, member in zip(cols, team):
        with col:
            st.markdown(f"<div class='metric-card'><div class='metric-value' style='font-size:1.1rem'>{member}</div>"
                        "<div class='metric-note'>Add name and contribution</div></div>", unsafe_allow_html=True)
    st.markdown("### Scope")
    st.write("This site is a presentation layer for the March 2025 study. The research source code, raw data, "
             "results and original figures remain in their existing project locations.")
    st.markdown("### A note on interpretation")
    st.write("Statistical significance does not automatically imply a large practical advantage. "
             "The results describe the studied population and should not be generalized beyond the documented scope.")


PAGES = {
    "Home": show_home,
    "H1 · First-move advantage": show_h1,
    "H2 · Black's first reply": show_h2,
    "Research & methodology": show_research,
    "Figures": show_figures,
    "About the team": show_about,
}

with st.sidebar:
    st.markdown("# ♟ WHITE LIES")
    st.caption("Chess × Data × Probability")
    page = st.radio("Navigate", list(PAGES.keys()), label_visibility="collapsed")
    st.divider()
    st.caption("Research period: March 2025")
    st.caption("Data source: Lichess")

try:
    PAGES[page]()
except FileNotFoundError as exc:
    st.error(str(exc))
    st.info("Run the website from the project root and keep the existing results/ and figures/ folders in place.")
except (KeyError, ValueError, pd.errors.ParserError) as exc:
    st.error(f"The dashboard could not read one of the research artifacts: {exc}")
    st.info("Check that the original results/ files have not been renamed or moved.")
