"""Read-only loaders for the existing White Lies research artifacts."""
from __future__ import annotations

import json
from pathlib import Path

import pandas as pd
import streamlit as st


@st.cache_data(show_spinner=False)
def load_csv(path: str | Path) -> pd.DataFrame:
    """Load a project CSV without changing the source file."""
    file_path = Path(path)
    if not file_path.exists():
        raise FileNotFoundError(f"Required research file was not found: {file_path}")
    return pd.read_csv(file_path)


@st.cache_data(show_spinner=False)
def load_json(path: str | Path) -> dict:
    """Load a project JSON artifact."""
    file_path = Path(path)
    if not file_path.exists():
        raise FileNotFoundError(f"Required research file was not found: {file_path}")
    with file_path.open(encoding="utf-8") as file:
        return json.load(file)


def _results_dir() -> Path:
    """Return the repository's existing results directory."""
    return Path(__file__).resolve().parents[1] / "results"


def load_h1_results() -> pd.DataFrame:
    """Load H1 subgroup estimates and normalize common data types."""
    data = load_csv(_results_dir() / "h1_results.csv")
    data["group_type"] = data["group_type"].astype(str)
    data["speed"] = data["speed"].astype(str)
    data["band"] = pd.to_numeric(data["band"], errors="coerce")
    data["reject"] = data["reject"].astype("boolean")
    return data


def load_h2_results() -> pd.DataFrame:
    """Load H2 cell-level omnibus test results."""
    data = load_csv(_results_dir() / "h2_results.csv")
    data["band"] = pd.to_numeric(data["band"], errors="coerce")
    return data


def load_h2_reply_scores() -> pd.DataFrame:
    """Load H2 reply-level estimates and normalize boolean columns."""
    data = load_csv(_results_dir() / "h2_reply_scores.csv")
    for column in ("eligible", "tested"):
        data[column] = data[column].astype("boolean").fillna(False).astype(bool)
    data["band"] = pd.to_numeric(data["band"], errors="coerce")
    return data
