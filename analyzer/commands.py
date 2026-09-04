"""Command `analyzer load` — baca file, tampilkan info, validasi, dan ringkasan statistik."""

from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.table import Table

from analyzer.loader import InvalidDataError, detect_column_types, load_dataframe, missing_summary
from analyzer.outliers import detect_flatlines, detect_outliers
from analyzer.plots import generate_charts
from analyzer.report import generate_report
from analyzer.stats import categorical_stats, numeric_stats, timestamp_stats

console = Console()


def load(
    file: Path = typer.Argument(
        ..., exists=True, dir_okay=False, readable=True, help="Path file CSV/TSV/log."
    ),
    delimiter: Optional[str] = typer.Option(
        None, "--delimiter", "-d", help="Delimiter custom (misal ';' atau '\\t'). Default: auto-detect."
    ),
    columns: Optional[str] = typer.Option(
        None, "--columns", "-c", help="Filter kolom spesifik dipisah koma (misal: 'id,value')."
    ),
    row_start: Optional[int] = typer.Option(None, "--row-start", min=0, help="Index baris awal (0-indexed)."),
    row_end: Optional[int] = typer.Option(None, "--row-end", min=1, help="Index baris akhir (exclusive)."),
    progress: bool = typer.Option(False, "--progress", "-p", help="Tampilkan progress bar saat membaca file."),
    k: float = typer.Option(1.5, "--k", min=0.0, help="Pengali IQR untuk outlier (default 1.5)."),
    show_outlier_rows: int = typer.Option(
        0, "--show-outlier-rows", min=0,
        help="Tampilkan N baris outlier pertama per kolom (0 = ringkasan saja).",
    ),
    flat_min_run: int = typer.Option(
        20, "--flat-min-run", min=2, help="Panjang minimal run flat-line (default 20 baris)."
    ),
    no_flatline: bool = typer.Option(False, "--no-flatline", help="Matikan deteksi flat-line."),
) -> None:
    """Baca file CSV/TSV: tipe kolom, missing values, statistik, outlier & flat-line."""
    cols_list = [c.strip() for c in columns.split(",")] if columns else None
    try:
        df = load_dataframe(
            file, delimiter=delimiter, columns=cols_list,
            row_start=row_start, row_end=row_end, show_progress=progress,
        )
    except InvalidDataError as e:
        typer.secho(f"Error: {e}", fg=typer.colors.RED, err=True)
        raise typer.Exit(code=1)

    typer.secho(f"\nFile    : {file}", fg=typer.colors.CYAN)
    typer.echo(f"Baris   : {len(df)}")
    typer.echo(f"Kolom   : {len(df.columns)}")

    col_types = detect_column_types(df)
    missing = missing_summary(df)

    # 1. Tipe Kolom & Missing Values
    typer.secho("\n--- Structure & Completeness ---", fg=typer.colors.GREEN)
    struct_table = Table(show_header=True, header_style="bold magenta")
    struct_table.add_column("Kolom")
    struct_table.add_column("Tipe")
    struct_table.add_column("Missing (%)")

    for col, ctype in col_types.items():
        pct = missing[col]
        pct_str = f"[yellow]{pct:.2f}%[/yellow]" if pct > 0 else "0.00%"
        struct_table.add_row(col, ctype, pct_str)
    console.print(struct_table)

    # 2. Statistik Kolom Numerik
    num_cols = [c for c, t in col_types.items() if t == "numeric"]
    if num_cols:
        typer.secho("\n--- Ringkasan Statistik (Numerik) ---", fg=typer.colors.GREEN)
        num_table = Table(show_header=True, header_style="bold cyan")
        num_table.add_column("Kolom")
        num_table.add_column("Count", justify="right")
        num_table.add_column("Mean", justify="right")
        num_table.add_column("Std Dev", justify="right")
        num_table.add_column("Min", justify="right")
        num_table.add_column("Median", justify="right")
        num_table.add_column("Max", justify="right")

        for s in numeric_stats(df, num_cols):
            num_table.add_row(
                s["column"],
                str(s["count"]),
                str(s["mean"]) if s["mean"] is not None else "-",
                str(s["std"]) if s["std"] is not None else "-",
                str(s["min"]) if s["min"] is not None else "-",
                str(s["median"]) if s["median"] is not None else "-",
                str(s["max"]) if s["max"] is not None else "-",
            )
        console.print(num_table)

    # 3. Distribusi Kolom Kategori / Teks
    cat_cols = [c for c, t in col_types.items() if t in ("category", "text")]
    if cat_cols:
        typer.secho("\n--- Distribusi Kategori / Teks ---", fg=typer.colors.GREEN)
        cat_table = Table(show_header=True, header_style="bold blue")
        cat_table.add_column("Kolom")
        cat_table.add_column("Unique Values", justify="right")
        cat_table.add_column("Top Values (Nilai: Jumlah)")

        for c in categorical_stats(df, cat_cols):
            top_str = ", ".join(f"{val}: {cnt}" for val, cnt in c["top_values"]) if c["top_values"] else "-"
            cat_table.add_row(c["column"], str(c["unique"]), top_str)
        console.print(cat_table)

    # 4. Rentang Waktu (Timestamp)
    ts_cols = [c for c, t in col_types.items() if t == "datetime"]
    if ts_cols:
        typer.secho("\n--- Rentang Waktu (Timestamp) ---", fg=typer.colors.GREEN)
        ts_table = Table(show_header=True, header_style="bold yellow")
        ts_table.add_column("Kolom")
        ts_table.add_column("Mulai (Min)")
        ts_table.add_column("Selesai (Max)")
        ts_table.add_column("Durasi")

        for t in timestamp_stats(df, ts_cols):
            ts_table.add_row(
                t["column"],
                t["min_time"] or "-",
                t["max_time"] or "-",
                t["duration"] or "-",
            )
        console.print(ts_table)

    # 5. Outlier (IQR) & Flat-line
    num_cols = [c for c, t in col_types.items() if t == "numeric"]
    if num_cols:
        typer.secho(f"\n--- Outlier (IQR, k={k}) ---", fg=typer.colors.GREEN)
        out_table = Table(show_header=True, header_style="bold red")
        out_table.add_column("Kolom")
        out_table.add_column("Batas Bawah", justify="right")
        out_table.add_column("Batas Atas", justify="right")
        out_table.add_column("Outlier", justify="right")
        out_table.add_column("%", justify="right")

        outlier_result = detect_outliers(df, num_cols, k=k)
        for col, r in outlier_result.items():
            if r["lower"] is None:
                out_table.add_row(col, "-", "-", "0", "0.00%")
                continue
            out_table.add_row(
                col, f"{r['lower']:.4g}", f"{r['upper']:.4g}", str(r["count"]), f"{r['pct']:.2f}%"
            )
            if show_outlier_rows > 0 and r["rows"]:
                for i, val in r["rows"][:show_outlier_rows]:
                    side = "bawah" if val < r["lower"] else "atas"
                    typer.secho(f"    baris {i}: {val:g} ({side} batas)", fg=typer.colors.YELLOW)
                shown = min(show_outlier_rows, len(r["rows"]))
                if shown < len(r["rows"]):
                    typer.echo(f"    ... {len(r['rows']) - shown} outlier lain tidak ditampilkan")
        console.print(out_table)

        if not no_flatline:
            typer.secho(f"\n--- Flat-line (sensor stuck, >= {flat_min_run} baris) ---", fg=typer.colors.GREEN)
            flat_result = detect_flatlines(df, num_cols, min_run=flat_min_run)
            found_any = False
            for col, runs in flat_result.items():
                for run in runs:
                    found_any = True
                    typer.secho(
                        f"  {col}: baris {run['start']}–{run['end']} "
                        f"({run['length']} baris) nilai konstan {run['value']:g}",
                        fg=typer.colors.RED,
                    )
            if not found_any:
                typer.secho("  Tidak ada flat-line terdeteksi.", fg=typer.colors.GREEN)

    all_empty_cols = [col for col in df.columns if df[col].isna().all()]
    if all_empty_cols:
        typer.secho(f"\nPeringatan: kolom berikut 100% kosong: {', '.join(all_empty_cols)}", fg=typer.colors.YELLOW)


def plot(
    file: Path = typer.Argument(
        ..., exists=True, dir_okay=False, readable=True, help="Path file CSV/TSV/log."
    ),
    out_dir: Path = typer.Option(
        Path("charts"), "--out-dir", "-o", help="Direktori tujuan PNG (default: ./charts)."
    ),
    delimiter: Optional[str] = typer.Option(
        None, "--delimiter", "-d", help="Delimiter custom (misal ';' atau '\\t'). Default: auto-detect."
    ),
    columns: Optional[str] = typer.Option(
        None, "--columns", "-c", help="Filter kolom spesifik dipisah koma."
    ),
    row_start: Optional[int] = typer.Option(None, "--row-start", min=0, help="Index baris awal (0-indexed)."),
    row_end: Optional[int] = typer.Option(None, "--row-end", min=1, help="Index baris akhir (exclusive)."),
    progress: bool = typer.Option(False, "--progress", "-p", help="Tampilkan progress bar saat membaca file."),
    k: float = typer.Option(1.5, "--k", min=0.0, help="Pengali IQR untuk highlight outlier (default 1.5)."),
    time_col: Optional[str] = typer.Option(
        None, "--time-col", help="Kolom timestamp untuk sumbu-x line chart. Default: kolom datetime terdeteksi."
    ),
) -> None:
    """Generate line chart + histogram (PNG) untuk kolom numerik, outlier di-highlight."""
    cols_list = [c.strip() for c in columns.split(",")] if columns else None
    try:
        df = load_dataframe(
            file, delimiter=delimiter, columns=cols_list,
            row_start=row_start, row_end=row_end, show_progress=progress,
        )
    except InvalidDataError as e:
        typer.secho(f"Error: {e}", fg=typer.colors.RED, err=True)
        raise typer.Exit(code=1)

    col_types = detect_column_types(df)
    num_cols = [c for c, t in col_types.items() if t == "numeric"]

    if not num_cols:
        typer.secho("Tidak ada kolom numerik untuk di-plot.", fg=typer.colors.YELLOW, err=True)
        raise typer.Exit(code=1)

    ts_cols = [c for c, t in col_types.items() if t == "datetime"]
    x_col = time_col or (ts_cols[0] if ts_cols else None)

    try:
        paths = generate_charts(df, num_cols, out_dir, x_col=x_col, k=k)
    except OSError as e:
        typer.secho(f"Error saat menulis chart: {e}", fg=typer.colors.RED, err=True)
        raise typer.Exit(code=1)

    typer.secho(f"Generated {len(paths)} chart di: {out_dir.resolve()}", fg=typer.colors.GREEN)
    for p in paths:
        typer.echo(f"  {p.name}")


def report(
    file: Path = typer.Argument(
        ..., exists=True, dir_okay=False, readable=True, help="Path file CSV/TSV/log."
    ),
    output: Path = typer.Option(
        Path("report.html"), "--output", "-o",
        help="File laporan tujuan. Ekstensi menentukan format: .html atau .md (default: report.html)."
    ),
    no_charts: bool = typer.Option(False, "--no-charts", help="Jangan sertakan chart di laporan."),
    delimiter: Optional[str] = typer.Option(
        None, "--delimiter", "-d", help="Delimiter custom (misal ';' atau '\\t'). Default: auto-detect."
    ),
    columns: Optional[str] = typer.Option(
        None, "--columns", "-c", help="Filter kolom spesifik dipisah koma."
    ),
    row_start: Optional[int] = typer.Option(None, "--row-start", min=0, help="Index baris awal (0-indexed)."),
    row_end: Optional[int] = typer.Option(None, "--row-end", min=1, help="Index baris akhir (exclusive)."),
    progress: bool = typer.Option(False, "--progress", "-p", help="Tampilkan progress bar saat membaca file."),
    k: float = typer.Option(1.5, "--k", min=0.0, help="Pengali IQR untuk deteksi outlier (default 1.5)."),
) -> None:
    """Generate laporan otomatis (HTML/Markdown): statistik + insight + chart."""
    if output.suffix.lower() not in (".html", ".md"):
        typer.secho(
            f"Error: ekstensi '{output.suffix}' tidak didukung. Gunakan .html atau .md.",
            fg=typer.colors.RED, err=True,
        )
        raise typer.Exit(code=1)

    cols_list = [c.strip() for c in columns.split(",")] if columns else None
    try:
        path = generate_report(
            file, output, k=k, with_charts=not no_charts, delimiter=delimiter,
            columns=cols_list, row_start=row_start, row_end=row_end, show_progress=progress,
        )
    except InvalidDataError as e:
        typer.secho(f"Error: {e}", fg=typer.colors.RED, err=True)
        raise typer.Exit(code=1)
    except OSError as e:
        typer.secho(f"Error saat menulis laporan: {e}", fg=typer.colors.RED, err=True)
        raise typer.Exit(code=1)

    typer.secho(f"Laporan dibuat: {path.resolve()}", fg=typer.colors.GREEN)
