"""Kalkulator statistik: numerik, kategori, dan timestamp."""

from typing import Any

import pandas as pd


def numeric_stats(df: pd.DataFrame, num_cols: list[str]) -> list[dict[str, Any]]:
    """Hitung mean, median, min, max, std dev untuk setiap kolom numerik."""
    result = []
    for col in num_cols:
        series = df[col].dropna()
        if series.empty:
            result.append({
                "column": col,
                "count": 0,
                "mean": None,
                "std": None,
                "min": None,
                "median": None,
                "max": None,
            })
            continue
        result.append({
            "column": col,
            "count": len(series),
            "mean": round(float(series.mean()), 4),
            "std": round(float(series.std()), 4) if len(series) > 1 else 0.0,
            "min": round(float(series.min()), 4),
            "median": round(float(series.median()), 4),
            "max": round(float(series.max()), 4),
        })
    return result


def categorical_stats(df: pd.DataFrame, cat_cols: list[str], top_n: int = 5) -> list[dict[str, Any]]:
    """Hitung statistik distribusi/value counts untuk kolom kategori/teks."""
    result = []
    for col in cat_cols:
        series = df[col].dropna().astype(str)
        if series.empty:
            result.append({
                "column": col,
                "unique": 0,
                "top_values": [],
            })
            continue
        val_counts = series.value_counts().head(top_n)
        top_values = [(val, int(cnt)) for val, cnt in val_counts.items()]
        result.append({
            "column": col,
            "unique": series.nunique(),
            "top_values": top_values,
        })
    return result


def timestamp_stats(df: pd.DataFrame, ts_cols: list[str]) -> list[dict[str, Any]]:
    """Deteksi rentang waktu (min ts, max ts, durasi/span) untuk kolom timestamp."""
    result = []
    for col in ts_cols:
        series = pd.to_datetime(df[col].dropna(), errors="coerce").dropna()
        if series.empty:
            result.append({
                "column": col,
                "min_time": None,
                "max_time": None,
                "duration": None,
            })
            continue
        min_t = series.min()
        max_t = series.max()
        duration = max_t - min_t
        result.append({
            "column": col,
            "min_time": str(min_t),
            "max_time": str(max_t),
            "duration": str(duration),
        })
    return result
