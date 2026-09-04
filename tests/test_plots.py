"""Test Fase 5 — analyzer.plots module."""

from pathlib import Path

import pandas as pd

from analyzer.loader import load_dataframe
from analyzer.plots import generate_charts, plot_hist, plot_line

FIXTURES = Path(__file__).parent / "fixtures"


def test_generate_charts_creates_png(tmp_path):
    df = load_dataframe(FIXTURES / "outliers.csv")
    paths = generate_charts(df, ["value"], tmp_path, k=1.5)

    assert len(paths) == 2
    for p in paths:
        assert p.exists() and p.stat().st_size > 0


def test_line_chart_with_outlier_highlight(tmp_path):
    df = pd.DataFrame({
        "val": [10, 11, 10, 12, 11, 100, 10, 11],
    })
    p = plot_line(df, "val", tmp_path / "line.png", outlier_idx=[5])
    assert p.exists() and p.stat().st_size > 0


def test_hist_chart(tmp_path):
    df = pd.DataFrame({"x": [1.0, 2.0, 1.5, 2.5, 3.0, 1.0]})
    p = plot_hist(df, "x", tmp_path / "hist.png", bins=4)
    assert p.exists() and p.stat().st_size > 0


def test_skip_empty_numeric(tmp_path):
    df = pd.DataFrame({"empty": [None, None], "ok": [1.0, 2.0]})
    paths = generate_charts(df, ["empty", "ok"], tmp_path)
    # empty col di-skip, cuma ok yg di-plot -> 2 file
    assert len(paths) == 2
