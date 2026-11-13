import pandas as pd
import pytest
from src.fetch_games import COLUMNS

@pytest.fixture
def games():
    row = dict.fromkeys(COLUMNS)
    row.update(game_id='test0000', utc_date='2025-03-15', source_month='2025-03', speed='blitz',
        time_control='180+0', white='alice', black='bob', white_elo=1650, black_elo=1650,
        band=1600, result='1-0', termination='Normal', is_resignation=True, time_forfeit=False,
        is_tournament=False, n_plies=20, eco='B20', opening='Sicilian Defense', first_move='e4',
        black_reply='c5', first10='e4 c5 Nf3 d6', sample_rate=1.)
    return pd.DataFrame([dict(row, game_id=f'test{i:04}', white=f'w{i}', black=f'b{i}', result=r)
        for i,r in enumerate(['1-0','1/2-1/2','0-1','1-0','0-1','1-0'])])
