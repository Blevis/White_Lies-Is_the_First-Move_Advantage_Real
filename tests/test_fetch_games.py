"""Offline tests for src/fetch_games.py on a tiny synthetic .pgn.zst. No network.
Run: python tests/test_fetch_games.py   (or pytest tests/)"""
import hashlib, json, os, sys, tempfile
import pandas as pd
import zstandard as zstd
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
import fetch_games as fg


def pgn(gid, we=1600, be=1600, speed="Blitz", result="1-0", term="Normal", moves="1. e4 c5 2. Nf3 d6",
        wt=None, bt=None, event=None, date="2025.06.15"):
    ev = event or f"Rated {speed} game"
    tags = [("Event", ev), ("Site", f"https://lichess.org/{gid}"), ("White", "alice"), ("Black", "bob"),
            ("Result", result), ("UTCDate", date), ("UTCTime", "12:00:00"), ("WhiteElo", we), ("BlackElo", be),
            ("WhiteRatingDiff", "+5"), ("BlackRatingDiff", "-5"), ("ECO", "B50"), ("Opening", "Sicilian Defense"),
            ("TimeControl", "180+0"), ("Termination", term)]
    if wt: tags.insert(7, ("WhiteTitle", wt))
    if bt: tags.insert(7, ("BlackTitle", bt))
    head = "\n".join(f'[{k} "{v}"]' for k, v in tags)
    return f"{head}\n\n{moves} {result}\n\n"


def write_zst(tmp, games):
    path = os.path.join(tmp, "synthetic.pgn.zst")
    with open(path, "wb") as f:
        f.write(zstd.ZstdCompressor().compress("".join(games).encode()))
    return path


def run(src, out, *extra):
    code = fg.main(["--input", src, "--out", out, *extra])
    man = json.load(open(out + ".manifest.json"))
    return code, man


def corpus(n=400):
    """n blitz games with distinct ids spread over the bands, plus a few classical ones."""
    g = [pgn(f"g{i:07d}", we=1000 + (i % 15) * 100, be=1000 + (i % 15) * 100) for i in range(n)]
    g += [pgn(f"c{i:07d}", speed="Classical") for i in range(40)]
    return g


def test_hash_sampling_is_deterministic_and_matches_spec():
    gid = "abcd1234"
    u = int(hashlib.md5(gid.encode()).hexdigest()[:8], 16) / 0xFFFFFFFF
    assert fg.hash_unit(gid) == u == fg.hash_unit(gid)
    assert fg.is_sampled(gid, u + 1e-9) and not fg.is_sampled(gid, u)
    with tempfile.TemporaryDirectory() as tmp:
        src = write_zst(tmp, corpus())
        _, m1 = run(src, f"{tmp}/a.csv", "--sample-rate", "0.3", "--speeds", "blitz")
        _, m2 = run(src, f"{tmp}/b.csv", "--sample-rate", "0.3", "--speeds", "blitz")
        a, b = pd.read_csv(f"{tmp}/a.csv"), pd.read_csv(f"{tmp}/b.csv")
        assert a.equals(b) and m1["output_sha256"] == m2["output_sha256"]
        expect = {f"g{i:07d}" for i in range(400) if fg.hash_unit(f"g{i:07d}") < 0.3}
        assert set(a.game_id) == expect and 0 < len(expect) < 400
        assert (a.sample_rate == 0.3).all()


def test_rate_overrides_apply():
    assert fg.parse_overrides("classical=0.10, 2200=0.2,2500=1") == ({"classical": 0.1}, {2200: 0.2, 2500: 1.0})
    for bad in ("classical", "classical=2", "1234=0.5", "x1=0.5"):
        try:
            fg.parse_overrides(bad); assert False, bad
        except ValueError:
            pass
    ov = fg.parse_overrides("classical=0.10,2200=0.20")
    assert fg.effective_rate("blitz", 1600, 0.01, ov) == 0.01
    assert fg.effective_rate("classical", 1600, 0.01, ov) == 0.10
    assert fg.effective_rate("classical", 2200, 0.01, ov) == 0.20          # max of all matches
    assert fg.effective_rate("blitz", 2200, 0.5, ov) == 0.5                # base can win
    with tempfile.TemporaryDirectory() as tmp:
        src = write_zst(tmp, corpus())
        run(src, f"{tmp}/o.csv", "--sample-rate", "0", "--rate-override", "classical=1")
        o = pd.read_csv(f"{tmp}/o.csv")
        assert len(o) == 40 and set(o.speed) == {"classical"} and (o.sample_rate == 1).all()
        run(src, f"{tmp}/p.csv", "--sample-rate", "0", "--rate-override", "1400=1")
        p = pd.read_csv(f"{tmp}/p.csv")
        assert len(p) > 0 and set(p.band) == {1400} and (p.sample_rate == 1).all()


def test_resignations_kept_and_flagged_and_short_games_flagged_not_dropped():
    games = [
        pgn("resign01", result="1-0", moves="1. e4 e5 2. Nf3"),                              # resignation
        pgn("mate0001", result="0-1", moves="1. f3 e5 2. g4 Qh4#"),                          # mate
        pgn("draw0001", result="1/2-1/2", moves="1. e4 e5 2. Nf3 Nc6"),                      # draw
        pgn("flag0001", result="1-0", term="Time forfeit", moves="1. e4 e5 2. Nf3 Nc6"),     # flag
        pgn("short001", result="1-0", moves="1. e4"),                                        # 1 ply
    ]
    with tempfile.TemporaryDirectory() as tmp:
        code, man = run(write_zst(tmp, games), f"{tmp}/r.csv", "--sample-rate", "1")
        d = pd.read_csv(f"{tmp}/r.csv").set_index("game_id")
        assert code == 0 and set(d.index) == {"resign01", "mate0001", "draw0001", "flag0001"}
        assert list(d.is_resignation) == [True, False, False, False]
        assert list(d.time_forfeit) == [False, False, False, True]
        assert man["rejections"]["min_plies"] == 1                  # short games need --min-plies 1
        run(write_zst(tmp, games), f"{tmp}/r1.csv", "--sample-rate", "1", "--min-plies", "1")
        assert "short001" in set(pd.read_csv(f"{tmp}/r1.csv").game_id)


def test_bot_games_dropped_and_other_filters_counted():
    games = [pgn("bot00001", wt="BOT"), pgn("bot00002", bt="BOT"), pgn("human001", wt="GM", bt="NM"),
             pgn("bullet01", speed="Bullet"), pgn("abandon1", term="Abandoned"),
             pgn("unrated1", we="?"), pgn("noresult", result="*"),
             pgn("tourney1", event="Rated Blitz tournament https://lichess.org/tournament/xyz")]
    with tempfile.TemporaryDirectory() as tmp:
        _, man = run(write_zst(tmp, games), f"{tmp}/b.csv", "--sample-rate", "1")
        d = pd.read_csv(f"{tmp}/b.csv", keep_default_na=False).set_index("game_id")
        assert set(d.index) == {"human001", "tourney1"}
        assert d.loc["human001", "white_title"] == "GM" and d.loc["human001", "black_title"] == "NM"
        assert list(d.is_tournament) == [False, True]
        assert man["rejections"] == dict(speed=1, rating=1, result=1, termination=1, bot=2, min_plies=0)
        assert man["games_seen"] == 8 and man["games_kept"] == 2


def test_annotations_stripped():
    mv = ("1. e4 { [%clk 0:03:00] } 1... c5?! { [%clk 0:03:00] } 2. f4!? $6 d6 3. Nf3?? Nf6!! 4. Bb5+ Bd7! "
          "5. O-O Nc6 6. d3 e6 7. c3 Be7 8. Qe2 O-O 9. Nbd2 a6 10. Bxd7 Qxd7")
    with tempfile.TemporaryDirectory() as tmp:
        run(write_zst(tmp, [pgn("annot001", moves=mv)]), f"{tmp}/n.csv", "--sample-rate", "1")
        d = pd.read_csv(f"{tmp}/n.csv").iloc[0]
        assert d.first10 == "e4 c5 f4 d6 Nf3 Nf6 Bb5+ Bd7 O-O Nc6"
        assert (d.first_move, d.black_reply, d.n_plies) == ("e4", "c5", 20)
        assert not any(ch in d.first10 for ch in "?!$")


def test_columns_csv_and_parquet_agree():
    games = [pgn("col00001", wt="IM")]
    with tempfile.TemporaryDirectory() as tmp:
        src = write_zst(tmp, games)
        run(src, f"{tmp}/c.csv", "--sample-rate", "1")
        run(src, f"{tmp}/c.parquet", "--sample-rate", "1")
        c, p = pd.read_csv(f"{tmp}/c.csv"), pd.read_parquet(f"{tmp}/c.parquet")
        assert list(c.columns) == list(p.columns) == fg.COLUMNS
        assert fg.COLUMNS == ["game_id", "utc_date", "source_month", "speed", "time_control", "white", "black",
                              "white_title", "black_title", "white_elo", "black_elo", "band", "result",
                              "termination", "is_resignation", "time_forfeit", "is_tournament", "n_plies",
                              "eco", "opening", "first_move", "black_reply", "first10", "sample_rate"]
        r = p.iloc[0]
        assert r.utc_date == "2025-06-15" and r.source_month == "2025-06" and r.band == 1600
        assert r.is_resignation and not r.time_forfeit and pd.isna(r.black_title)
        import pyarrow.parquet as pq
        meta = pq.ParquetFile(f"{tmp}/c.parquet").metadata
        assert meta.row_group(0).column(0).compression == "ZSTD"


def test_parquet_written_in_chunks():
    old = fg.CHUNK_ROWS
    fg.CHUNK_ROWS = 50
    try:
        with tempfile.TemporaryDirectory() as tmp:
            run(write_zst(tmp, corpus()), f"{tmp}/k.parquet", "--sample-rate", "1")
            import pyarrow.parquet as pq
            pf = pq.ParquetFile(f"{tmp}/k.parquet")
            assert pf.metadata.num_rows == 440 and pf.metadata.num_row_groups == 9   # 8 x 50 + 40
    finally:
        fg.CHUNK_ROWS = old


def test_manifest_fields_and_limit_marks_incomplete():
    with tempfile.TemporaryDirectory() as tmp:
        src = write_zst(tmp, corpus())
        code, m = run(src, f"{tmp}/m.csv", "--sample-rate", "1")
        for k in ("args", "url", "git_commit", "start_utc", "end_utc", "compressed_bytes_read", "games_seen",
                  "games_kept", "rejections", "kept_per_speed_band", "complete", "output_sha256"):
            assert k in m, k
        assert code == 0 and m["complete"] is True and m["games_seen"] == m["games_kept"] == 440
        assert m["compressed_bytes_read"] == os.path.getsize(src) and m["url"] == src
        assert m["args"]["sample_rate"] == 1.0 and sum(m["kept_per_speed_band"].values()) == 440
        assert m["output_sha256"] == hashlib.sha256(open(f"{tmp}/m.csv", "rb").read()).hexdigest()
        assert "blitz/1600" in m["kept_per_speed_band"] and m["start_utc"] <= m["end_utc"]
        code, m = run(src, f"{tmp}/l.csv", "--sample-rate", "1", "--limit", "10")
        assert code == 0 and m["complete"] is False and m["games_kept"] == 10
        assert len(pd.read_csv(f"{tmp}/l.csv")) == 10


def test_truncated_stream_writes_incomplete_manifest_and_exits_nonzero():
    with tempfile.TemporaryDirectory() as tmp:
        src = write_zst(tmp, corpus())
        blob = open(src, "rb").read()
        open(src, "wb").write(blob[: len(blob) // 2])
        code, m = run(src, f"{tmp}/t.csv", "--sample-rate", "1")
        # truncated frame: either zstd raises or the size check catches it; both -> non-zero
        assert code != 0 and m["complete"] is False and m["error"]
        assert m["output_sha256"]


if __name__ == "__main__":
    for name, fn in list(globals().items()):
        if name.startswith("test_"):
            fn(); print("ok", name)
