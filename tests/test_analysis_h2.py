import pandas as pd
import pytest
from src.h2 import spread_test
from src.hypothesis_h2 import group_replies, analyze_replies
from src.validation import clean_games

def test_reply_partition_and_sparse_coverage(games):
    g,_=clean_games(games)
    g.loc[0,'black_reply']='e5'
    grouped=group_replies(g)
    assert grouped[list('WDB')].to_numpy().sum()==len(g)
    summary,replies=analyze_replies(g,min_n=3,n_sim=500)
    assert summary.status.iloc[0]=='insufficient' and summary.coverage.iloc[0]==0
    assert not replies.tested.any()

def test_reply_vs_rest_disjoint_and_coverage(games):
    g,_=clean_games(games)
    g.loc[:2,'black_reply']='e5'
    g.loc[5,'black_reply']='a6'
    summary,replies=analyze_replies(g,min_n=2,n_sim=500,contrasts=False)
    assert summary.coverage.iloc[0]==5/6 and replies.tested.sum()==2
    assert replies[replies.reply=='e5'].iloc[0].rest_score==.5

def test_full_distribution_detects_draw_only_change():
    cell=pd.DataFrame(dict(reply=['a','b'],W=[4900,1000],D=[200,8000],B=[4900,1000]))
    r=spread_test(cell,n_sim=1000)
    assert r['p_sd']>.9 and r['p_distribution']<.01

@pytest.mark.parametrize('W,D,B',[([-1,1],[1,1],[1,1]),([0,1],[0,1],[0,1]),([1.5,1],[1,1],[1,1])])
def test_spread_rejects_invalid_counts(W,D,B):
    with pytest.raises(ValueError): spread_test(pd.DataFrame(dict(reply=['a','b'],W=W,D=D,B=B)))

def test_h2_null_false_positive_rate_is_calibrated():
    import numpy as np
    from scipy.stats import binom
    rejects=0
    for seed in range(80):
        rng=np.random.default_rng(seed+200)
        outcomes=np.array([rng.multinomial(n,[.47,.06,.47]) for n in [1000,2000,3000]])
        cell=pd.DataFrame(outcomes,columns=list('WDB')).assign(reply=['a','b','c'])
        rejects+=spread_test(cell,n_sim=1000,seed=seed)['p_sd']<.05
    assert rejects<=binom.ppf(.995,80,.05)
