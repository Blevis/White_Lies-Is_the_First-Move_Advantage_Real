import hashlib
import json
import numpy as np
import pytest
from src.validation import validate_manifest, clean_games, ValidationError

def collection(tmp_path,games):
    path=tmp_path/'games.parquet'
    games.to_parquet(path,index=False)
    m=dict(complete=True,error=None,source_month='2025-03',output='games.parquet',
        url='https://database.lichess.org/standard/lichess_db_standard_rated_2025-03.pgn.zst',
        games_seen=len(games),games_kept=len(games),games_not_sampled=0,
        kept_per_speed_band={'blitz/1600':len(games)},
        rejections=dict(speed=0,rating=0,result=0,termination=0,bot=0,min_plies=0),
        rate_overrides=dict(speed={},band={}),
        args=dict(out='games.parquet',month='2025-03',limit=None,min_plies=2,band_by='avg',
            sample_rate=1.,rate_override='',speeds='blitz,rapid,classical',keep_terminations='Normal,Time forfeit'),
        output_sha256=hashlib.sha256(path.read_bytes()).hexdigest())
    sidecar=path.with_suffix('.parquet.manifest.json')
    sidecar.write_text(json.dumps(m))
    return path,sidecar,m

def test_manifest_valid_and_incomplete_fails(tmp_path,games):
    path,sidecar,m=collection(tmp_path,games)
    _,summary=validate_manifest(path,tmp_path)
    assert summary['validated']
    m['complete']=False
    sidecar.write_text(json.dumps(m))
    with pytest.raises(ValidationError,match='complete'): validate_manifest(path,tmp_path)

@pytest.mark.parametrize('field,value',[('output_sha256','bad'),('games_kept',999),('output','wrong.parquet'),('source_month','2025-04')])
def test_manifest_rejects_wrong_provenance(tmp_path,games,field,value):
    path,sidecar,m=collection(tmp_path,games)
    m[field]=value
    sidecar.write_text(json.dumps(m))
    with pytest.raises(ValidationError): validate_manifest(path,tmp_path)

def test_clean_records_duplicate_and_rating_difference(games):
    games.loc[1,'game_id']=games.loc[0,'game_id']
    games.loc[2,'white_elo']=1660
    out,ledger=clean_games(games)
    assert len(out)==5 and out.loc[2,'elo_difference']==10
    assert ledger['excluded_total']==1
    assert next(x for x in ledger['rules'] if x['rule']=='duplicate_id_after_first')['excluded']==1

@pytest.mark.parametrize('column,value,rule',[
    ('white_elo',np.nan,'invalid_ratings'),('result','*','invalid_result'),
    ('utc_date','2025-02-30','invalid_date_or_month'),('speed','bullet','invalid_speed'),
    ('band',1800,'inconsistent_band'),('sample_rate',0,'invalid_sample_rate'),('white_title','BOT','bot'),
    ('termination','Abandoned','invalid_termination'),('n_plies',1,'too_few_plies'),
    ('black_reply',None,'missing_black_reply'),('first_move',None,'missing_first_move')])
def test_every_exclusion_is_counted(games,column,value,rule):
    if column=='white_elo': games[column]=games[column].astype(float)
    games.loc[0,column]=value
    out,ledger=clean_games(games)
    assert len(out)==5 and ledger['excluded_total']==1
    assert next(x for x in ledger['rules'] if x['rule']==rule)['flagged']==1

def test_short_resignations_preserved(games):
    games.loc[0,'n_plies']=2
    out,ledger=clean_games(games)
    assert len(out)==6 and ledger['excluded_total']==0

def test_manifest_fails_when_declared_sampling_rate_disagrees(tmp_path,games):
    path,sidecar,m=collection(tmp_path,games)
    m['args']['sample_rate']=.1
    sidecar.write_text(json.dumps(m))
    with pytest.raises(ValidationError,match='sample_rates'): validate_manifest(path,tmp_path)

def test_signed_rating_boundaries_match_near_equal_definition(tmp_path,games):
    from src.run_analysis import eda_tables
    from src.fetch_games import band_of
    games.loc[:,'white_elo']=[1625,1624,1550,1549,1675,1676]
    games['band']=((games.white_elo+games.black_elo)//2).map(band_of)
    g,_=clean_games(games)
    eda=eda_tables(g,tmp_path)
    signed=eda[eda.dimension=='signed_rating_gap'].set_index('group')
    assert signed.loc['Within 25','N']==2
    assert signed.loc['White lower 26-100','N']==2
    assert signed.loc['White lower >100','N']==1
    assert signed.loc['White higher 26-100','N']==1
