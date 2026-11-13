"""Offline artifact smoke check: run after python -m src.run_analysis."""
import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from src.run_analysis import verify_artifacts
if __name__=='__main__':
    assert verify_artifacts(ROOT)
    print('Frozen-data pipeline artifacts verified')
