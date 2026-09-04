"""Test Fase 6 — analyzer.report module."""

from pathlib import Path

from analyzer.report import generate_report

FIXTURES = Path(__file__).parent / "fixtures"


def test_generate_report_html(tmp_path):
    out = tmp_path / "report.html"
    generate_report(FIXTURES / "outliers.csv", out, k=1.5, with_charts=True)

    assert out.exists()
    text = out.read_text(encoding="utf-8")
    assert "<!DOCTYPE html>" in text
    assert "Insight Otomatis" in text
    assert "outlier" in text.lower()
    assert "data:image/png;base64," in text  # chart inline


def test_generate_report_md(tmp_path):
    out = tmp_path / "report.md"
    generate_report(FIXTURES / "outliers.csv", out, k=1.5, with_charts=True)

    assert out.exists()
    text = out.read_text(encoding="utf-8")
    assert text.startswith("# Data Analyzer Report")
    assert "## Insight Otomatis" in text
    assert "## Statistik Numerik" in text
    assert "_line.png" in text  # chart sebagai link file


def test_generate_report_no_charts(tmp_path):
    out = tmp_path / "report.html"
    generate_report(FIXTURES / "outliers.csv", out, with_charts=False)

    text = out.read_text(encoding="utf-8")
    assert "data:image/png" not in text


def test_generate_report_md_creates_chart_dir(tmp_path):
    out = tmp_path / "report.md"
    generate_report(FIXTURES / "outliers.csv", out, with_charts=True)

    chart_dir = tmp_path / "report_charts"
    assert chart_dir.exists()
    assert len(list(chart_dir.glob("*.png"))) > 0
