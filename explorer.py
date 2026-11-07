"""Lichess opening-explorer client + collection loop.

Auth: the explorer requires a (free, scope-less) personal token.
    https://lichess.org/account/oauth/token   ->   LICHESS_TOKEN in env or .env
"""
import hashlib, json, os, pathlib, time
import pandas as pd
import requests

BASE = "https://explorer.lichess.org/lichess"
CACHE = pathlib.Path(".cache")

# Rating buckets are given by lower bound: 1600 -> [1600, 1800), 2500 -> 2500+.
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

    def get(self, play="", speeds="blitz", ratings="1600", variant="standard"):
        params = dict(variant=variant, speeds=speeds, ratings=ratings, play=play,
                      moves=1, topGames=0, recentGames=0)
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
            out="data/explorer_raw.csv", verbose=True):
    """One row per (speed, band, position): raw W/D/B counts. Cached on disk."""
    rows, total = [], len(speeds) * len(ratings) * len(positions)
    for sp in speeds:
        for r in ratings:
            for name, play in positions.items():
                d = ex.get(play, sp, str(r))
                rows.append(dict(speed=sp, band=r, pos=name,
                                 W=d["white"], D=d["draws"], B=d["black"]))
        if verbose:
            print(f"{sp}: {len(rows)}/{total} cells (HTTP so far: {ex.n_http})")
    df = pd.DataFrame(rows)
    pathlib.Path(out).parent.mkdir(exist_ok=True)
    df.to_csv(out, index=False)
    return df
