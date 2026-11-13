import numpy as np
import pytest
from src.stats import outcome_metrics, inverse_probability_weights, score_ci, benjamini_hochberg, multinomial_score_interval

def test_known_score_and_draw_rate():
    m=outcome_metrics(['1-0','1-0','1/2-1/2','0-1'])
    assert m['score']==.625 and m['draw_rate']==.25
    assert m['white_win_rate']==.5 and m['decisive_white_win_rate']==2/3
    assert score_ci([2],[1],[1]).score.iloc[0]==.625

def test_empty_and_all_draws():
    assert np.isnan(outcome_metrics([])['score'])
    assert np.isnan(outcome_metrics(['1/2-1/2'])['decisive_white_win_rate'])
    assert np.isnan(score_ci([0],[0],[0]).score.iloc[0])
    ci=multinomial_score_interval(0,1,0)
    assert ci['lo']<.5<ci['hi']

@pytest.mark.parametrize('rates',[[0],[-.1],[1.1],[np.nan],[np.inf]])
def test_invalid_rates(rates):
    with pytest.raises(ValueError): inverse_probability_weights(rates)

def test_weights_and_invalid_outcomes():
    np.testing.assert_equal(inverse_probability_weights([.01,.1]),[100,10])
    with pytest.raises(ValueError): outcome_metrics(['*'])
    with pytest.raises(ValueError): outcome_metrics(['1-0'],[0])
    with pytest.raises(ValueError): score_ci([-1],[0],[2])

def test_bh_analytical_values_and_missing():
    np.testing.assert_allclose(benjamini_hochberg([.01,.04,.03,.2,np.nan]),
        [.04,.053333333333,.053333333333,.2,np.nan],equal_nan=True)

def test_bootstrap_reproducibility_and_ci_scaling():
    a=multinomial_score_interval(520,60,420)
    assert a==multinomial_score_interval(520,60,420)
    b=multinomial_score_interval(5200,600,4200)
    assert a['lo']<.55<a['hi']
    assert .25<(b['hi']-b['lo'])/(a['hi']-a['lo'])<.4
    assert multinomial_score_interval(1,0,0)['lo']<1

def test_bootstrap_standard_error_matches_trinomial_variance():
    ci=multinomial_score_interval(5200,600,4200)
    mean=.55
    expected=np.sqrt((.52+.25*.06-mean**2)/10000)
    assert abs(ci['se']/expected-1)<.04
