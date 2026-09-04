# ARCHITECTURE.md — Struktur Project

Dokumen ini menjelaskan struktur folder, alur data, dan tanggung jawab tiap module dalam **Data Analyzer CLI** — sesuai implementasi aktual (Fase 1–7 selesai).

---

## 1. Struktur Folder (aktual)

```
analyzer-data/
├── analyzer/                  # Source code utama (Python package)
│   ├── __init__.py            # Metadata & versi package
│   ├── cli.py                 # Entry point Typer: daftar command (load, plot, report, version)
│   ├── commands.py            # Implementasi command CLI: load, plot, report (output Rich tables)
│   ├── loader.py              # Baca CSV/TSV + csv.Sniffer delimiter + validasi + filter kolom/baris
│   ├── stats.py               # Kalkulasi statistik: numerik, kategori, timestamp
│   ├── outliers.py            # Deteksi outlier IQR + flat-line (sensor stuck)
│   ├── plots.py               # Generator chart PNG (matplotlib, backend Agg)
│   └── report.py              # Generator laporan HTML (inline base64) & Markdown
│
├── tests/
│   ├── fixtures/              # Dataset uji: clean, dirty, big (15k baris), outliers, flatline,
│   │                          #   pipe, semicolon, tsv, single-column, corrupt, empty, header-only
│   ├── test_loader.py         # Test parsing, delimiter sniffing, validasi
│   ├── test_stats.py          # Test kalkulasi statistik
│   ├── test_outliers.py       # Test IQR outlier & flat-line
│   ├── test_plots.py          # Test generate PNG
│   ├── test_report.py         # Test laporan HTML/MD
│   └── test_polish.py         # Test filter, progress bar, dataset uji
│
├── docs/                      # Dokumentasi internal pengembangan
│   ├── todo.md                # Rencana fase
│   ├── progress.md            # Status aktual (sumber kebenaran)
│   ├── architecture.md        # Dokumen ini
│   └── README.md              # Pointer ke README utama
│
├── .github/workflows/         # CI: pytest multi-OS & multi-Python
├── agent.md                   # Aturan wajib AI coding agent
├── pyproject.toml             # Metadata package + dependency + entry point
├── requirements.txt           # Dependency (alternatif pip install)
└── README.md                  # Dokumentasi user-facing utama
```

---

## 2. Alur Data (Data Flow)

```
File input (CSV/TSV/log)
        │
        ▼
 [loader._detect_delimiter]  → csv.Sniffer pada sample 64KB (koma/tab/;/|), fallback "," 1-kolom
        │
        ▼
 [loader.load_dataframe]     → pd.read_csv C-engine (sep eksplisit) + validasi
        │                      (empty, header-only, kolom kosong semua) + filter (--columns,
        │                      --row-start/end) + progress bar chunked (opsional)
        ▼
 [loader.detect_column_types]→ numeric / datetime / boolean / category / text / empty
 [loader.missing_summary]    → % missing per kolom
        │
        ├──────────────────────────────►  [commands.load] tampilkan di terminal (Rich)
        │
        ▼
 [stats.numeric_stats]       → count, mean, std, min, median, max
 [stats.categorical_stats]   → unique count + top values
 [stats.timestamp_stats]     → min/max/durasi rentang waktu
        │
        ▼
 [outliers.detect_outliers]  → IQR bounds [Q1-k·IQR, Q3+k·IQR], index & nilai outlier
 [outliers.detect_flatlines] → run nilai konstan ≥ N baris (sensor stuck)
        │
        ├──────────────────────────────►  [commands.load] tabel outlier + daftar baris
        │
        ▼
 [plots.generate_charts]     → {col}_line.png (outlier merah) + {col}_hist.png (garis mean)
        │
        ▼
 [report.generate_report]    → insight otomatis (missing tinggi, outlier, stuck, interval)
        │                      HTML standalone (base64 inline) atau Markdown + folder PNG
        ▼
 Output: tabel terminal / charts/ / report.html / report.md
```

Module independen (loose-coupled): bisa dites unit terpisah, dan dipanggil ulang oleh command lain (misal `report` memanggil `loader`, `stats`, `outliers`, `plots` sekaligus).

---

## 3. Tanggung Jawab Tiap Module

| Module | Tanggung jawab | Fase |
|---|---|---|
| `cli.py` | Entry point Typer; register command `load`, `plot`, `report`, `version` | 1, 7 |
| `commands.py` | Orkestrasi + format output Rich (tabel struktur, statistik, outlier, flat-line) | 1, 3, 4, 5, 6, 7 |
| `loader.py` | Delimiter sniffing (64KB sample), pd.read_csv C-engine, validasi dasar, filter kolom/baris, chunked progress read | 2, 7 |
| `stats.py` | Statistik numerik (mean/median/min/max/std), kategori (value counts), timestamp (rentang) | 3 |
| `outliers.py` | IQR bounds & deteksi outlier per kolom; flat-line run detection | 4 |
| `plots.py` | Line chart (highlight outlier) + histogram (mean line) → PNG via matplotlib Agg | 5 |
| `report.py` | Insight otomatis + laporan HTML standalone (base64) / Markdown (+ folder PNG) | 6 |
| `tests/` | 41 unit test + 14 fixture dataset | 7 |

---

## 4. Prinsip Desain

1. **Separation of concerns** — logic murni (`loader`, `stats`, `outliers`, `plots`, `report`) terpisah dari presentasi (`commands.py`); semua bisa dites tanpa CLI.
2. **CLI tipis, logic tebal** — `cli.py` hanya entry point; `commands.py` orkestrasi; kalkulasi ada di module masing-masing.
3. **Performa C-engine** — delimiter dideteksi via `csv.Sniffer` (sample 64KB), lalu di-pass eksplisit ke `pd.read_csv()` agar tetap pakai C engine (cepat untuk file besar; siap Fase 7+).
4. **Fail loud, fail clear** — semua kegagalan (file kosong, header-only, delimiter salah, kolom tak ada, rentang baris invalid) jadi `InvalidDataError` dengan pesan jelas, bukan raw traceback.
5. **Headless-safe** — matplotlib dipaksa backend `Agg` supaya aman dijalankan di server/CI tanpa display.

---

## 5. Update Dokumen Ini

Update `architecture.md` setiap kali:
- Ada module/file baru yang benar-benar dibuat.
- Ada perubahan alur data antar module.
- Struktur berubah karena keputusan teknis.
