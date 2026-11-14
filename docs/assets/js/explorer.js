/* White Lies: static views of exported results. No inference is computed here. */
(() => {
  "use strict";
  const source = document.currentScript && document.currentScript.src;
  const DATA_URL = source ? new URL("../data/research.json", source).href : "../assets/data/research.json";
  const nf = new Intl.NumberFormat("en-US");
  const pct = (value, digits = 3) => Number.isFinite(value) ? `${(value * 100).toFixed(digits)}%` : "Unavailable";
  const count = value => Number.isFinite(value) ? nf.format(value) : "—";
  const esc = value => String(value ?? "").replace(/[&<>"']/g, c => ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c]));
  const bandLabel = value => Number(value) === 0 ? "Below 1000" : Number(value) === 2500 ? "2500+" : `${value}–${Number(value) === 2200 ? 2499 : Number(value) + 199}`;
  const speeds = ["blitz", "rapid", "classical"];
  const bands = [0, 1000, 1200, 1400, 1600, 1800, 2000, 2200, 2500];
  let dataPromise;
  let instance = 0;
  const getData = () => dataPromise ||= fetch(DATA_URL).then(response => {
    if (!response.ok) throw new Error(`Aggregate data returned HTTP ${response.status}`);
    return response.json();
  }).then(data => {
    if (data.schema_version !== 1 || !data.h1?.rows || !data.h2?.replies) throw new Error("Unsupported aggregate data format");
    return data;
  });
  const option = (value, label = value) => `<option value="${esc(value)}">${esc(label)}</option>`;
  const select = (id, label, options, value) => `<label class="wl-control" for="${id}"><span>${label}</span><select id="${id}">${options.map(o => option(o[0], o[1])).join("")}</select></label>`;
  const empty = message => `<div class="wl-empty" role="status"><strong>No tested estimate for this selection.</strong><p>${message}</p></div>`;
  const chartNote = text => `<p class="wl-chart-note">${text}</p>`;

  // All intervals are read from published exports. Axes always contain the 50% reference.
  function intervals(rows, title, {compact = false} = {}) {
    const values = rows.filter(row => Number.isFinite(row.score) && Number.isFinite(row.lo) && Number.isFinite(row.hi));
    if (!values.length) return empty("No confidence interval was exported for this combination.");
    const min = Math.min(.50, ...values.map(row => row.lo));
    const max = Math.max(.52, ...values.map(row => row.hi));
    const pad = Math.max(.0025, (max - min) * .08);
    const lower = Math.max(0, Math.floor((min - pad) * 1000) / 1000);
    const upper = Math.min(1, Math.ceil((max + pad) * 1000) / 1000);
    const pos = value => ((value - lower) / (upper - lower) * 100).toFixed(4);
    const tickValues = [lower, lower + (upper-lower)*.25, lower+(upper-lower)*.5, lower+(upper-lower)*.75, upper];
    return `<div class="wl-ci ${compact ? "wl-ci-compact" : ""}" role="group" aria-label="${esc(title)}">
      <div class="wl-ci-key"><span><i class="wl-key-dot"></i> White score</span><span><i class="wl-key-line"></i> 95% interval</span><span>Dashed line: 50%</span></div>
      ${values.map(row => {
        const description = `${row.label}: White score ${pct(row.score)}, 95% confidence interval ${pct(row.lo)} to ${pct(row.hi)}, ${count(row.N)} sampled games${row.status === "insufficient" ? "; insufficient for hypothesis testing" : ""}.`;
        return `<div class="wl-ci-row${row.status === "insufficient" ? " wl-descriptive" : ""}" tabindex="0" aria-label="${esc(description)}">
          <div class="wl-ci-label">${esc(row.label)}<small>n = ${count(row.N)}${row.status === "insufficient" ? " · descriptive" : ""}</small></div>
          <div class="wl-ci-track" aria-hidden="true"><span class="wl-ci-reference" style="left:${pos(.5)}%"></span><span class="wl-ci-range" style="left:${pos(row.lo)}%;width:${pos(row.hi)-pos(row.lo)}%"></span><span class="wl-ci-point" style="left:${pos(row.score)}%"></span></div>
          <strong class="wl-ci-value">${pct(row.score)}</strong>
          <span class="wl-ci-tooltip" role="tooltip">95% CI ${pct(row.lo)}–${pct(row.hi)} · n = ${count(row.N)}${row.status === "insufficient" ? " · descriptive only" : ""}</span>
        </div>`;
      }).join("")}
      <div class="wl-ci-axis" aria-hidden="true"><span></span><div>${tickValues.map((value, i) => `<span style="left:${i*25}%">${pct(value, upper-lower > .2 ? 0 : 1)}</span>`).join("")}</div><span></span></div>
      <p class="wl-axis-caption">White score (%) · interval scale expands to include all displayed uncertainty</p>
    </div>`;
  }

  function outcomes(row) {
    const parts = [
      ["White win", row.white_win_rate, "white"],
      ["Draw", row.draw_rate, "draw"],
      ["Black win", row.black_win_rate, "black"]
    ];
    return `<div class="wl-outcomes" role="img" aria-label="${esc(parts.map(p=>`${p[0]} ${pct(p[1])}`).join(", "))}">${parts.map(p=>`<span class="wl-outcome-${p[2]}" style="width:${p[1]*100}%" title="${p[0]}: ${pct(p[1])}"></span>`).join("")}</div>
      <dl class="wl-outcome-legend">${parts.map(p=>`<div><dt><i class="wl-outcome-${p[2]}"></i>${p[0]}</dt><dd>${pct(p[1])}</dd></div>`).join("")}</dl>
      <p class="wl-chart-note">${row.weighted ? "Inverse-probability-weighted outcome shares" : "Raw sample outcome shares"}. White score = White win share + half the draw share. These percentages are not raw game counts.</p>`;
  }

  function initExplorer(root, data) {
    const id = `wl-ex-${++instance}`;
    root.innerHTML = `<div class="wl-dashboard-toolbar"><div><span class="wl-overline">RESEARCH EXPLORER</span><p>March 2025 · frozen research outputs</p></div>${select(`${id}-category`, "View results", [["all","All findings"],["h1","H1 · White score"],["h2","H2 · Opening replies"]])}</div>
      <p class="wl-data-status" role="status" aria-live="polite" data-status></p>
      <div data-h1-panel>
        <div class="wl-filter-panel"><div class="wl-section-label">H1 / Select a population</div><div class="wl-filter-grid">
          ${select(`${id}-speed`,"Time control",[["all","All time controls"],...speeds.map(s=>[s,s[0].toUpperCase()+s.slice(1)])])}
          ${select(`${id}-band`,"Mean-rating band",[["all","All rating bands"],...bands.map(b=>[b,bandLabel(b)])])}
          ${select(`${id}-weight`,"Estimator",[["weighted","Weighted · primary"],["raw","Unweighted · whole sample"]])}
          <button class="wl-ui-button wl-filter-reset" type="button" data-reset>Reset filters</button>
        </div><p class="wl-control-hint">Unweighted intervals are available for the whole sample only. Mean-rating bands use both players’ recorded Elo.</p></div>
        <div class="wl-kpis" data-kpis></div>
        <section class="wl-chart-card"><div class="wl-card-heading"><span class="wl-chart-index">01</span><div><h2>White scoring advantage</h2><p data-selected-label></p></div></div><div data-chart-primary></div><p class="wl-caution" data-h1-status></p><p class="wl-chart-note">The point is expected score, with a win worth 1, a draw ½ and a loss 0. The line is the exported 95% confidence interval. Source: <code>h1_results.csv</code> / <code>h1_summary.json</code>.</p></section>
        <div class="wl-chart-grid"><section class="wl-chart-card"><div class="wl-card-heading"><span class="wl-chart-index">02</span><div><h2>By time control</h2><p data-speed-caption></p></div></div><div data-chart-speed></div><p class="wl-chart-note">Weighted comparisons at the selected rating band. Overlapping intervals do not establish equality between time controls. Source: <code>h1_results.csv</code>.</p></section>
        <section class="wl-chart-card"><div class="wl-card-heading"><span class="wl-chart-index">04</span><div><h2>Three outcomes. One score.</h2><p data-outcome-caption></p></div></div><div data-chart-outcome></div><p class="wl-chart-note">Outcome shares have no intervals in this view. Source: <code>h1_results.csv</code> / <code>h1_summary.json</code>.</p></section></div>
        <section class="wl-chart-card"><div class="wl-card-heading"><span class="wl-chart-index">03</span><div><h2>Across rating bands</h2><p data-band-caption></p></div></div><div data-chart-band></div><p class="wl-chart-note">Weighted estimates. There is no monotonic pattern across rating bands. Sparse groups remain descriptive; uncertainty is shown rather than hidden. Source: <code>h1_results.csv</code>.</p></section>
        <section class="wl-chart-card"><div class="wl-card-heading"><span class="wl-chart-index">06</span><div><h2>How sensitive is the finding?</h2><p>Whole-study sensitivity analyses · independent of the filters above</p></div></div><div data-chart-robustness></div><p class="wl-caution"><strong>Game length changes the magnitude.</strong> Requiring at least 40 plies reduces the weighted score from 51.776% to 50.769%. This restriction changes the population under analysis. A ply is one player’s move.</p><p class="wl-chart-note">Intervals and sample sizes are copied from the reported analyses. Equal-rating standardization uses dyadic covariance; the other displayed intervals use the reported bootstrap. Source: <code>robustness_results.csv</code> and <code>h1_summary.json</code>.</p></section>
      </div><div data-h2-panel><div data-opening-module></div></div>`;
    const controls = Object.fromEntries(["category","speed","band","weight"].map(name=>[name,root.querySelector(`#${id}-${name}`)]));
    const query = selector => root.querySelector(selector);
    function renderH1() {
      const speed = controls.speed.value;
      const band = controls.band.value;
      const all = speed === "all" && band === "all";
      const rawOption = controls.weight.querySelector('option[value="raw"]');
      rawOption.disabled = !all;
      let resetMessage = "";
      if (!all && controls.weight.value === "raw") { controls.weight.value = "weighted"; resetMessage = "Unweighted subgroup intervals are unavailable; showing the published weighted result. "; }
      const raw = controls.weight.value === "raw";
      const row = raw ? data.h1.summary.raw : data.h1.rows.find(r => r.speed === speed && (band === "all" ? r.band === -1 : r.band === Number(band)));
      const label = `${speed === "all" ? "All time controls" : speed[0].toUpperCase()+speed.slice(1)} · ${band === "all" ? "all rating bands" : bandLabel(band)}`;
      query("[data-status]").textContent = `${resetMessage}Showing ${raw ? "unweighted sample" : "weighted"} H1 results for ${label.toLowerCase()}. H2 uses its own cell filters below.`;
      if (!row) {
        query("[data-chart-primary]").innerHTML = empty("This estimate is not present in the validated exports.");
        return;
      }
      query("[data-kpis]").innerHTML = [["Sampled games",count(row.N)],["White score",pct(row.score)],["Above 50%",`${row.score>=.5?"+":""}${((row.score-.5)*100).toFixed(3)} pp`],["Estimator",raw?"Unweighted":"IPW"]].map(([label,value])=>`<div class="wl-kpi"><span>${label}</span><strong>${value}</strong></div>`).join("");
      query("[data-selected-label]").textContent = `${label} · ${raw ? "raw sample estimate" : "inverse-probability weighting"}`;
      query("[data-chart-primary]").innerHTML = intervals([{...row,label:"Selected population"}],"White score and 95% confidence interval");
      query("[data-h1-status]").textContent = row.status === "insufficient" ? "Descriptive only: this group has insufficient observed games or decisive outcomes for the prespecified H1 test. It is not evidence for or against equality." : raw ? "The raw estimate describes the deliberately oversampled study sample. It does not adjust for the different collection probabilities." : "The weighted estimate targets the eligible source-game population under the sampling assumptions. N is the observed sample count, not a weighted population total.";
      const speedRows = speeds.map(s=>data.h1.rows.find(r=>r.speed===s && (band==="all"?r.group_type==="speed":r.group_type==="cell"&&r.band===Number(band)))).filter(Boolean);
      query("[data-chart-speed]").innerHTML = intervals(speedRows.map(r=>({...r,label:r.speed[0].toUpperCase()+r.speed.slice(1)})),"White score by time control",{compact:true});
      query("[data-speed-caption]").textContent = band==="all" ? "All rating bands · weighted" : `Rating ${bandLabel(band)} · weighted`;
      const bandRows = data.h1.rows.filter(r=>speed==="all"?r.group_type==="band":r.group_type==="cell"&&r.speed===speed).sort((a,b)=>a.band-b.band);
      query("[data-chart-band]").innerHTML = intervals(bandRows.map(r=>({...r,label:bandLabel(r.band)})),"White score by mean-rating band");
      query("[data-band-caption]").textContent = `${speed==="all"?"All time controls":speed} · weighted`;
      query("[data-outcome-caption]").textContent = `${label} · ${raw?"unweighted":"weighted"}`;
      query("[data-chart-outcome]").innerHTML = outcomes(row);
    }
    controls.category.addEventListener("change",()=>{
      query("[data-h1-panel]").hidden=controls.category.value==="h2";
      query("[data-h2-panel]").hidden=controls.category.value==="h1";
      query("[data-status]").textContent = controls.category.value==="all"?"Showing both hypothesis sections. Each section has separate population filters.":`Showing ${controls.category.value.toUpperCase()} results.`;
    });
    for(const name of ["speed","band","weight"]) controls[name].addEventListener("change",renderH1);
    query("[data-reset]").addEventListener("click",()=>{controls.speed.value="all";controls.band.value="all";controls.weight.value="weighted";renderH1();});
    const scenarios = ["Unweighted sample","Absolute rating difference <= 25","Exclude time forfeits","At least 10 plies","At least 40 plies"];
    const shortLabels = {"Unweighted sample":"Unweighted sample","Absolute rating difference <= 25":"Rating gap ≤ 25","Exclude time forfeits":"No time forfeits","At least 10 plies":"At least 10 plies","At least 40 plies":"At least 40 plies"};
    const robust = [{...data.h1.summary.primary,label:"Primary · weighted"},{...data.h1.summary.rating_adjusted,label:"Equal-rating model"},...scenarios.map(s=>data.robustness.find(r=>r.hypothesis==="H1"&&r.scenario===s)).filter(Boolean).map(r=>({...r,label:shortLabels[r.scenario]}))];
    query("[data-chart-robustness]").innerHTML = intervals(robust,"H1 robustness and sensitivity estimates");
    initOpenings(query("[data-opening-module]"),data);
    renderH1();
  }

  function boardMarkup(first, reply, initial) {
    const board = {};
    const back = ["R","N","B","Q","K","B","N","R"];
    for(let file=0;file<8;file++) {
      const letter=String.fromCharCode(97+file);
      board[`${letter}1`]=`w${back[file]}`;board[`${letter}2`]="wP";
      board[`${letter}8`]=`b${back[file]}`;board[`${letter}7`]="bP";
    }
    const highlights = [];
    if(!initial) {
      const from=`${first[0]}2`; delete board[from];board[first]="wP";highlights.push(from,first);
      if(reply) {
        const knightFrom={Na6:"b8",Nc6:"b8",Nf6:"g8",Nh6:"g8"};
        const from=knightFrom[reply]||( /^[a-h][56]$/.test(reply)?`${reply[0]}7`:null);
        const to=knightFrom[reply]?reply.slice(1):reply;
        if(from&&board[from]) {board[to]=board[from];delete board[from];highlights.push(from,to);}
      }
    }
    const symbols={wK:"♔",wQ:"♕",wR:"♖",wB:"♗",wN:"♘",wP:"♙",bK:"♚",bQ:"♛",bR:"♜",bB:"♝",bN:"♞",bP:"♟"};
    const names={K:"king",Q:"queen",R:"rook",B:"bishop",N:"knight",P:"pawn"};
    const notation=initial?"Initial position":`1.${first}${reply?` ${reply}`:""}`;
    let html=`<div class="wl-chessboard" role="img" aria-label="${esc(`Chessboard, White at bottom. ${notation}. ${initial?"All pieces on their starting squares.":`Highlighted squares show the moves. White pawn moved from ${first[0]}2 to ${first}.`}${!initial&&reply?` Black played ${reply}.`:""}`)}">`;
    for(let rank=8;rank>=1;rank--) for(let file=0;file<8;file++) {
      const square=`${String.fromCharCode(97+file)}${rank}`;
      const piece=board[square];
      html+=`<span class="wl-square ${(file+rank)%2===1?"wl-square-dark":"wl-square-light"}${highlights.includes(square)?" wl-square-moved":""}" data-square="${square}" data-piece="${piece||""}" aria-hidden="true">${piece?`<span class="wl-piece ${piece[0]==="w"?"wl-piece-white":"wl-piece-black"}" title="${esc(`${square}: ${piece[0]==="w"?"White":"Black"} ${names[piece[1]]}`)}">${symbols[piece]}</span>`:""}${file===0?`<small class="wl-rank">${rank}</small>`:""}${rank===1?`<small class="wl-file">${String.fromCharCode(97+file)}</small>`:""}</span>`;
    }
    return html+`</div><p class="wl-board-notation" aria-live="polite">${notation}</p>`;
  }

  function initOpenings(root, data) {
    const id=`wl-open-${++instance}`;
    root.innerHTML=`<section class="wl-chart-card wl-opening-card"><div class="wl-card-heading"><span class="wl-chart-index">05</span><div><h2>Black’s first reply</h2><p>A move on the board. An observed group in the data.</p></div></div>
      <div class="wl-filter-grid wl-opening-filters">${select(`${id}-first`,"White’s first move",[["e4","1.e4"],["d4","1.d4"]])}${select(`${id}-speed`,"Time control",speeds.map(s=>[s,s[0].toUpperCase()+s.slice(1)]))}${select(`${id}-band`,"Mean-rating band",bands.map(b=>[b,bandLabel(b)]))}${select(`${id}-reply`,"Black’s immediate reply",[["all","All tested replies"]])}</div>
      <div class="wl-opening-status" role="status" aria-live="polite" data-opening-status></div>
      <div class="wl-opening-layout"><aside class="wl-board-panel" aria-label="Explanatory chess position"><div data-board></div><div class="wl-board-buttons"><button type="button" class="wl-ui-button" data-board-reset>Initial position</button><button type="button" class="wl-ui-button" data-board-show>Show selected moves</button></div><p class="wl-chart-note">White is at the bottom; a1 is dark. This board illustrates the selected grouping. It is not an engine evaluation or a recommendation.</p></aside>
        <div class="wl-reply-panel"><div class="wl-test-results" data-cell-results></div><div data-reply-chart></div><p class="wl-chart-note">Points are White scores. Intervals are marginal 95% intervals, not simultaneous or adjusted for selecting extremes. Within each cell, sampling weights are constant. Omnibus tests concern the whole eligible reply set, not individual replies.</p></div></div>
      <div class="wl-table-tools"><label class="wl-control" for="${id}-search"><span>Search tested reply notation</span><input type="search" id="${id}-search" placeholder="For example, Nf6" autocomplete="off"></label><span class="wl-control-hint">Select a column heading to sort. Default order is notation.</span></div>
      <div class="wl-table-scroll" tabindex="0" role="region" aria-label="Opening replies table"><table class="wl-data-table"><caption data-table-caption></caption><thead><tr><th scope="col" aria-sort="ascending"><button type="button" data-sort="reply">Reply <span aria-hidden="true">↕</span></button></th><th scope="col" aria-sort="none"><button type="button" data-sort="N">Sample n <span aria-hidden="true">↕</span></button></th><th scope="col" aria-sort="none"><button type="button" data-sort="score">White score <span aria-hidden="true">↕</span></button></th><th scope="col">95% interval</th><th scope="col">Status</th></tr></thead><tbody data-reply-table></tbody></table></div>
      <p class="wl-caution">Observed reply differences can reflect player selection and rating imbalance. Sorting does not identify the objectively best defense. Near-equal-rating sensitivity leaves only 1 of 28 score-spread rejections.</p>
      <p class="wl-chart-note">Sources: <code>h2_results.csv</code>, <code>h2_reply_scores.csv</code>, <code>h2_summary.json</code>. Bands below 1200 and replies with fewer than 200 observed games are excluded from primary H2; a tested cell needs at least two eligible replies. All 35 eligible cells belong to each test’s separate Benjamini–Hochberg correction family.</p></section>`;
    const q=selector=>root.querySelector(selector);
    const controls=Object.fromEntries(["first","speed","band","reply","search"].map(name=>[name,q(`#${id}-${name}`)]));
    controls.band.value="1600";
    let sortKey="reply",sortDirection=1,rows=[],cell=null,initial=false;
    function renderBoard() { q("[data-board]").innerHTML=boardMarkup(controls.first.value,controls.reply.value==="all"?null:controls.reply.value,initial); }
    function renderTable() {
      const search=controls.search.value.trim().toLowerCase();
      const filtered=rows.filter(r=>r.reply.toLowerCase().includes(search)).sort((a,b)=>sortDirection*(sortKey==="reply"?a.reply.localeCompare(b.reply):a[sortKey]-b[sortKey]));
      q("[data-reply-table]").innerHTML=filtered.length?filtered.map(r=>`<tr><td><button type="button" class="wl-reply-link" data-show-reply="${esc(r.reply)}" aria-label="Show 1.${esc(r.first)} ${esc(r.reply)} on the chessboard">${esc(r.reply)}</button></td><td>${count(r.N)}</td><td>${pct(r.score)}</td><td>${pct(r.lo)}–${pct(r.hi)}</td><td>Eligible · tested cell</td></tr>`).join(""):`<tr><td colspan="5">${rows.length?"No tested reply matches this search.":"No primary tested replies in this cell."}</td></tr>`;
      q("[data-table-caption]").textContent=`${filtered.length} tested ${filtered.length===1?"reply":"replies"} · 1.${controls.first.value} · ${controls.speed.value} · mean rating ${bandLabel(controls.band.value)}`;
    }
    function renderSelection() {
      const selected=controls.reply.value==="all"?rows:rows.filter(r=>r.reply===controls.reply.value);
      q("[data-reply-chart]").innerHTML=rows.length?intervals(selected.map(r=>({...r,label:`1…${r.reply}`})),"White score by Black immediate reply",{compact:true}):empty(Number(controls.band.value)<1200?"The primary H2 design excludes mean-rating bands below 1200. Select a band of 1200 or higher.":"This cell has fewer than two replies meeting the 200-game threshold. Sparse data do not establish equality.");
      initial=false;renderBoard();
    }
    function renderCell() {
      cell=data.h2.cells.find(r=>r.first===controls.first.value&&r.speed===controls.speed.value&&r.band===Number(controls.band.value));
      const allRows=data.h2.replies.filter(r=>r.first===controls.first.value&&r.speed===controls.speed.value&&r.band===Number(controls.band.value));
      rows=allRows.filter(r=>r.tested).sort((a,b)=>a.reply.localeCompare(b.reply));
      const oldReply=controls.reply.value;
      controls.reply.innerHTML=option("all","All tested replies")+rows.map(r=>option(r.reply,`1…${r.reply} · n=${count(r.N)}`)).join("");
      if(rows.some(r=>r.reply===oldReply)) controls.reply.value=oldReply;
      controls.reply.disabled=!rows.length;
      const label=`1.${controls.first.value} · ${controls.speed.value} · rating ${bandLabel(controls.band.value)}`;
      q("[data-opening-status]").textContent=rows.length?`${label}: ${rows.length} tested replies, ${count(cell.included_games)} included sampled games; ${allRows.length-rows.length} observed replies excluded by the primary eligibility rules.`:`${label}: no primary H2 test is available. ${cell ? `${count(cell.total_games)} sampled games were observed in this cell.` : "No observed cell is present in the exported results."}`;
      const p=value=>Number.isFinite(value)?value.toPrecision(4):"Unavailable";
      q("[data-cell-results]").innerHTML=cell?.status==="tested"?`<div><span>Score-spread test</span><strong>${cell.reject_score?"Evidence detected":"Not detected"}</strong><small>BH q = ${p(cell.q_score)}</small></div><div><span>W / D / B distribution</span><strong>${cell.reject_distribution?"Evidence detected":"Not detected"}</strong><small>BH q = ${p(cell.q_distribution)}</small></div>`:`<div><span>Cell eligibility</span><strong>Insufficient for testing</strong><small>No adjusted p-value is available.</small></div>`;
      renderSelection();renderTable();
    }
    for(const key of ["first","speed","band"]) controls[key].addEventListener("change",renderCell);
    controls.reply.addEventListener("change",renderSelection);
    controls.search.addEventListener("input",renderTable);
    q("[data-board-reset]").addEventListener("click",()=>{initial=true;renderBoard();});
    q("[data-board-show]").addEventListener("click",()=>{initial=false;renderBoard();});
    root.addEventListener("click",event=>{
      const sort=event.target.closest("[data-sort]");
      if(sort) {
        sortDirection=sortKey===sort.dataset.sort?-sortDirection:1;sortKey=sort.dataset.sort;
        root.querySelectorAll("[data-sort]").forEach(button=>button.parentElement.setAttribute("aria-sort",button===sort?(sortDirection===1?"ascending":"descending"):"none"));renderTable();
      }
      const move=event.target.closest("[data-show-reply]");
      if(move) {controls.reply.value=move.dataset.showReply;renderSelection();q("[data-opening-status]").textContent=`Showing 1.${controls.first.value} ${controls.reply.value}. The selected reply’s interval is descriptive; cell tests still concern all eligible replies.`;}
    });
    renderCell();
  }

  async function mount() {
    const nodes=[...document.querySelectorAll("[data-wl-explorer], [data-wl-openings], [data-wl-preview]")].filter(n=>!n.dataset.wlReady);
    if(!nodes.length)return;
    nodes.forEach(n=>{n.dataset.wlReady="loading";});
    try {
      const data=await getData();
      nodes.forEach(node=>{
        if(!node.isConnected)return;
        if(node.hasAttribute("data-wl-explorer"))initExplorer(node,data);
        else if(node.hasAttribute("data-wl-openings"))initOpenings(node,data);
        else node.innerHTML=intervals(speeds.map(speed=>data.h1.rows.find(r=>r.group_type==="speed"&&r.speed===speed)).filter(Boolean).map(r=>({...r,label:r.speed[0].toUpperCase()+r.speed.slice(1)})),"Weighted White score by time control",{compact:true})+chartNote("Weighted White score and 95% intervals · observed sample counts · source: h1_results.csv");
        node.dataset.wlReady="true";
      });
    } catch(error) {
      nodes.forEach(node=>{node.dataset.wlReady="error";node.innerHTML=`<div class="wl-empty" role="alert"><strong>The research data could not be loaded.</strong><p>Reload this page or read the full research report from the navigation. The static report and figures remain available.</p><button type="button" class="wl-ui-button" data-retry>Retry data loading</button></div>`;node.querySelector("[data-retry]").addEventListener("click",()=>{dataPromise=null;delete node.dataset.wlReady;mount();});});
      console.error("White Lies explorer:",error.message);
    }
  }
  // Hover/focus details stay open while inspected and can be dismissed without moving focus.
  document.addEventListener("keydown", event => {
    if (event.key !== "Escape") return;
    document.querySelectorAll(".wl-ci-row:hover, .wl-ci-row:focus-within").forEach(row => row.classList.add("wl-tooltip-dismissed"));
  });
  for (const eventName of ["pointerover", "focusin"]) document.addEventListener(eventName, event => {
    const row = event.target.closest?.(".wl-ci-row");
    if (row && !row.contains(event.relatedTarget)) row.classList.remove("wl-tooltip-dismissed");
  });
  if(typeof document$!=="undefined")document$.subscribe(mount);
  else if(document.readyState==="loading")document.addEventListener("DOMContentLoaded",mount);
  else mount();
})();
