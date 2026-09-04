"""Deteksi outlier IQR + flat-line (sensor stuck)."""

from typing import Any

import pandas as pd


def iqr_bounds(series: pd.Series, k: float = 1.5) -> tuple[float, float] | None:
    """Batas bawah/atas IQR: [Q1 - k*IQR, Q3 + k*IQR]. None kalau data kurang."""
    s = pd.to_numeric(series, errors="coerce").dropna()
    if len(s) < 4:
        return None
    q1, q3 = s.quantile(0.25), s.quantile(0.75)
    iqr = q3 - q1
    if iqr == 0:
        return (float(q1), float(q3))
    return (float(q1 - k * iqr), float(q3 + k * iqr))


def detect_outliers(df: pd.DataFrame, num_cols: list[str], k: float = 1.5) -> dict[str, dict[str, Any]]:
    """Deteksi outlier per kolom numerik pakai IQR.

    Return per kolom: count, pct, lower, upper, dan list (index, value) outlier.
    """
    result: dict[str, dict[str, Any]] = {}
    for col in num_cols:
        s = pd.to_numeric(df[col], errors="coerce")
        bounds = iqr_bounds(s, k)
        if bounds is None:
            result[col] = {"count": 0, "pct": 0.0, "lower": None, "upper": None, "rows": []}
            continue
        lower, upper = bounds
        mask = (s < lower) | (s > upper)
        rows = [(int(i), float(s.loc[i])) for i in s.index[mask.fillna(False)]]
        n = len(s.dropna())
        result[col] = {
            "count": len(rows),
            "pct": round(len(rows) / n * 100, 2) if n else 0.0,
            "lower": lower,
            "upper": upper,
            "rows": rows,
        }
    return result


def flatline_runs(series: pd.Series, min_run: int = 20, tol: float = 1e-12) -> list[dict[str, Any]]:
    """Deteksi run nilai sama berurutan (>= min_run) — indikasi sensor stuck.

    Return list run: start index (posisi baris), end index, length, value.
    """
    s = pd.to_numeric(series, errors="coerce").dropna()
    runs: list[dict[str, Any]] = []
    if len(s) < min_run:
        return runs

    prev_val: float | None = None
    run_start = 0
    run_len = 1
    for idx, val in s.items():
        if prev_val is not None and abs(val - prev_val) <= tol:
            run_len += 1
        else:
            if prev_val is not None and run_len >= min_run:
                runs.append({
                    "start": int(run_start),
                    "end": int(idx),
                    "length": run_len,
                    "value": float(prev_val),
                })
            run_start = idx
            run_len = 1
        prev_val = val
    if run_len >= min_run:
        runs.append({"start": int(run_start), "end": int(idx), "length": run_len, "value": float(prev_val)})
    return runs


def detect_flatlines(df: pd.DataFrame, num_cols: list[str], min_run: int = 20) -> dict[str, list[dict[str, Any]]]:
    """Deteksi flat-line per kolom numerik. Return per kolom list run."""
    return {col: flatline_runs(df[col], min_run=min_run) for col in num_cols}
