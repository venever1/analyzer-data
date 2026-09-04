"""Laporan otomatis: gabung statistik + insight + chart (HTML & Markdown)."""

import base64
import html
from collections.abc import Callable
from datetime import datetime
from pathlib import Path
from typing import Any

import pandas as pd

from analyzer.loader import detect_column_types, load_dataframe, missing_summary
from analyzer.outliers import detect_flatlines, detect_outliers
from analyzer.stats import categorical_stats, numeric_stats, timestamp_stats

InsightFn = Callable[[pd.DataFrame, dict[str, str]], list[str]]


def _insights(df: pd.DataFrame, col_types: dict[str, str], k: float) -> list[str]:
    """Generate insight otomatis dari dataset."""
    out: list[str] = []
    num_cols = [c for c, t in col_types.items() if t == "numeric"]
    missing = missing_summary(df)

    worst = max(missing, key=missing.get, default=None)
    if worst and missing[worst] >= 10:
        out.append(f"Kolom <code>{html.escape(worst)}</code> punya missing value tinggi ({missing[worst]:.2f}%).")

    outlier_result = detect_outliers(df, num_cols, k=k)
    for col, r in outlier_result.items():
        if r["count"] > 0:
            out.append(
                f"Kolom <code>{html.escape(col)}</code> punya {r['count']} outlier "
                f"({r['pct']:.2f}%) di luar rentang IQR [{r['lower']:.4g}, {r['upper']:.4g}]."
            )

    flat_result = detect_flatlines(df, num_cols)
    for col, runs in flat_result.items():
        if runs:
            longest = max(runs, key=lambda r: r["length"])
            out.append(
                f"Kolom <code>{html.escape(col)}</code> terindikasi sensor stuck: "
                f"nilai konstan {longest['length']} baris."
            )

    ts_cols = [c for c, t in col_types.items() if t == "datetime"]
    for col in ts_cols:
        s = pd.to_datetime(df[col].dropna(), errors="coerce")
        if not s.empty and s.nunique() > 1:
            gaps = s.sort_values().diff().dropna()
            mode_gap = gaps.mode().iloc[0]
            out.append(f"Interval data <code>{html.escape(col)}</code> umumnya {mode_gap}.")

    if not out:
        out.append("Data terlihat bersih: tidak ada outlier, missing value tinggi, atau flat-line.")
    return out


def _fmt(v: Any) -> str:
    return "-" if v is None else f"{v:,}" if isinstance(v, int) else f"{v:,.4g}"


def _chart_b64(path: Path) -> str:
    """Baca PNG jadi base64 untuk inline di HTML."""
    return base64.b64encode(path.read_bytes()).decode("ascii")


def _build_report_html(
    df: pd.DataFrame,
    file_name: str,
    col_types: dict[str, str],
    k: float,
    chart_dir: Path | None,
    insights: list[str],
) -> str:
    """Susun laporan HTML standalone (chart inline base64)."""
    num_cols = [c for c, t in col_types.items() if t == "numeric"]
    cat_cols = [c for c, t in col_types.items() if t in ("category", "text")]
    ts_cols = [c for c, t in col_types.items() if t == "datetime"]
    missing = missing_summary(df)
    e = html.escape

    rows_num = ""
    for s in numeric_stats(df, num_cols):
        rows_num += (
            f"<tr><td>{e(s['column'])}</td><td>{_fmt(s['count'])}</td><td>{_fmt(s['mean'])}</td>"
            f"<td>{_fmt(s['std'])}</td><td>{_fmt(s['min'])}</td><td>{_fmt(s['median'])}</td>"
            f"<td>{_fmt(s['max'])}</td></tr>\n"
        )

    rows_struct = ""
    for col, ctype in col_types.items():
        pct = missing[col]
        style = ' style="color:#b45309;font-weight:bold;"' if pct >= 10 else ""
        rows_struct += f"<tr><td>{e(col)}</td><td>{e(ctype)}</td><td{style}>{pct:.2f}%</td></tr>\n"

    rows_cat = ""
    for c in categorical_stats(df, cat_cols):
        top = ", ".join(f"{e(str(v))} ({n})" for v, n in c["top_values"]) or "-"
        rows_cat += f"<tr><td>{e(c['column'])}</td><td>{c['unique']}</td><td>{top}</td></tr>\n"

    rows_ts = ""
    for t in timestamp_stats(df, ts_cols):
        rows_ts += (
            f"<tr><td>{e(t['column'])}</td><td>{e(t['min_time'] or '-')}</td>"
            f"<td>{e(t['max_time'] or '-')}</td><td>{e(t['duration'] or '-')}</td></tr>\n"
        )

    chart_html = ""
    if chart_dir:
        for png in sorted(chart_dir.glob("*.png")):
            b64 = _chart_b64(png)
            chart_html += (
                f'<div class="chart"><h3>{e(png.stem)}</h3>'
                f'<img src="data:image/png;base64,{b64}" alt="{e(png.stem)}"/></div>\n'
            )

    insight_html = "\n".join(f"<li>{i}</li>" for i in insights)

    return f"""<!DOCTYPE html>
<html lang="id">
<head>
<meta charset="utf-8"/>
<title>Report — {e(file_name)}</title>
<style>
  body {{ font-family: 'Segoe UI', system-ui, sans-serif; margin: 40px auto; max-width: 960px; color: #1f2937; }}
  h1 {{ color: #1e3a8a; border-bottom: 2px solid #1e3a8a; padding-bottom: 8px; }}
  h2 {{ color: #1e3a8a; margin-top: 32px; }}
  table {{ border-collapse: collapse; width: 100%; margin: 12px 0; font-size: 14px; }}
  th, td {{ border: 1px solid #d1d5db; padding: 6px 10px; text-align: left; }}
  th {{ background: #eff6ff; }}
  code {{ background: #f3f4f6; padding: 1px 5px; border-radius: 3px; }}
  .meta {{ color: #6b7280; font-size: 13px; }}
  .insights {{ background: #fefce8; border-left: 4px solid #eab308; padding: 12px 16px; }}
  .chart {{ margin: 24px 0; }}
  .chart img {{ max-width: 100%; border: 1px solid #e5e7eb; }}
</style>
</head>
<body>
<h1>Data Analyzer Report</h1>
<p class="meta">File: <code>{e(file_name)}</code> &nbsp;|&nbsp; Baris: {len(df):,} &nbsp;|&nbsp; Kolom: {len(df.columns)} &nbsp;|&nbsp; Dibuat: {datetime.now().strftime("%Y-%m-%d %H:%M")}</p>

<h2>Insight Otomatis</h2>
<ul class="insights">
{insight_html}
</ul>

<h2>Struktur Kolom &amp; Missing Values</h2>
<table>
<tr><th>Kolom</th><th>Tipe</th><th>Missing (%)</th></tr>
{rows_struct}
</table>

<h2>Statistik Numerik</h2>
<table>
<tr><th>Kolom</th><th>Count</th><th>Mean</th><th>Std Dev</th><th>Min</th><th>Median</th><th>Max</th></tr>
{rows_num}
</table>

<h2>Distribusi Kategori / Teks</h2>
<table>
<tr><th>Kolom</th><th>Unique</th><th>Top Values</th></tr>
{rows_cat}
</table>

<h2>Rentang Waktu</h2>
<table>
<tr><th>Kolom</th><th>Mulai</th><th>Selesai</th><th>Durasi</th></tr>
{rows_ts}
</table>

<h2>Chart</h2>
{chart_html or "<p><em>(Tidak ada chart — jalankan dengan --charts untuk menyertakan visualisasi.)</em></p>"}
</body>
</html>
"""


def _build_report_md(
    df: pd.DataFrame,
    file_name: str,
    col_types: dict[str, str],
    chart_dir: Path | None,
    insights: list[str],
) -> str:
    """Susun laporan Markdown (chart sebagai link file PNG)."""
    num_cols = [c for c, t in col_types.items() if t == "numeric"]
    cat_cols = [c for c, t in col_types.items() if t in ("category", "text")]
    ts_cols = [c for c, t in col_types.items() if t == "datetime"]
    missing = missing_summary(df)

    lines = [
        f"# Data Analyzer Report — {file_name}",
        "",
        f"- **Baris:** {len(df):,} | **Kolom:** {len(df.columns)}",
        f"- **Dibuat:** {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        "",
        "## Insight Otomatis",
        "",
        *[f"- {i.replace('<code>', '`').replace('</code>', '`')}" for i in insights],
        "",
        "## Struktur Kolom & Missing Values",
        "",
        "| Kolom | Tipe | Missing (%) |",
        "|-------|------|------------:",
    ]
    for col, ctype in col_types.items():
        lines.append(f"| {col} | {ctype} | {missing[col]:.2f}% |")

    lines += ["", "## Statistik Numerik", "", "| Kolom | Count | Mean | Std Dev | Min | Median | Max |",
              "|-------|------:|-----:|--------:|----:|-------:|----:|"]
    for s in numeric_stats(df, num_cols):
        lines.append(
            f"| {s['column']} | {_fmt(s['count'])} | {_fmt(s['mean'])} | {_fmt(s['std'])} | "
            f"{_fmt(s['min'])} | {_fmt(s['median'])} | {_fmt(s['max'])} |"
        )

    lines += ["", "## Distribusi Kategori / Teks", "", "| Kolom | Unique | Top Values |", "|-------|-------:|------------|"]
    for c in categorical_stats(df, cat_cols):
        top = ", ".join(f"{v} ({n})" for v, n in c["top_values"]) or "-"
        lines.append(f"| {c['column']} | {c['unique']} | {top} |")

    lines += ["", "## Rentang Waktu", "", "| Kolom | Mulai | Selesai | Durasi |", "|-------|-------|---------|--------|"]
    for t in timestamp_stats(df, ts_cols):
        lines.append(f"| {t['column']} | {t['min_time'] or '-'} | {t['max_time'] or '-'} | {t['duration'] or '-'} |")

    if chart_dir:
        lines += ["", "## Chart", ""]
        for png in sorted(chart_dir.glob("*.png")):
            lines.append(f"![{png.stem}]({png.name})")

    return "\n".join(lines) + "\n"


def generate_report(
    file: Path,
    output: Path,
    k: float = 1.5,
    with_charts: bool = True,
    delimiter: str | None = None,
    columns: list[str] | None = None,
    row_start: int | None = None,
    row_end: int | None = None,
    show_progress: bool = False,
) -> Path:
    """Generate laporan (HTML/MD tergantung ekstensi output)."""
    df = load_dataframe(
        file, delimiter=delimiter, columns=columns,
        row_start=row_start, row_end=row_end, show_progress=show_progress,
    )
    col_types = detect_column_types(df)

    chart_dir: Path | None = None
    if with_charts and any(t == "numeric" for t in col_types.values()):
        from analyzer.plots import generate_charts

        chart_dir = output.resolve().parent / f"{output.stem}_charts"
        num_cols = [c for c, t in col_types.items() if t == "numeric"]
        ts_cols = [c for c, t in col_types.items() if t == "datetime"]
        x_col = ts_cols[0] if ts_cols else None
        generate_charts(df, num_cols, chart_dir, x_col=x_col, k=k)

    insights = _insights(df, col_types, k)
    file_name = file.name

    if output.suffix.lower() == ".md":
        content = _build_report_md(df, file_name, col_types, chart_dir, insights)
    else:
        content = _build_report_html(df, file_name, col_types, k, chart_dir, insights)

    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(content, encoding="utf-8")
    return output
