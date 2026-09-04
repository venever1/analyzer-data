"""Visualisasi: line chart + histogram, export PNG (matplotlib, backend Agg)."""

from pathlib import Path

import matplotlib

matplotlib.use("Agg")  # headless, tanpa GUI
import matplotlib.pyplot as plt
import pandas as pd


def plot_line(
    df: pd.DataFrame,
    col: str,
    path: Path,
    x_col: str | None = None,
    outlier_idx: list | None = None,
) -> Path:
    """Line chart kolom numerik vs timestamp/index, outlier di-highlight merah."""
    fig, ax = plt.subplots(figsize=(10, 5))
    x = pd.to_datetime(df[x_col]) if x_col else df.index

    ax.plot(x, df[col], color="tab:blue", linewidth=1.0, label=col)
    if outlier_idx:
        ax.scatter(
            x.loc[outlier_idx] if x_col else [x[i] for i in outlier_idx],
            df.loc[outlier_idx, col],
            color="red",
            s=40,
            zorder=3,
            label="outlier",
        )
        ax.legend()

    ax.set_title(f"{col} vs {x_col or 'index'}")
    ax.set_xlabel(x_col or "index")
    ax.set_ylabel(col)
    fig.tight_layout()
    fig.savefig(path, dpi=120)
    plt.close(fig)
    return path


def plot_hist(df: pd.DataFrame, col: str, path: Path, bins: int = 30) -> Path:
    """Histogram distribusi kolom numerik."""
    s = pd.to_numeric(df[col], errors="coerce").dropna()
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.hist(s, bins=bins, color="tab:blue", edgecolor="white")
    ax.axvline(s.mean(), color="orange", linestyle="--", linewidth=1.5, label=f"mean={s.mean():.3g}")
    ax.legend()
    ax.set_title(f"Distribusi {col}")
    ax.set_xlabel(col)
    ax.set_ylabel("frekuensi")
    fig.tight_layout()
    fig.savefig(path, dpi=120)
    plt.close(fig)
    return path


def generate_charts(
    df: pd.DataFrame,
    num_cols: list[str],
    out_dir: Path,
    x_col: str | None = None,
    k: float = 1.5,
) -> list[Path]:
    """Generate line chart + histogram untuk semua kolom numerik ke `out_dir`.

    Line chart highlight outlier IQR. Kolom kosong semua di-skip.
    Return list path PNG yang dibuat.
    """
    from analyzer.outliers import detect_outliers

    out_dir.mkdir(parents=True, exist_ok=True)
    out_dir = out_dir.resolve()
    outlier_result = detect_outliers(df, num_cols, k=k)

    paths: list[Path] = []
    for col in num_cols:
        s = pd.to_numeric(df[col], errors="coerce")
        if s.dropna().empty:
            continue
        safe = col.replace(" ", "_").replace("/", "_")
        paths.append(plot_line(df, col, out_dir / f"{safe}_line.png", x_col=x_col,
                               outlier_idx=[i for i, _ in outlier_result[col]["rows"]]))
        paths.append(plot_hist(df, col, out_dir / f"{safe}_hist.png"))
    return paths
