#!/usr/bin/env python3
"""Stream ONE Lichess monthly PGN dump (.pgn.zst) over HTTP and write a game-level random sample.

The dump is never stored: bytes are decompressed as they arrive, the whole file is always read
(no early stopping, so the sample covers the entire month), and only sampled games are written.
Intended use: a representative sample of one 2025 month for testing H1 (White's score by rating
band) and H2 (does Black's first reply matter?).

Sampling (deterministic, uniform over the month)
  A game is kept iff  int(md5(game_id).hexdigest()[:8], 16) / 0xFFFFFFFF < rate.
  The hash is a pure function of the Lichess game id, so the same game is always kept or always
  dropped, for any run, any machine, and any prefix of the dump. The check runs right after the
  headers are read, BEFORE any movetext work, so skipped games cost almost nothing.
  rate = max(--sample-rate, every matching --rate-override). A key is a speed name or a band lower
  bound, e.g. "classical=0.10,2200=0.10,2500=0.10" oversamples scarce cells. Because the rate
  depends only on (speed, band), it is CONSTANT inside every (speed, band) cell: within-cell
  comparisons (H2) need no weighting. Pooling across cells (H1 totals) must weight each game by
  1/sample_rate, which is stored on every row.

Filters (every rejection is counted by rule in the manifest)
  speed (--speeds) | rating (both Elos numeric) | result (1-0, 0-1, 1/2-1/2) |
  termination (Normal, Time forfeit) | bot (WhiteTitle or BlackTitle == BOT) |
  min_plies (--min-plies, default 2: Black must have replied; counted among sampled games only).
  Resignations and short games are NOT dropped; they are flagged.

Resignation detection. Lichess dumps have no explicit 'resign' flag: 'Normal' covers checkmate,
stalemate, draws AND resignations. A game is flagged is_resignation iff
    Termination == Normal  AND  Result is decisive (1-0 / 0-1)  AND  last move is not mate ('#').
Dropping them (as the legacy data/games.csv did) inflates the draw rate and biases openings.

Output: one row per sampled game (columns in COLUMNS). SAN tokens are stripped of annotation
marks (?, !, ?!, !?, !!, ??) and NAGs ($n). --out ending in .parquet is written with pyarrow
(explicit schema, zstd, chunks of 200k rows); anything else is CSV.

Manifest: <out>.manifest.json records args, URL, git commit, start/end UTC, bytes read, games
seen/kept, rejections per rule, kept per (speed, band), complete flag and the output's sha256.
On a network/zstd error (or a truncated stream) it is written with complete=false and the exit
status is non-zero. --limit (testing only) also forces complete=false.

Usage
  python src/fetch_games.py --month 2025-06 --out data/games_2025-06.parquet \\
      --rate-override "classical=0.10,2200=0.10,2500=0.10"
  python src/fetch_games.py --input tiny.pgn.zst --out /tmp/t.csv --limit 100   # local file, same logic
"""
import argparse, bisect, codecs, csv, datetime as dt, hashlib, json, pathlib, re, subprocess, sys, time
import requests
import urllib3
import zstandard as zstd

URL = "https://database.lichess.org/standard/lichess_db_standard_rated_{month}.pgn.zst"
BANDS = [0, 1000, 1200, 1400, 1600, 1800, 2000, 2200, 2500]   # lower bounds, as in explorer.py
RESULTS = {"1-0", "0-1", "1/2-1/2"}
DECISIVE = {"1-0", "0-1"}
COLUMNS = ["game_id", "utc_date", "source_month", "speed", "time_control", "white", "black",
           "white_title", "black_title", "white_elo", "black_elo", "band", "result", "termination",
           "is_resignation", "time_forfeit", "is_tournament", "n_plies", "eco", "opening",
           "first_move", "black_reply", "first10", "sample_rate"]
REJECT_RULES = ["speed", "rating", "result", "termination", "bot", "min_plies"]
WANTED = {"Event", "Site", "White", "Black", "Result", "UTCDate", "WhiteElo", "BlackElo",
          "WhiteTitle", "BlackTitle", "TimeControl", "ECO", "Opening", "Termination"}
CHUNK_ROWS = 200_000
PROGRESS_EVERY = 1_000_000
STREAM_ERRORS = (requests.exceptions.RequestException, urllib3.exceptions.HTTPError,
                 zstd.ZstdError, ConnectionError, TimeoutError, EOFError)

SPEED = re.compile(r"Rated (\S+)")
COMMENT = re.compile(r"\{[^}]*\}")
MOVENUM = re.compile(r"\d+\.+")
MARKS = re.compile(r"[?!]+$")
MONTH = re.compile(r"(\d{4}-\d{2})")


class Counting:
    """Wraps a raw stream and counts compressed bytes consumed (for progress and completeness)."""
    def __init__(self, raw, total=None):
        self.raw, self.n, self.total = raw, 0, total
    def read(self, size=-1):
        b = self.raw.read(size)
        self.n += len(b)
        return b


def open_stream(src):
    if src.startswith("http"):
        r = requests.get(src, stream=True, timeout=60,
                         headers={"User-Agent": "chess-white-advantage-uni-project"})
        r.raise_for_status()
        total = r.headers.get("Content-Length")
        return Counting(r.raw, int(total) if total else None)
    return Counting(open(src, "rb"), pathlib.Path(src).stat().st_size)


def lines_of(stream, chunk=1 << 20):
    """Decompress `stream` and yield text lines. Unlike a plain stream_reader this raises EOFError
    if the zstd frame is cut off, so a truncated dump can never pass as a complete one."""
    dctx = zstd.ZstdDecompressor(max_window_size=2 ** 31)     # dumps use a long window
    dec = codecs.getincrementaldecoder("utf-8")(errors="replace")
    dobj, tail, pending = dctx.decompressobj(), "", False    # pending: inside an unfinished frame
    while True:
        blob = stream.read(chunk)
        if not blob:
            break
        while blob:
            pending = True
            text = tail + dec.decode(dobj.decompress(blob))
            *lines, tail = text.split("\n")
            yield from lines
            blob = b""
            if dobj.eof:                                      # frame finished; maybe another follows
                pending, blob, dobj = False, dobj.unused_data, dctx.decompressobj()
    if pending:
        raise EOFError("truncated zstd frame")
    if tail + dec.decode(b"", final=True):
        yield tail


def records(lines):
    """Yield one list of non-empty lines per game."""
    cur = []
    for line in lines:
        line = line.rstrip("\n")
        if line.startswith("[Event ") and cur:
            yield cur
            cur = []
        if line:
            cur.append(line)
    if cur:
        yield cur


def headers_of(rec):
    """Only the header tags in WANTED, parsed by string slicing (no regex: runs on every game)."""
    h = {}
    for ln in rec:
        if ln[0] == "[":
            sp = ln.find(' "')
            key = ln[1:sp]
            if key in WANTED:
                h[key] = ln[sp + 2:-2]
    return h


def sans_of(rec):
    """SAN tokens of one game with comments, move numbers, NAGs, the result token and annotation
    marks removed. Only called for sampled games."""
    text = COMMENT.sub(" ", " ".join(ln for ln in rec if ln[0] != "["))
    out = []
    for t in MOVENUM.sub(" ", text).split():
        if t[0] == "$" or t in RESULTS or t == "*":
            continue
        t = MARKS.sub("", t)
        if t:
            out.append(t)
    return out


def band_of(r):
    return BANDS[bisect.bisect_right(BANDS, r) - 1]


def hash_unit(game_id):
    """Deterministic pseudo-uniform value in [0, 1] derived only from the game id."""
    return int(hashlib.md5(game_id.encode()).hexdigest()[:8], 16) / 0xFFFFFFFF


def parse_overrides(spec):
    """'classical=0.10,2200=0.10' -> ({speed: rate}, {band: rate}). Raises ValueError."""
    by_speed, by_band = {}, {}
    for part in filter(None, (p.strip() for p in (spec or "").split(","))):
        key, sep, val = part.partition("=")
        key = key.strip().lower()
        try:
            rate = float(val)
        except ValueError:
            rate = None
        if not sep or rate is None or not 0 <= rate <= 1:
            raise ValueError(f"bad override {part!r}: expected key=rate with 0 <= rate <= 1")
        if key.isdigit():
            if int(key) not in BANDS:
                raise ValueError(f"override {key!r} is not a band lower bound {BANDS}")
            by_band[int(key)] = rate
        elif key.isalpha():
            by_speed[key] = rate
        else:
            raise ValueError(f"override key {key!r} is neither a speed name nor a band")
    return by_speed, by_band


def effective_rate(speed, band, base, overrides):
    """max(base rate, every override matching the game's speed or band)."""
    by_speed, by_band = overrides
    return max(base, by_speed.get(speed, 0.0), by_band.get(band, 0.0))


def is_sampled(game_id, rate):
    return hash_unit(game_id) < rate


class CsvSink:
    def __init__(self, path):
        self.f = open(path, "w", newline="", encoding="utf-8")
        self.w = csv.writer(self.f)
        self.w.writerow(COLUMNS)
    def write(self, row):
        self.w.writerow(row)
    def close(self):
        self.f.close()


class ParquetSink:
    """Buffers rows and writes them in CHUNK_ROWS-row groups with an explicit schema + zstd."""
    def __init__(self, path):
        import pyarrow as pa, pyarrow.parquet as pq          # lazy: CSV output needs no pyarrow
        self.pa = pa
        s, i, b = pa.string(), pa.int32(), pa.bool_()
        types = dict(white_elo=i, black_elo=i, band=i, n_plies=i, is_resignation=b,
                     time_forfeit=b, is_tournament=b, sample_rate=pa.float64())
        self.schema = pa.schema([(c, types.get(c, s)) for c in COLUMNS])
        self.w = pq.ParquetWriter(path, self.schema, compression="zstd")
        self.buf = [[] for _ in COLUMNS]
    def write(self, row):
        for col, v in zip(self.buf, row):
            col.append(v)
        if len(self.buf[0]) >= CHUNK_ROWS:
            self.flush()
    def flush(self):
        if self.buf[0]:
            arrays = [self.pa.array(c, type=f.type) for c, f in zip(self.buf, self.schema)]
            self.w.write_table(self.pa.Table.from_arrays(arrays, schema=self.schema))
            self.buf = [[] for _ in COLUMNS]
    def close(self):
        self.flush()
        self.w.close()


def make_sink(path):
    return ParquetSink(path) if path.endswith(".parquet") else CsvSink(path)


def sha256_of(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def git_commit():
    try:
        return subprocess.run(["git", "-C", str(pathlib.Path(__file__).resolve().parent), "rev-parse", "HEAD"],
                              capture_output=True, text=True, check=True).stdout.strip()
    except (OSError, subprocess.CalledProcessError):
        return None


def progress(seen, kept, stream, t0):
    el = time.time() - t0
    eta = f"{el * (stream.total / stream.n - 1) / 60:.0f} min" if stream.total and stream.n else "n/a"
    print(f"  seen {seen:,} | kept {kept:,} | {stream.n / 1e9:.2f} GB | {el / 60:.1f} min | ETA {eta}",
          file=sys.stderr, flush=True)


def build_parser():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    src = ap.add_mutually_exclusive_group(required=True)
    src.add_argument("--month", help="YYYY-MM of the standard rated dump")
    src.add_argument("--url")
    src.add_argument("--input", help="local .pgn.zst file (same code path; useful for testing)")
    ap.add_argument("--speeds", default="blitz,rapid,classical")
    ap.add_argument("--min-plies", type=int, default=2, help="drop games with fewer plies (default 2: Black replied)")
    ap.add_argument("--keep-terminations", default="Normal,Time forfeit")
    ap.add_argument("--band-by", choices=["avg", "min", "max"], default="avg",
                    help="which rating defines the band (verify against the explorer's semantics)")
    ap.add_argument("--sample-rate", type=float, default=0.01, help="base keep probability (default 0.01)")
    ap.add_argument("--rate-override", default="",
                    help='e.g. "classical=0.10,2200=0.10,2500=0.10": speed name or band lower bound; '
                         'a game uses the max of the base rate and all matching overrides')
    ap.add_argument("--limit", type=int, help="TESTING ONLY: stop after this many kept games; marks complete=false")
    ap.add_argument("--out", default="data/games.parquet", help=".parquet -> parquet (zstd), otherwise CSV")
    ap.add_argument("--pgn-out", help="optionally also write kept games as PGN")
    return ap


def main(argv=None):
    ap = build_parser()
    a = ap.parse_args(argv)
    if not 0 <= a.sample_rate <= 1:
        ap.error("--sample-rate must be in [0, 1]")
    if a.input and not pathlib.Path(a.input).is_file():
        ap.error(f"--input {a.input} not found")
    try:
        overrides = parse_overrides(a.rate_override)
    except ValueError as e:
        ap.error(str(e))

    speeds = {s.strip().lower() for s in a.speeds.split(",")}
    terms = {t.strip() for t in a.keep_terminations.split(",")}
    url = a.input or a.url or URL.format(month=a.month)
    month_hit = MONTH.search(a.month or url)
    source_month = month_hit.group(1) if month_hit else None
    out_path = pathlib.Path(a.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    rej = dict.fromkeys(REJECT_RULES, 0)
    cells = {}
    seen = kept = not_sampled = 0
    error = None
    start = dt.datetime.now(dt.timezone.utc)
    t0 = time.time()
    stream = None
    sink = pgn = None
    try:
        sink = make_sink(a.out)
        pgn = open(a.pgn_out, "w", encoding="utf-8") if a.pgn_out else None
        stream = open_stream(url)
        for rec in records(lines_of(stream)):
            seen += 1
            if seen % PROGRESS_EVERY == 0:
                progress(seen, kept, stream, t0)
            h = headers_of(rec)
            m = SPEED.match(h.get("Event", ""))
            speed = m.group(1).lower() if m else None
            if speed not in speeds:
                rej["speed"] += 1; continue
            try:
                we, be = int(h["WhiteElo"]), int(h["BlackElo"])
            except (KeyError, ValueError):
                rej["rating"] += 1; continue
            res, term = h.get("Result"), h.get("Termination")
            if res not in RESULTS:
                rej["result"] += 1; continue
            if term not in terms:
                rej["termination"] += 1; continue
            if h.get("WhiteTitle") == "BOT" or h.get("BlackTitle") == "BOT":
                rej["bot"] += 1; continue
            game_id = h.get("Site", "").rsplit("/", 1)[-1]
            band = band_of({"avg": (we + be) // 2, "min": min(we, be), "max": max(we, be)}[a.band_by])
            rate = effective_rate(speed, band, a.sample_rate, overrides)
            if not is_sampled(game_id, rate):                    # before any movetext work
                not_sampled += 1; continue
            sans = sans_of(rec)
            if len(sans) < a.min_plies:
                rej["min_plies"] += 1; continue
            date = h.get("UTCDate", "").replace(".", "-") or None
            event = h.get("Event", "")
            sink.write([game_id, date, source_month or (date[:7] if date else None), speed,
                        h.get("TimeControl"), h.get("White"), h.get("Black"),
                        h.get("WhiteTitle"), h.get("BlackTitle"), we, be, band, res, term,
                        term == "Normal" and res in DECISIVE and not (sans and sans[-1].endswith("#")),
                        term == "Time forfeit", "tournament" in event.lower(), len(sans),
                        h.get("ECO"), h.get("Opening"), sans[0] if sans else None,
                        sans[1] if len(sans) > 1 else None, " ".join(sans[:10]), rate])
            cells[(speed, band)] = cells.get((speed, band), 0) + 1
            kept += 1
            if pgn:
                pgn.write("\n".join(rec) + "\n\n")
            if a.limit and kept >= a.limit:
                break
        if not (a.limit and kept >= a.limit) and stream.total and stream.n != stream.total:
            error = f"truncated stream: read {stream.n} of {stream.total} compressed bytes"
    except STREAM_ERRORS as e:
        error = f"stream interrupted ({type(e).__name__}: {e}); partial output kept"
    finally:
        if sink:
            sink.close()
        if pgn:
            pgn.close()

    manifest = dict(
        args=vars(a), url=url, git_commit=git_commit(), source_month=source_month,
        rate_overrides=dict(speed=overrides[0], band=overrides[1]),
        start_utc=start.isoformat(timespec="seconds"),
        end_utc=dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
        compressed_bytes_read=stream.n if stream else 0, games_seen=seen, games_kept=kept,
        games_not_sampled=not_sampled, rejections=rej,
        kept_per_speed_band={f"{s}/{b}": n for (s, b), n in sorted(cells.items())},
        complete=error is None and not a.limit, error=error,
        output=a.out, output_sha256=sha256_of(a.out) if out_path.exists() else None)
    man_path = a.out + ".manifest.json"
    with open(man_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)

    print(f"\nread {manifest['compressed_bytes_read'] / 1e9:.3f} GB compressed, {seen:,} games, "
          f"kept {kept:,} -> {a.out}  (manifest: {man_path})")
    print("rejected:", {k: v for k, v in rej.items() if v}, "| not sampled:", f"{not_sampled:,}")
    print("per cell (speed/band):", manifest["kept_per_speed_band"])
    if error:
        print("ERROR:", error, file=sys.stderr)
        return 1
    if a.limit:
        print("--limit used: complete=false (testing only)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
