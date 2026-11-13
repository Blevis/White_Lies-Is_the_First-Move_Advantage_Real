import numpy as np
import pandas as pd
from scipy.stats import binom
from src.hypothesis_h1 import h1_test, run_h1, dyadic_covariance
from src.validation import clean_games

def synthetic_counts(w,d,b,band=1600,rate=.01):
    return pd.DataFrame(dict(result=['1-0']*int(w)+['1/2-1/2']*int(d)+['0-1']*int(b),
        speed='blitz',band=band,sample_rate=rate))

def test_h1_symmetric_and_reproducible():
    g=synthetic_counts(470,60,470)
    a=h1_test(g,seed=7)
    assert a==h1_test(g,seed=7)
    assert a['score']==.5 and a['lo']<.5<a['hi'] and a['p_mc']>.4
    assert abs(a['null_mean']-.5)<.001

def test_null_simulation_matches_exact_at_interior_p():
    a=h1_test(synthetic_counts(490,60,450),weighted=False,n_sim=10000)
    assert abs(a['p_mc']-a['p_exact_unweighted'])<.025

def test_nominal_false_positive_rate_and_power():
    rejects,power=0,0
    for seed in range(80):
        rng=np.random.default_rng(seed)
        w,d,b=rng.multinomial(2000,[.47,.06,.47])
        r=h1_test(synthetic_counts(w,d,b),n_sim=1000,seed=seed)
        rejects+=r['p_mc']<.05
        w,d,b=rng.multinomial(2000,[.55,.06,.39])
        a=h1_test(synthetic_counts(w,d,b),n_sim=1000,seed=seed)
        power+=a['p_mc']<.05
        assert abs(a['score']-.58)<.05
    assert rejects<=binom.ppf(.995,80,.05)
    assert power>=75

def test_sampling_imbalance_recovers_population_and_uses_observed_n():
    a=synthetic_counts(540,0,360,rate=.01)
    b=synthetic_counts(400,0,600,band=2200,rate=.1)
    sample=pd.concat([a,b],ignore_index=True)
    weighted,raw=h1_test(sample),h1_test(sample,weighted=False)
    assert abs(weighted['score']-.58)<1e-12
    assert abs(raw['score']-940/1900)<1e-12
    assert weighted['N']==1900 and weighted['effective_n']<1900
    assert weighted['hi']-weighted['lo']>.03

def test_dyadic_covariance_shared_players_both_colors():
    variance=dyadic_covariance([1.,2.,3.],['a','c','d'],['b','a','e'])[0,0]
    assert variance==18
    assert dyadic_covariance([1.,2.],['a','b'],['b','a'])[0,0]==9

def test_sparse_h1_inconclusive(games):
    g,_=clean_games(games)
    r=h1_test(g)
    assert r['status']=='insufficient' and np.isnan(r['p_mc'])
    assert r['lo']<r['score']<r['hi']

def test_subgroups_bh_and_single_primary():
    g=pd.concat([synthetic_counts(550,50,400),synthetic_counts(600,50,350,band=1800)])
    table=run_h1(g,n_sim=500)
    assert table.group_type.eq('primary').sum()==1
    assert (table.p_adjusted>=table.p_mc).all()

def test_weighted_bootstrap_interval_calibration():
    covered=0
    for seed in range(80):
        rng=np.random.default_rng(seed+100)
        w,d,b=rng.multinomial(3000,[.52,.06,.42])
        ci=h1_test(synthetic_counts(w,d,b),n_sim=1500,seed=seed)
        covered+=ci['lo']<=.55<=ci['hi']
    # Lower envelope for nominal 95% coverage, allowing Monte Carlo variability.
    assert covered>=binom.ppf(.005,80,.95)

def test_rating_adjustment_recovers_planted_equal_rating_score():
    from src.hypothesis_h1 import rating_adjustment
    rng=np.random.default_rng(41)
    n=20000
    difference=rng.normal(50,90,n)
    # A positive average rating imbalance inflates the raw score by ~.025.
    probability=.53+.0005*difference
    y=rng.binomial(1,probability.clip(.01,.99))
    g=pd.DataFrame(dict(speed='blitz',band=1600,weight=100.,elo_difference=difference,
        white_score=y,white=[f'w{i}' for i in range(n)],black=[f'b{i}' for i in range(n)]))
    adjusted,_=rating_adjustment(g)
    assert abs(adjusted['score']-.53)<.015
    assert abs(g.white_score.mean()-.53)>abs(adjusted['score']-.53)
