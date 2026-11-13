from pathlib import Path
import json
import pandas as pd
from src.run_analysis import verify_artifacts

def test_executed_artifacts_numeric_and_consistent():
    root=Path(__file__).resolve().parents[1]
    assert verify_artifacts(root)
    data=json.loads((root/'results/dataset_summary.json').read_text())
    h1=pd.read_csv(root/'results/h1_results.csv').iloc[0]
    replies=pd.read_csv(root/'results/h2_reply_scores.csv')
    assert data['N']==h1.N==836070
    assert replies.N.sum()==pd.read_csv(root/'results/h2_results.csv').total_games.sum()
    assert replies.loc[replies.tested,'lo'].le(replies.loc[replies.tested,'score']).all()
    full=pd.read_csv(root/'results/h1_results.csv')
    for kind in ['speed','band','cell']:
        subset=full[full.group_type==kind]
        assert subset.N.sum()==h1.N
        reconstructed=(subset.score*subset.weight_total).sum()/subset.weight_total.sum()
        assert abs(reconstructed-h1.score)<1e-12
    assert (replies.N==replies.W+replies.D+replies.B).all()
    assert (replies.loc[replies.tested,'N']>=200).all()
    summary=json.loads((root/'results/h1_summary.json').read_text())
    assert abs(summary['primary']['score']-h1.score)<1e-12
    assert summary['n_sim']==10000 and summary['seed']==202503

def test_reports_and_executed_notebook_exist():
    root=Path(__file__).resolve().parents[1]
    for name in ['FINAL_RESEARCH_REPORT.md','FINAL_CONCLUSION.md','implementation_audit.md','COMPLETION_CHECKLIST.md']:
        assert (root/'reports'/name).stat().st_size>500
    nb=json.loads((root/'analysis.ipynb').read_text())
    code=[c for c in nb['cells'] if c['cell_type']=='code']
    assert code and all(c['execution_count'] is not None for c in code)
    assert not any(o.get('output_type')=='error' for c in code for o in c['outputs'])
