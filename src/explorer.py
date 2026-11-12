"""Lichess opening-explorer client + collection loop.

Auth: the explorer requires a (free, scope-less) personal token.
    https://lichess.org/account/oauth/token   ->   LICHESS_TOKEN in env or .env
"""
import hashlib, json, os, pathlib, re, time
import pandas as pd
import requests

BASE = "https://explorer.lichess.org/lichess"
CACHE = pathlib.Path(".cache")

# Study window (README: Jan-Dec 2025). The explorer default is ALL TIME, so every request must
# carry since/until explicitly; both are part of the cache key and of the output CSV.
SINCE, UNTIL = "2025-01", "2025-12"
_MONTH = re.compile(r"^\d{4}-(0[1-9]|1[0-2])$")

# Rating buckets are given by lower bound: 1600 -> [1600, 1800), 2500 -> 2500+.
# (Lichess spec: group 0 = 0-999, ..., 2500 = 2500 and above. Per-player vs average game rating
# is not specified by the API; fetch_games.py assumes the average -- verify with ground truth.)
RATINGS = [0, 1000, 1200, 1400, 1600, 1800, 2000, 2200, 2500]
SPEEDS = ["bullet", "blitz", "rapid", "classical"]

# Root + the five positions needed to derive all six families by subtraction (UCI).
POSITIONS = {
    "root": "",
    "e4": "e2e4",
    "e4e5": "e2e4,e7e5",
    "d4": "d2d4",
    "d4d5": "d2d4,d7d5",
}


class Explorer:
    def __init__(self, token=None, min_interval=1.0, cache_dir=CACHE):
        token = token or os.environ.get("LICHESS_TOKEN")
        if not token:
            raise RuntimeError("LICHESS_TOKEN not set (see module docstring).")
        self.cache = pathlib.Path(cache_dir)
        self.cache.mkdir(exist_ok=True)
        self.s = requests.Session()
        self.s.headers.update({
            "Authorization": f"Bearer {token}",
            "Accept": "application/json",
            "User-Agent": "chess-white-advantage-uni-project",
        })
        self.min_interval, self._last = min_interval, 0.0
        self.n_http = 0  # real requests made (cache hits excluded)

    def get(self, play="", speeds="blitz", ratings="1600", variant="standard",
            since=SINCE, until=UNTIL, moves=1):
        """One explorer query. `moves` = number of most common continuations returned (the
        position totals white/draws/black are always for ALL games, whatever `moves` is)."""
        for m in (since, until):
            if not _MONTH.match(str(m)):
                raise ValueError(f"since/until must be 'YYYY-MM', got {m!r}")
        if since > until:
            raise ValueError(f"since {since} is after until {until}")
        params = dict(variant=variant, speeds=speeds, ratings=ratings, play=play,
                      since=since, until=until, moves=moves, topGames=0, recentGames=0)
        key = hashlib.sha1(json.dumps(params, sort_keys=True).encode()).hexdigest()
        f = self.cache / f"{key}.json"
        if f.exists():
            return json.loads(f.read_text())
        for attempt in range(6):
            time.sleep(max(0.0, self.min_interval - (time.time() - self._last)))  # serial requests
            r = self.s.get(BASE, params=params, timeout=30)
            self._last = time.time()
            self.n_http += 1
            if r.status_code == 429:          # Lichess asks for a full-minute backoff
                time.sleep(60)
                continue
            r.raise_for_status()              # 401 => bad/missing token
            data = r.json()
            f.write_text(json.dumps(data))
            return data
        raise RuntimeError(f"rate-limited repeatedly: {params}")


def collect(ex, speeds=SPEEDS, ratings=RATINGS, positions=POSITIONS,
            out="data/explorer_raw.csv", verbose=True, since=SINCE, until=UNTIL):
    """One row per (speed, band, position): raw W/D/B counts for [since, until]. Cached on disk."""
    rows, total = [], len(speeds) * len(ratings) * len(positions)
    for sp in speeds:
        for r in ratings:
            for name, play in positions.items():
                d = ex.get(play, sp, str(r), since=since, until=until)
                rows.append(dict(speed=sp, band=r, pos=name, since=since, until=until,
                                 W=d["white"], D=d["draws"], B=d["black"]))
        if verbose:
            print(f"{sp} [{since}..{until}]: {len(rows)}/{total} cells (HTTP so far: {ex.n_http})")
    df = pd.DataFrame(rows)
    pathlib.Path(out).parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(out, index=False)
    return df