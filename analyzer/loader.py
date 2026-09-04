"""Loader: baca CSV/TSV/log dengan delimiter custom + validasi dasar."""

import csv
from pathlib import Path

import pandas as pd
import rich.progress

# Jumlah byte yang dibaca untuk sniffing delimiter. Cukup banyak baris supaya
# csv.Sniffer tidak salah tebak (misal koma di dalam teks), tapi tetap murah.
_SNIFF_SAMPLE_BYTES = 64 * 1024
# Kandidat delimiter yang diperbolehkan saat sniffing.
_SNIFF_DELIMITERS = [",", "\t", ";", "|"]


class InvalidDataError(Exception):
    """Data tidak valid (kosong, kolom kosong semua, dsb)."""


def _detect_delimiter(path: Path) -> str:
    """Deteksi delimiter dari sample awal file pakai csv.Sniffer.

    Baca sampel multi-baris (bukan cuma baris pertama) supaya deteksi lebih akurat.
    Raise InvalidDataError kalau sample kosong / delimiter tidak bisa ditentukan.
    """
    try:
        with open(path, encoding="utf-8", newline="") as f:
            sample = f.read(_SNIFF_SAMPLE_BYTES)
    except OSError as e:
        raise InvalidDataError(f"Tidak bisa membaca '{path}': {e}") from e
    except UnicodeDecodeError as e:
        raise InvalidDataError(f"File '{path}' bukan teks UTF-8 yang valid.") from e

    if not sample.strip():
        raise InvalidDataError(f"File '{path}' kosong / tidak punya data.")

    try:
        return csv.Sniffer().sniff(sample, delimiters="".join(_SNIFF_DELIMITERS)).delimiter
    except csv.Error:
        # Tidak ada delimiter kandidat di sample -> kemungkinan file 1 kolom.
        # Fallback ke "," aman: pandas tetap baca sebagai 1 kolom.
        return ","


def _apply_filters(
    df: pd.DataFrame,
    columns: list[str] | None = None,
    row_range: tuple[int, int | None] | None = None,
) -> pd.DataFrame:
    """Filter DataFrame berdasarkan daftar kolom dan/atau rentang baris [start, end)."""
    if columns:
        missing_cols = [c for c in columns if c not in df.columns]
        if missing_cols:
            raise InvalidDataError(f"Kolom tidak ditemukan: {', '.join(missing_cols)}. "
                                   f"Kolom tersedia: {', '.join(df.columns)}")
        df = df[columns]
    if row_range:
        start, end = row_range
        df = df.iloc[start:end]
        if df.empty:
            raise InvalidDataError(f"Rentang baris [{start}:{end}] menghasilkan 0 baris (file punya {len(df)} baris).")
    return df


def load_dataframe(
    path: Path,
    delimiter: str | None = None,
    columns: list[str] | None = None,
    row_start: int | None = None,
    row_end: int | None = None,
    show_progress: bool = False,
) -> pd.DataFrame:
    """Baca file delimited jadi DataFrame.

    Kalau `delimiter` diberikan, dipakai langsung. Kalau tidak, delimiter
    dideteksi dari sample file (csv.Sniffer), lalu dipass eksplisit ke
    pandas.read_csv() agar bisa pakai C engine (cepat, penting untuk file besar).
    `columns` / `row_start`/`row_end` untuk filter kolom & rentang baris.
    `show_progress` menampilkan progress bar chunked-read (untuk file besar).
    Raise InvalidDataError dengan pesan jelas kalau file bermasalah.
    """
    sep = delimiter if delimiter else _detect_delimiter(path)
    row_range = (row_start, row_end) if (row_start is not None or row_end is not None) else None

    try:
        if show_progress:
            chunks = []
            with rich.progress.Progress(
                rich.progress.TextColumn("[progress.description]{task.description}"),
                rich.progress.BarColumn(bar_width=40),
                rich.progress.TextColumn("{task.completed} chunks"),
            ) as progress:
                task = progress.add_task("Membaca file...", total=None)
                reader = pd.read_csv(path, sep=sep, chunksize=10_000)
                for chunk in reader:
                    chunks.append(chunk)
                    progress.update(task, completed=len(chunks))
            df = pd.concat(chunks, ignore_index=True)
        else:
            df = pd.read_csv(path, sep=sep)  # C engine default
    except pd.errors.EmptyDataError as e:
        raise InvalidDataError(f"File '{path}' kosong / tidak punya data.") from e
    except pd.errors.ParserError as e:
        raise InvalidDataError(f"File '{path}' gagal di-parse (delimiter salah / struktur rusak): {e}") from e
    except UnicodeDecodeError as e:
        raise InvalidDataError(f"File '{path}' bukan teks UTF-8 yang valid.") from e
    except OSError as e:
        raise InvalidDataError(f"Tidak bisa membaca '{path}': {e}") from e
    except Exception as e:
        raise InvalidDataError(f"File '{path}' gagal dibaca: {e}") from e

    if df.shape[1] == 0:
        raise InvalidDataError(f"File '{path}' tidak punya kolom sama sekali.")
    if len(df) == 0:
        raise InvalidDataError(f"File '{path}' cuma berisi header, tanpa data baris.")
    if all(pd.isna(df[col]).all() or (df[col].astype(str).str.strip() == "").all() for col in df.columns):
        raise InvalidDataError(f"Semua kolom di '{path}' kosong / berisi nilai kosong.")

    df = _apply_filters(df, columns=columns, row_range=row_range)
    return df


def detect_column_types(df: pd.DataFrame, timestamp_cols: list[str] | None = None) -> dict[str, str]:
    """Deteksi tipe tiap kolom: numeric, datetime, boolean, category, text.

    Kolom sudah-typed pandas dipercaya. Kolom object diuji: parseable sebagai tanggal -> datetime,
    semua non-null numerik -> numeric, unique ratio rendah -> category, sisanya text.
    """
    types: dict[str, str] = {}
    for col in df.columns:
        series = df[col]
        if pd.api.types.is_numeric_dtype(series):
            types[col] = "numeric"
        elif pd.api.types.is_datetime64_any_dtype(series):
            types[col] = "datetime"
        elif pd.api.types.is_bool_dtype(series):
            types[col] = "boolean"
        else:
            non_null = series.dropna().astype(str).str.strip()
            if non_null.empty:
                types[col] = "empty"
            elif timestamp_cols and col in timestamp_cols:
                types[col] = "datetime"
            else:
                sample = non_null
                parsed = pd.to_datetime(sample, errors="coerce", format="mixed")
                if parsed.notna().mean() >= 0.9:
                    types[col] = "datetime"
                elif pd.to_numeric(sample, errors="coerce").notna().mean() >= 0.9:
                    types[col] = "numeric"
                elif series.nunique(dropna=True) <= max(20, len(series) * 0.05):
                    types[col] = "category"
                else:
                    types[col] = "text"
    return types


def missing_summary(df: pd.DataFrame) -> dict[str, float]:
    """Persentase missing value per kolom (0-100)."""
    return {col: round(float(df[col].isna().mean() * 100), 2) for col in df.columns}
