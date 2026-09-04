"""Test Fase 2 — loader + commands."""

from pathlib import Path

import pytest

from analyzer.loader import (
    InvalidDataError,
    _detect_delimiter,
    detect_column_types,
    load_dataframe,
    missing_summary,
)

FIXTURES = Path(__file__).parent / "fixtures"


def test_load_csv():
    df = load_dataframe(FIXTURES / "sample.csv")
    assert len(df) == 6
    assert len(df.columns) == 4


def test_load_tsv():
    df = load_dataframe(FIXTURES / "sample.tsv")
    assert len(df) == 4
    assert len(df.columns) == 4


def test_load_semicolon():
    df = load_dataframe(FIXTURES / "semicolon.csv", delimiter=";")
    assert len(df) == 3
    assert "city" in df.columns


def test_load_empty_raises():
    with pytest.raises(InvalidDataError):
        load_dataframe(FIXTURES / "empty.csv")


def test_load_header_only_raises():
    with pytest.raises(InvalidDataError, match="header"):
        load_dataframe(FIXTURES / "header_only.csv")


def test_detect_column_types():
    df = load_dataframe(FIXTURES / "sample.csv")
    types = detect_column_types(df)
    assert types["id"] == "numeric"
    assert types["timestamp"] == "datetime"
    assert types["value"] == "numeric"
    assert types["category"] == "category"


def test_missing_summary():
    df = load_dataframe(FIXTURES / "missing_values.csv")
    miss = missing_summary(df)
    assert miss["value"] == 40.0
    assert miss["notes"] == 60.0
    assert miss["id"] == 0.0


def test_missing_summary_clean():
    df = load_dataframe(FIXTURES / "sample.tsv")
    miss = missing_summary(df)
    assert all(v == 0.0 for v in miss.values())


# --- Delimiter sniffing (csv.Sniffer, sample multi-row) ---


def test_sniff_comma():
    assert _detect_delimiter(FIXTURES / "sample.csv") == ","


def test_sniff_tab():
    assert _detect_delimiter(FIXTURES / "sample.tsv") == "\t"


def test_sniff_semicolon():
    assert _detect_delimiter(FIXTURES / "semicolon.csv") == ";"


def test_sniff_pipe():
    assert _detect_delimiter(FIXTURES / "pipe.csv") == "|"


def test_sniff_single_column_fallback():
    assert _detect_delimiter(FIXTURES / "single_column.csv") == ","


def test_load_pipe():
    df = load_dataframe(FIXTURES / "pipe.csv")
    assert len(df) == 3
    assert list(df.columns) == ["id", "region", "reading"]


def test_load_single_column():
    df = load_dataframe(FIXTURES / "single_column.csv")
    assert list(df.columns) == ["value"]
    assert len(df) == 3


def test_sniff_ambiguous_comma_in_text():
    content = 'name;description\nJakarta;Kota besar, padat\nBandung;Sejuk, asri\n'
    p = FIXTURES / "_tmp_ambiguous.csv"
    p.write_text(content, encoding="utf-8")
    try:
        assert _detect_delimiter(p) == ";"
        df = load_dataframe(p)
        assert list(df.columns) == ["name", "description"]
    finally:
        p.unlink()


def test_sniff_large_sample():
    rows = "\n".join(f"{i},val{i},2026-01-01 00:{i % 60:02d}:00" for i in range(3000))
    content = "id,name,ts\n" + rows + "\n"
    p = FIXTURES / "_tmp_large.csv"
    p.write_text(content, encoding="utf-8")
    try:
        assert _detect_delimiter(p) == ","
        df = load_dataframe(p)
        assert len(df) == 3000
        assert list(df.columns) == ["id", "name", "ts"]
    finally:
        p.unlink()


def test_sniff_empty_file_raises():
    with pytest.raises(InvalidDataError):
        _detect_delimiter(FIXTURES / "empty.csv")


def test_explicit_delimiter_overrides_sniff():
    df = load_dataframe(FIXTURES / "sample.csv", delimiter=";")
    assert len(df.columns) == 1
