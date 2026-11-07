"""Scrape Wikipedia's 'List of ECO codes' -> tidy (eco, moves, article, family) table.

Page layout (verified from a screenshot, Nov 2026): columns Code | Moves | Main article,
section rows like 'A (up-arrow)', footnote <sup> markers in cells, multi-line <br> move cells.
'List of chess openings' redirects to this page.
"""
import pathlib, re
import pandas as pd
import requests
from lxml import html as LH

URL = "https://en.wikipedia.org/wiki/List_of_ECO_codes"
UA = {"User-Agent": "chess-white-advantage-uni-project (student coursework)"}
CODE_RE = re.compile(r"^\s*([A-E]\d\d)\b")
FIRST_PLIES = re.compile(r"1\.\s*([^\s]+)(?:\s+([^\s]+))?")


def family_from_eco(eco: str) -> str:
    """Fallback: ECO letter/number -> family (ECO is structural, so only approximate)."""
    L, n = eco[0], int(eco[1:3])
    if L == "A":
        return "flank" if n < 40 else "semi_closed"
    if L == "B":
        return "semi_open"
    if L == "C":
        return "semi_open" if n < 20 else "open"      # C00-C19 French
    if L == "D":
        return "closed" if n < 70 else "semi_closed"   # D70+ Grunfeld
    return "semi_closed"                               # E: Indian systems


def family_from_moves(line: str):
    """First two plies -> family, matching the explorer position splits. None if ambiguous."""
    m = FIRST_PLIES.match(line or "")
    if not m:
        return None
    w, b = m.groups()
    if b is not None and re.match(r"\d+\.", b):        # '1.e4 2.Nf3'-style: no black move given
        b = None
    if w == "e4":
        return None if b is None else ("open" if b == "e5" else "semi_open")
    if w == "d4":
        return None if b is None else ("closed" if b == "d5" else "semi_closed")
    return "flank"


def family(eco, moves_line):
    return family_from_moves(moves_line) or family_from_eco(eco)


def fetch_html(cache="data/wiki_openings.html", refresh=False):
    p = pathlib.Path(cache)
    if p.exists() and not refresh:
        return p.read_text(encoding="utf-8")
    r = requests.get(URL, headers=UA, timeout=30)
    r.raise_for_status()
    p.parent.mkdir(exist_ok=True)
    p.write_text(r.text, encoding="utf-8")
    return r.text


def _lines(cell):
    """Cell text as a list of lines: footnote <sup> removed, <br> -> newline."""
    for el in cell.xpath(".//sup"):
        el.drop_tree()
    for br in cell.xpath(".//br"):
        br.tail = "\n" + (br.tail or "")
    txt = cell.text_content()
    return [re.sub(r"\s+", " ", l).strip() for l in txt.split("\n") if l.strip()]


def parse_openings(html: str) -> pd.DataFrame:
    root = LH.fromstring(html)
    rows = []
    for table in root.xpath("//table"):
        heads = [re.sub(r"\s+", " ", th.text_content()).strip().lower() for th in table.xpath(".//th")]
        if not (any(h.startswith("code") for h in heads) and any(h.startswith("moves") for h in heads)):
            continue
        for tr in table.xpath(".//tr"):
            cells = tr.xpath("./th|./td")
            if len(cells) < 2:
                continue                                # section rows ('A (up-arrow)')
            m = CODE_RE.match(cells[0].text_content())
            if not m:
                continue                                # header row
            moves = _lines(cells[1])
            art = _lines(cells[2]) if len(cells) > 2 else []
            eco = m.group(1)
            first = moves[0] if moves else ""
            rows.append(dict(eco=eco, moves=" / ".join(moves), article=art[0] if art else None,
                             family_eco=family_from_eco(eco), family_moves=family_from_moves(first),
                             family=family(eco, first)))
    if not rows:
        raise RuntimeError("No Code/Moves table found: page layout changed? (try refresh=True)")
    return pd.DataFrame(rows).drop_duplicates().reset_index(drop=True)


def load_openings(refresh=False):
    return parse_openings(fetch_html(refresh=refresh))