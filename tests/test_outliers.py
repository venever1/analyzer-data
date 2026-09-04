"""Test Fase 4 — analyzer.outliers module."""

from pathlib import Path

import pandas as pd

from analyzer.loader import load_dataframe
from analyzer.outliers import detect_flatlines, detect_outliers, iqr_bounds

FIXTURES = Path(__file__).parent / "fixtures"


def test_iqr_bounds():
    s = pd.Series([10, 12, 11, 13, 12, 11, 12, 100])  # Q1=11, Q3=12.5, IQR=1.5
    bounds = iqr_bounds(s, k=1.5)
    assert bounds is not None
    lower, upper = bounds
    assert lower < 10
    assert upper < 100


def test_detect_outliers():
    df = load_dataframe(FIXTURES / "outliers.csv")
    res = detect_outliers(df, ["value"], k=1.5)

    v = res["value"]
    assert v["count"] == 2  # 100.0 and 150.0
    rows = dict(v["rows"])
    assert 20 in rows and rows[20] == 100.0
    assert 24 in rows and rows[24] == 150.0


def test_detect_flatlines():
    df = load_dataframe(FIXTURES / "flatline.csv")
    res = detect_flatlines(df, ["sensor2"], min_run=20)

    runs = res["sensor2"]
    assert len(runs) == 1
    run = runs[0]
    assert run["length"] == 30
    assert run["value"] == 7.5


def test_no_outlier_clean():
    df = pd.DataFrame({"v": [10, 11, 10, 11, 10, 11, 10, 11]})
    res = detect_outliers(df, ["v"], k=1.5)
    assert res["v"]["count"] == 0
