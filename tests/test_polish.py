"""Test Fase 7 — Polish & UX (filter, progress, dataset uji)."""

from pathlib import Path

import pytest

from analyzer.loader import InvalidDataError, load_dataframe

FIXTURES = Path(__file__).parent / "fixtures"


def test_filter_columns():
    df = load_dataframe(FIXTURES / "sample.csv", columns=["id", "value"])
    assert list(df.columns) == ["id", "value"]
    assert len(df) == 6


def test_filter_columns_invalid_raises():
    with pytest.raises(InvalidDataError, match="Kolom tidak ditemukan"):
        load_dataframe(FIXTURES / "sample.csv", columns=["nonexistent"])


def test_filter_row_range():
    df = load_dataframe(FIXTURES / "sample.csv", row_start=1, row_end=4)
    assert len(df) == 3  # iloc[1:4] -> baris 1, 2, 3
    assert df.iloc[0]["id"] == 2


def test_load_big_file_with_progress():
    df = load_dataframe(FIXTURES / "big.csv", show_progress=True)
    assert len(df) == 15000
    assert list(df.columns) == ["id", "timestamp", "voltage", "current", "status"]


def test_dataset_clean():
    df = load_dataframe(FIXTURES / "clean.csv")
    assert len(df) == 5
    assert df["sensor_temp"].mean() == pytest.approx(24.74)


def test_dataset_dirty():
    df = load_dataframe(FIXTURES / "dirty.csv")
    assert len(df) == 6
    assert df["val1"].isna().sum() == 2
