"""Test Fase 3 — analyzer.stats module."""

from pathlib import Path

import pandas as pd

from analyzer.loader import load_dataframe
from analyzer.stats import categorical_stats, numeric_stats, timestamp_stats

FIXTURES = Path(__file__).parent / "fixtures"


def test_numeric_stats():
    df = load_dataframe(FIXTURES / "sample.csv")
    stats = numeric_stats(df, ["id", "value"])

    id_stat = next(s for s in stats if s["column"] == "id")
    assert id_stat["count"] == 6
    assert id_stat["min"] == 1.0
    assert id_stat["max"] == 6.0
    assert id_stat["mean"] == 3.5
    assert id_stat["median"] == 3.5

    val_stat = next(s for s in stats if s["column"] == "value")
    assert val_stat["count"] == 5  # 1 NaN
    assert val_stat["min"] == 9.8
    assert val_stat["max"] == 12.1
    assert val_stat["median"] == 10.5


def test_numeric_stats_empty_series():
    df = pd.DataFrame({"empty_num": [None, None]})
    stats = numeric_stats(df, ["empty_num"])
    assert stats[0]["count"] == 0
    assert stats[0]["mean"] is None


def test_categorical_stats():
    df = load_dataframe(FIXTURES / "sample.csv")
    stats = categorical_stats(df, ["category"])

    cat_stat = stats[0]
    assert cat_stat["column"] == "category"
    assert cat_stat["unique"] == 3
    top = dict(cat_stat["top_values"])
    assert top["A"] == 2
    assert top["B"] == 2
    assert top["C"] == 2


def test_timestamp_stats():
    df = load_dataframe(FIXTURES / "sample.csv")
    stats = timestamp_stats(df, ["timestamp"])

    ts_stat = stats[0]
    assert ts_stat["column"] == "timestamp"
    assert ts_stat["min_time"] == "2026-01-01 00:00:00"
    assert ts_stat["max_time"] == "2026-01-01 05:00:00"
    assert "5:00:00" in ts_stat["duration"] or "05:00:00" in ts_stat["duration"]
