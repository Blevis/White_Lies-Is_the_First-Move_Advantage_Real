"""Offline tests for explorer date-window patch + H2 reply-level spread test. No network.
Run: python tests/test_h2.py   (or pytest tests/)"""
import json, os, sys, tempfile, pathlib
import numpy as np, pandas as pd
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
os.environ.setdefault("LICHESS_TOKEN", "test")
import explorer, h2


class FakeResp:
    status_code = 200
    def __init__(self, payload): self.p = payload
    def raise_for_status(self): pass
    def json(self): return self.p


def fake_explorer(tmp, payload_fn):
    ex = explorer.Explorer(token="t", min_interval=0, cache_dir=tmp)
    calls = []
    def get(url, params, timeout):
        calls.append(params); return FakeResp(payload_fn(params))
    ex.s.get = get
    return ex, calls


def payload(params):
    top = params["moves"]
    mv = [dict(uci="c7c5", san="c5", white=480_000, draws=40_000, black=480_000),
          dict(uci="e7e5", san="e5", white=520_000, draws=40_000, black=440_000),
          dict(uci="e7e6", san="e6", white=130_000, draws=10_000, black=110_000)][:top]
    return dict(white=1_200_000, draws=100_000, black=1_100_000, moves=mv)


def test_since_until_sent_and_in_cache_key():
    with tempfile.TemporaryDirectory() as tmp:
        ex, calls = fake_explorer(tmp, payload)
        ex.get("e2e4", "blitz", "1600")
        assert calls[0]["since"] == "2025-01" and calls[0]["until"] == "2025-12"
        ex.get("e2e4", "blitz", "1600")                       # cache hit
        assert len(calls) == 1
        ex.get("e2e4", "blitz", "1600", since="2024-01", until="2024-12")
        assert len(calls) == 2                                # different window => new request


def test_window_validation():
    with tempfile.TemporaryDirectory() as tmp:
        ex, _ = fake_explorer(tmp, payload)
        for bad in [dict(since="2025-1"), dict(until="2025-13"), dict(since="2026-01", until="2025-12")]:
            try: ex.get("", "blitz", "1600", **bad)
            except ValueError: continue
            raise AssertionError(f"accepted {bad}")


def test_collect_writes_window_columns():
    with tempfile.TemporaryDirectory() as tmp:
        ex, _ = fake_explorer(tmp + "/c", lambda p: dict(white=3, draws=1, black=2))
        df = explorer.collect(ex, speeds=["blitz"], ratings=[1600], out=tmp + "/a/b/raw.csv", verbose=False)
        assert set(df.since) == {"2025-01"} and set(df.until) == {"2025-12"} and len(df) == 5


def test_collect_replies_partition():
    with tempfile.TemporaryDirectory() as tmp:
        ex, calls = fake_explorer(tmp + "/c", payload)
        df = h2.collect_replies(ex, speeds=["blitz"], ratings=[1200, 1400], out=None, verbose=False)
        assert len(calls) == 2 * 1 * 2 and all(c["moves"] == h2.TOP_REPLIES for c in calls)
        cell = df[(df["first"] == "e4") & (df.band == 1200)]
        tot = cell[["W", "D", "B"]].sum()
        assert tot.tolist() == [1_200_000, 100_000, 1_100_000]      # replies + _other == position
        assert (cell[["W", "D", "B"]] >= 0).all().all()


def _cell(scores, N, draw=0.05):
    rows = []
    for i, (s, n) in enumerate(zip(scores, N)):
        D = int(n * draw); W = int(round(n * s - D / 2))
        rows.append(dict(first="e4", speed="blitz", band=1600, reply=f"r{i}", W=W, D=D, B=n - W - D))
    return pd.DataFrame(rows)


def test_null_is_not_rejected_and_planted_effect_is():
    # no true differences, small N so sampling noise is visible: p-values ~uniform
    ps = []
    for seed in range(40):
        rng = np.random.default_rng(seed)
        N = [4000, 3000, 2000, 1000]
        rows = []
        for i, n in enumerate(N):
            W, D, B = rng.multinomial(n, [.47, .06, .47])
            rows.append(dict(first="e4", speed="blitz", band=1600, reply=f"r{i}", W=W, D=D, B=B))
        ps.append(h2.spread_test(pd.DataFrame(rows), n_sim=500, seed=seed)["p_sd"])
    assert 0.3 < np.mean(ps) < 0.7 and np.mean(np.array(ps) < .05) < .15, ps
    # planted 2-point effect on one reply at explorer-scale N
    r = h2.spread_test(_cell([.52, .52, .52, .50], [900_000, 700_000, 500_000, 300_000]), n_sim=500)
    assert r["p_sd"] < 0.01 and r["worst"] == "r3"
    assert 0.003 < r["sd_excess"] < 0.01 and abs(r["range_obs"] - 0.02) < 1e-3
    # no effect at explorer-scale N: excess spread ~ 0
    r0 = h2.spread_test(_cell([.52, .52, .52, .52], [900_000, 700_000, 500_000, 300_000]), n_sim=500)
    assert r0["sd_excess"] < 5e-4


def test_run_h2_filters_and_draw_rate_preserved():
    c = _cell([.52, .53, .51], [200_000, 100_000, 5_000])         # third below min_n
    other = pd.DataFrame([dict(first="e4", speed="blitz", band=1600, reply="_other", W=1, D=1, B=1)])
    s, t = h2.run_h2(pd.concat([c, other]), n_sim=200)
    assert len(s) == 1 and s.k.iloc[0] == 2 and set(t.reply) == {"r0", "r1"}
    cv = h2.coverage(pd.concat([c, other]))
    assert 0.97 < cv.coverage.iloc[0] < 1.0


def _games():
    return pd.DataFrame(dict(
        speed=["blitz"] * 6, band=[1600] * 6,
        result=["1-0", "0-1", "1/2-1/2", "1-0", "1-0", "1-0"],
        first_move=["e4", "e4", "e4", "d4", "Nf3", "e4"],
        black_reply=["c5", "c5", "e5", "d5", "d5", "c5"],
        white_title=[None, None, None, None, None, "BOT"], black_title=[None] * 6))


def test_replies_from_games():
    with tempfile.TemporaryDirectory() as tmp:
        for name, write in (("g.csv", lambda g, p: g.to_csv(p, index=False)),
                            ("g.parquet", lambda g, p: g.to_parquet(p))):
            write(_games(), f"{tmp}/{name}")
            r = h2.replies_from_games(f"{tmp}/{name}")
            c5 = r[(r["first"] == "e4") & (r.reply == "c5")].iloc[0]
            # 3 e4-c5 games, one of them a BOT game -> excluded
            assert (c5.W, c5.D, c5.B) == (1, 0, 1) and "Nf3" not in set(r["first"])


if __name__ == "__main__":
    for name, fn in list(globals().items()):
        if name.startswith("test_"):
            fn(); print("ok", name)