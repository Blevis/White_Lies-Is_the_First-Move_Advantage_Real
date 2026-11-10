#!/usr/bin/env python3
"""Stream a Lichess monthly PGN dump (.pgn.zst) over HTTP and filter it on the fly.

The dump is never stored: bytes are decompressed as they arrive, games are filtered one at a
time, and only the *kept* games are written (compact CSV, optionally raw PGN). Stop early with
--limit, --quota-per-cell or --max-gb, so you pay only for the prefix of the file you need.

Filters
  * more than --min-moves full moves (default 10  => at least 11)
  * no resignations
  * speed, termination type, valid ratings (anonymous/unrated '?' games dropped)

Resignation detection. Lichess dumps have no explicit 'resign' flag: Termination is one of
Normal / Time forfeit / Abandoned / Rules infraction, and 'Normal' covers checkmate, stalemate,
draws AND resignations. A game is therefore treated as a resignation iff
    Termination == Normal  AND  Result is decisive (1-0 / 0-1)  AND  last move is not mate ('#').
Draws, checkmates and time forfeits are kept; abandoned/rules-infraction games are dropped by
default (--keep-terminations).

Usage
  python fetch_games.py --month 2026-09 --quota-per-cell 20000 --max-gb 4 --out data/games.csv
  python fetch_games.py --input local_sample.pgn.zst --limit 1000      # local file, same logic
"""
import argparse, bisect, csv, io, os, re, sys, time
import requests
import zstandard as zstd

URL = "https://database.lichess.org/standard/lichess_db_standard_rated_{month}.pgn.zst"
BANDS = [0, 1000, 1200, 1400, 1600, 1800, 2000, 2200, 2500]   # lower bounds, as in explorer.py
DECISIVE = {"1-0", "0-1"}
RESULTS = {"1-0", "0-1", "1/2-1/2"}
HDR = re.compile(r'^\[(\w+) "(.*)"\]$')
COMMENT = re.compile(r"\{[^}]*\}")
MOVENUM = re.compile(r"\d+\.+")
LASTNUM = re.compile(r"(\d+)\.")
SPEED = re.compile(r"Rated (\S+)")


class Counting:
    """Wraps a raw stream and counts compressed bytes consumed (for --max-gb and progress)."""
    def __init__(self, raw):
        self.raw, self.n = raw, 0
    def read(self, size=-1):
        b = self.raw.read(size)
        self.n += len(b)
        return b


def open_stream(src):
    if src.startswith("http"):
        r = requests.get(src, stream=True, timeout=60,
                         headers={"User-Agent": "chess-white-advantage-uni-project"})
        r.raise_for_status()
        return Counting(r.raw)
    return Counting(open(src, "rb"))


def records(fh):
    """Yield one list of non-empty lines per game."""
    cur = []
    for line in fh:
        line = line.rstrip("\n")
        if line.startswith("[Event ") and cur:
            yield cur
            cur = []
        if line:
            cur.append(line)
    if cur:
        yield cur


def analyse(rec):
    """-> (headers, movetext) for one record."""
    h, mt = {}, []
    for ln in rec:
        m = HDR.match(ln)
        if m:
            h[m.group(1)] = m.group(2)
        else:
            mt.append(ln)
    return h, " ".join(mt)


def band_of(r):
    return BANDS[bisect.bisect_right(BANDS, r) - 1]


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    src = ap.add_mutually_exclusive_group(required=True)
    src.add_argument("--month", help="YYYY-MM of the standard rated dump")
    src.add_argument("--url")
    src.add_argument("--input", help="local .pgn.zst file (same code path; useful for testing)")
    ap.add_argument("--speeds", default="bullet,blitz,rapid,classical")
    ap.add_argument("--min-moves", type=int, default=10, help="keep games with MORE than this many full moves")
    ap.add_argument("--include-resignations", action="store_true",
                    help="disable the resignation filter (e.g. to compare against explorer counts)")
    ap.add_argument("--keep-terminations", default="Normal,Time forfeit")
    ap.add_argument("--band-by", choices=["avg", "min", "max"], default="avg",
                    help="which rating defines the band (verify against the explorer's semantics)")
    ap.add_argument("--quota-per-cell", type=int, help="max kept games per (speed, band); stop when all cells are full")
    ap.add_argument("--limit", type=int, help="stop after this many kept games")
    ap.add_argument("--max-gb", type=float, help="stop after this many COMPRESSED GB have been read")
    ap.add_argument("--out", default="data/games_sample.csv")
    ap.add_argument("--pgn-out", help="optionally also write kept games as PGN")
    a = ap.parse_args()

    speeds = {s.strip().lower() for s in a.speeds.split(",")}
    terms = {t.strip() for t in a.keep_terminations.split(",")}
    url = a.input or a.url or URL.format(month=a.month)
    src_stream = open_stream(url)
    dctx = zstd.ZstdDecompressor(max_window_size=2 ** 31)     # dumps use a long window
    fh = io.TextIOWrapper(dctx.stream_reader(src_stream), encoding="utf-8", errors="replace", newline="")

    cells = {(s, b): 0 for s in speeds for b in BANDS}
    rej = dict(speed=0, rating=0, termination=0, result=0, short=0, resignation=0, quota=0)
    seen = kept = 0
    t0 = time.time()
    pgn = open(a.pgn_out, "w", encoding="utf-8") if a.pgn_out else None
    os.makedirs(os.path.dirname(a.out) or ".", exist_ok=True)
    cols = ["game_id", "speed", "time_control", "white_elo", "black_elo", "band", "result",
            "termination", "n_moves", "eco", "opening", "first4"]
    out = open(a.out, "w", newline="", encoding="utf-8")
    w = csv.writer(out)
    w.writerow(cols)

    def done():
        return ((a.limit and kept >= a.limit)
                or (a.max_gb and src_stream.n >= a.max_gb * 1e9)
                or (a.quota_per_cell and all(v >= a.quota_per_cell for v in cells.values())))

    try:
        for rec in records(fh):
            seen += 1
            if seen % 200_000 == 0:
                print(f"  seen {seen:,} | kept {kept:,} | {src_stream.n/1e9:.2f} GB | {time.time()-t0:.0f}s",
                      file=sys.stderr)
                if done():
                    break
            h, mt = analyse(rec)
            m = SPEED.match(h.get("Event", ""))
            speed = m.group(1).lower() if m else None
            if speed not in speeds:
                rej["speed"] += 1; continue
            try:
                we, be = int(h["WhiteElo"]), int(h["BlackElo"])
            except (KeyError, ValueError):
                rej["rating"] += 1; continue
            term, res = h.get("Termination", "Normal"), h.get("Result", "*")
            if term not in terms:
                rej["termination"] += 1; continue
            if res not in RESULTS:
                rej["result"] += 1; continue
            clean = COMMENT.sub(" ", mt)
            nums = LASTNUM.findall(clean)
            n_moves = int(nums[-1]) if nums else 0
            if n_moves <= a.min_moves:
                rej["short"] += 1; continue
            sans = [t for t in MOVENUM.sub(" ", clean).split() if not t.startswith("$") and t not in RESULTS | {"*"}]
            if not a.include_resignations and term == "Normal" and res in DECISIVE and not (sans and sans[-1].endswith("#")):
                rej["resignation"] += 1; continue
            rating = {"avg": (we + be) // 2, "min": min(we, be), "max": max(we, be)}[a.band_by]
            cell = (speed, band_of(rating))
            if a.quota_per_cell and cells[cell] >= a.quota_per_cell:
                rej["quota"] += 1; continue
            cells[cell] += 1
            kept += 1
            w.writerow([h.get("Site", "").rsplit("/", 1)[-1], speed, h.get("TimeControl", ""), we, be,
                        cell[1], res, term, n_moves, h.get("ECO", ""), h.get("Opening", ""),
                        " ".join(sans[:4])])
            if pgn:
                pgn.write("\n".join(rec) + "\n\n")
            if done():
                break
    except (requests.exceptions.RequestException, zstd.ZstdError) as e:
        print(f"stream interrupted ({type(e).__name__}: {e}); partial output kept", file=sys.stderr)
    finally:
        out.close()
        if pgn:
            pgn.close()

    print(f"\nread {src_stream.n/1e9:.3f} GB compressed, {seen:,} games, kept {kept:,} -> {a.out}")
    print("rejected:", {k: v for k, v in rej.items() if v})
    print("per cell (speed, band):", {f"{s}/{b}": v for (s, b), v in sorted(cells.items()) if v})
    if a.quota_per_cell:
        unfilled = [f"{s}/{b}" for (s, b), v in sorted(cells.items()) if v < a.quota_per_cell]
        if unfilled:
            print("cells below quota (rare cells may never fill; raise --max-gb or use fewer cells):", unfilled)


if __name__ == "__main__":
    main()