# Data Analyzer CLI

[![Tests](https://github.com/venever1/analyzer-data/actions/workflows/tests.yml/badge.svg)](https://github.com/venever1/analyzer-data/actions/workflows/tests.yml)
![Python](https://img.shields.io/badge/python-3.10%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)

CLI tool Python general-purpose untuk membaca file CSV/TSV/log, menampilkan ringkasan statistik, deteksi anomali/outlier, visualisasi chart (PNG), dan generate laporan otomatis (HTML/Markdown).

> Dibuat untuk analisis data cepat langsung dari terminal — tanpa perlu buka Excel atau tulis script Python manual.

---

## Daftar Isi

1. [Fitur Utama](#-fitur-utama)
2. [Instalasi](#-instalasi)
3. [Cara Penggunaan](#️-cara-penggunaan)
   - [`analyzer load` — Analisis Data](#1-analyzer-load--analisis-data)
   - [`analyzer plot` — Visualisasi Chart](#2-analyzer-plot--visualisasi-chart)
   - [`analyzer report` — Laporan Otomatis](#3-analyzer-report--laporan-otomatis)
4. [Referensi Opsi Lengkap](#-referensi-opsi-lengkap)
5. [Contoh Dataset](#-contoh-dataset)
6. [Troubleshooting](#-troubleshooting)
7. [Testing](#-testing)
8. [Struktur Project](#-struktur-project)

---

## 🚀 Fitur Utama

| Fitur | Penjelasan |
|-------|-----------|
| **Auto-Sniff Delimiter** | Mengenali otomatis koma `,`, tab `\t`, titik-koma `;`, dan pipe `\|` — tidak perlu ditentukan manual. |
| **Auto-Detect Tipe Kolom** | Setiap kolom dideteksi otomatis sebagai `numeric`, `datetime`, `category`, `boolean`, atau `text`. |
| **Ringkasan Statistik** | Count, mean, median, min, max, std dev untuk kolom numerik; value counts untuk kolom kategori; rentang waktu untuk kolom timestamp. |
| **Deteksi Outlier** | Metode **IQR** (default `k=1.5`). Nilai di luar `[Q1 - k·IQR, Q3 + k·IQR]` ditandai sebagai outlier. |
| **Deteksi Flat-line** | Deteksi nilai konstan beruntun (indikasi sensor mati/stuck), default minimal 20 baris. |
| **Visualisasi PNG** | Line chart (outlier di-highlight merah) + histogram per kolom numerik. |
| **Laporan Otomatis** | HTML standalone (chart inline base64, 1 file portabel) atau Markdown + folder PNG. |
| **Filter Data** | Analisis kolom tertentu (`-c`) dan/atau rentang baris (`--row-start`, `--row-end`). |
| **Progress Bar** | Untuk file besar, tampilkan progress pembacaan dengan `-p`. |

---

## 📦 Instalasi

### Prasyarat

- **Python 3.10 atau lebih baru** — cek dengan:
  ```bash
  python --version
  ```
  Kalau belum terinstall, unduh dari [python.org](https://www.python.org/downloads/). Saat instalasi di Windows, centang **"Add Python to PATH"**.

### Langkah Instalasi

**1. Clone / unduh project**

```bash
git clone https://github.com/user/analyzer-data.git   # ganti dengan URL repo asli Anda
cd analyzer-data
```

*(Atau unduh ZIP lalu ekstrak dan masuk ke foldernya.)*

**2. Buat virtual environment** (praktik baik supaya dependency tidak mengotorisi Python global):

```bash
python -m venv .venv
```

**3. Aktifkan virtual environment:**

| OS | Command |
|----|---------|
| Windows (PowerShell) | `.venv\Scripts\Activate.ps1` |
| Windows (CMD) | `.venv\Scripts\activate.bat` |
| Linux / macOS | `source .venv/bin/activate` |

> Kalau PowerShell memblokir script, jalankan sekali: `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser`

**4. Install package beserta dependency-nya:**

```bash
pip install -e .
```

Ini otomatis menginstall: `typer` (CLI framework), `pandas` (data processing), `matplotlib` (chart), dan `rich` (tabel & progress bar).

**5. Verifikasi instalasi:**

```bash
analyzer version
# Output: analyzer 0.1.0

analyzer --help
# Menampilkan daftar semua command
```

Jika `analyzer` tidak dikenali, pastikan virtual environment aktif, atau gunakan `python -m analyzer.cli` sebagai alternatif.

### Instalasi dari requirements.txt (alternatif)

```bash
pip install -r requirements.txt
```

Lalu jalankan lewat `python -m analyzer.cli ...` (tanpa entry point `analyzer`).

---

## ️🛠️ Cara Penggunaan

Terdapat **4 command**: `load`, `plot`, `report`, dan `version`.

```
analyzer <command> <file.csv> [opsi]
```

---

### 1. `analyzer load` — Analisis Data

Command utama: baca file, validasi, dan tampilkan laporan lengkap di terminal.

**Contoh paling dasar:**

```bash
analyzer load tests/fixtures/sample.csv
```

**Output (nyata):**

```
File    : tests\fixtures\sample.csv
Baris   : 6
Kolom   : 4

--- Structure & Completeness ---
┏━━━━━━━━━━━┳━━━━━━━━━━┳━━━━━━━━━━━━━┓
┃ Kolom     ┃ Tipe     ┃ Missing (%) ┃
┡━━━━━━━━━━━╇━━━━━━━━━━╇━━━━━━━━━━━━━┩
│ id        │ numeric  │ 0.00%       │
│ timestamp │ datetime │ 0.00%       │
│ value     │ numeric  │ 16.67%      │
│ category  │ category │ 0.00%       │
└───────────┴──────────┴─────────────┘

--- Ringkasan Statistik (Numerik) ---
┏━━━━━━━┳━━━━━━━┳━━━━━━━┳━━━━━━━━━┳━━━━━┳━━━━━━━━┳━━━━━━┓
┃ Kolom ┃ Count ┃  Mean ┃ Std Dev ┃ Min ┃ Median ┃  Max ┃
┡━━━━━━━╇━━━━━━━╇━━━━━━━╇━━━━━━━━━╇━━━━━╇━━━━━━━━╇━━━━━━┩
│ id    │     6 │   3.5 │  1.8708 │ 1.0 │    3.5 │  6.0 │
│ value │     5 │ 10.72 │  0.9418 │ 9.8 │   10.5 │ 12.1 │
└───────┴───────┴───────┴─────────┴─────┴────────┴──────┘

--- Distribusi Kategori / Teks ---
┏━━━━━━━━━━┳━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ Kolom    ┃ Unique Values ┃ Top Values (Nilai: Jumlah) ┃
┡━━━━━━━━━━╇━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━┩
│ category │             3 │ A: 2, B: 2, C: 2           │
└──────────┴───────────────┴────────────────────────────┘

--- Rentang Waktu (Timestamp) ---
┏━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━┓
┃ Kolom     ┃ Mulai (Min)         ┃ Selesai (Max)       ┃ Durasi          ┃
┡━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━┩
│ timestamp │ 2026-01-01 00:00:00 │ 2026-01-01 05:00:00 │ 0 days 05:00:00 │
└───────────┴─────────────────────┴─────────────────────┴─────────────────┘

--- Outlier (IQR, k=1.5) ---
┏━━━━━━━┳━━━━━━━━━━━━━┳━━━━━━━━━━━━┳━━━━━━━━━┳━━━━━━━┓
┃ Kolom ┃ Batas Bawah ┃ Batas Atas ┃ Outlier ┃     % ┃
┡━━━━━━━╇━━━━━━━━━━━━━╇━━━━━━━━━━━━╇━━━━━━━━━╇━━━━━━━┩
│ id    │        -1.5 │        8.5 │       0 │ 0.00% │
│ value │         8.2 │         13 │       0 │ 0.00% │
└───────┴─────────────┴────────────┴─────────┴───────┘

--- Flat-line (sensor stuck, >= 20 baris) ---
  Tidak ada flat-line terdeteksi.
```

**Contoh lanjutan:**

```bash
# Tampilkan daftar baris outlier (5 baris pertama per kolom)
analyzer load data/sensor.csv --show-outlier-rows 5

# Longgarkan threshold outlier (k=2.0 lebih toleran; k=1.0 lebih ketat)
analyzer load data/sensor.csv --k 2.0

# Deteksi flat-line lebih sensitif (nilai konstan >= 10 baris dianggap stuck)
analyzer load data/sensor.csv --flat-min-run 10

# Matikan deteksi flat-line
analyzer load data/sensor.csv --no-flatline

# Analisis file besar dengan progress bar
analyzer load big_export.csv -p

# Analisis hanya kolom tertentu + rentang baris 0-5000
analyzer load big_export.csv -c "timestamp,voltage,current" --row-start 0 --row-end 5000

# File dengan delimiter non-standar (misal titik-koma dari Excel Eropa)
analyzer load euro_data.csv -d ";"
```

---

### 2. `analyzer plot` — Visualisasi Chart

Generate **PNG** untuk setiap kolom numerik: 1 line chart (outlier merah) + 1 histogram (dengan garis mean oranye).

```bash
# Simpan ke folder ./charts (default)
analyzer plot data/sensor.csv

# Simpan ke folder tertentu
analyzer plot data/sensor.csv -o hasil_chart/

# Plot hanya kolom tertentu
analyzer plot data/sensor.csv -c "voltage,current" -o charts/

# Paksa kolom timestamp tertentu sebagai sumbu-x
analyzer plot data/sensor.csv --time-col timestamp

# File besar + rentang baris
analyzer plot big_export.csv --row-start 0 --row-end 20000 -p
```

**Hasil yang dihasilkan** (per kolom numerik):

| File | Isi |
|------|-----|
| `{kolom}_line.png` | Line chart nilai vs waktu/index; titik outlier berwarna **merah** |
| `{kolom}_hist.png` | Histogram distribusi + garis putus-putus mean |

Buka PNG-nya dengan image viewer biasa.

---

### 3. `analyzer report` — Laporan Otomatis

Gabungan semua analisis dalam satu file laporan: statistik + insight otomatis + chart. **Format ditentukan dari ekstensi file output** (`.html` atau `.md`).

```bash
# HTML standalone — 1 file, semua chart ter-embed (base64), tinggal dibuka di browser
analyzer report data/sensor.csv -o report.html

# Markdown — file .md + folder report_charts/ berisi PNG
analyzer report data/sensor.csv -o report.md

# Tanpa chart (lebih cepat, file lebih kecil)
analyzer report data/sensor.csv -o report.html --no-charts

# Laporan untuk subset data
analyzer report big_export.csv -o q1_report.html -c "timestamp,voltage" --row-start 0 --row-end 10000
```

**Isi laporan:**

1. **Insight Otomatis** — temuan penting: missing value tinggi (≥10%), jumlah outlier per kolom, indikasi sensor stuck, interval data umum.
2. **Struktur Kolom & Missing Values** — tabel tipe kolom + persentase data kosong.
3. **Statistik Numerik** — count, mean, std, min, median, max.
4. **Distribusi Kategori** — unique count + top values.
5. **Rentang Waktu** — min/max timestamp + durasi.
6. **Chart** — line chart + histogram (inline di HTML, link di Markdown).

> 💡 **HTML vs Markdown?** HTML bagus untuk dibagikan/dibuka langsung di browser (portabel, 1 file). Markdown bagus untuk GitHub/wiki/dokumentasi repo.

---

### 4. `analyzer version`

```bash
analyzer version
# analyzer 0.1.0
```

---

## 📋 Referensi Opsi Lengkap

### Opsi umum (tersedia di `load`, `plot`, dan `report`)

| Opsi | Singkat | Default | Fungsi |
|------|---------|---------|--------|
| `--delimiter <str>` | `-d` | auto-detect | Paksa delimiter tertentu, misal `;` atau `\t`. |
| `--columns <str>` | `-c` | (semua) | Filter kolom, dipisah koma. Contoh: `-c "id,value"`. |
| `--row-start <int>` | — | 0 | Baris awal (0-indexed, inclusive). |
| `--row-end <int>` | — | (akhir) | Baris akhir (exclusive). `--row-start 0 --row-end 100` = baris 0–99. |
| `--progress` | `-p` | off | Progress bar saat membaca file besar. |
| `--k <float>` | — | 1.5 | Pengali IQR untuk outlier. Naikkan = lebih toleran, turunkan = lebih ketat. |

### Opsi khusus `analyzer load`

| Opsi | Default | Fungsi |
|------|---------|--------|
| `--show-outlier-rows <int>` | 0 | Tampilkan N baris outlier pertama per kolom beserta posisi barisnya. |
| `--flat-min-run <int>` | 20 | Minimal baris beruntun bernilai sama untuk dianggap flat-line. |
| `--no-flatline` | off | Matikan deteksi flat-line. |

### Opsi khusus `analyzer plot`

| Opsi | Default | Fungsi |
|------|---------|--------|
| `--out-dir <path>` / `-o` | `charts` | Folder tujuan PNG. |
| `--time-col <str>` | auto-detect | Kolom timestamp untuk sumbu-x line chart. |

### Opsi khusus `analyzer report`

| Opsi | Default | Fungsi |
|------|---------|--------|
| `--output <path>` / `-o` | `report.html` | File output. Ekstensi `.html` / `.md` menentukan format. |
| `--no-charts` | off | Laporan tanpa chart (lebih cepat). |

---

## 📂 Contoh Dataset

Folder `tests/fixtures/` berisi dataset untuk mencoba semua fitur:

```bash
# Data bersih
analyzer load tests/fixtures/clean.csv

# Data kotor (banyak missing value, tanggal rusak)
analyzer load tests/fixtures/dirty.csv

# Data dengan outlier jelas (100.0 dan 150.0) + sensor stuck
analyzer load tests/fixtures/outliers.csv --show-outlier-rows 5

# Data besar (15.000 baris) — coba dengan progress bar
analyzer load tests/fixtures/big.csv -p

# Format non-koma: TSV, semicolon, pipe
analyzer load tests/fixtures/sample.tsv
analyzer load tests/fixtures/semicolon.csv
analyzer load tests/fixtures/pipe.csv

# Laporan lengkap dari data outlier
analyzer report tests/fixtures/outliers.csv -o contoh_report.html
```

---

## 🔧 Troubleshooting

| Masalah | Penyebab & Solusi |
|---------|-------------------|
| `'analyzer' is not recognized` | Virtual environment belum aktif, atau install ulang dengan `pip install -e .`. Alternatif: `python -m analyzer.cli ...`. |
| `Delimiter file ... tidak bisa dideteksi` | Delimiter file tidak standar. Tentukan manual: `analyzer load file.txt -d "\|"` (atau delimiter lain). |
| `File '...' kosong / tidak punya data` | File benar-benar kosong atau hanya berisi spasi/baris baru. |
| `File '...' cuma berisi header` | Tidak ada baris data di bawah header. Cek isi file. |
| `File '...' bukan teks UTF-8 yang valid` | File dengan encoding lain. Konversi dulu: buka di editor, save as UTF-8. |
| `Kolom tidak ditemukan: xxx` | Nama kolom di `-c` salah/ketuk. Cek nama persisnya di output `Structure & Completeness`. |
| `Rentang baris [X:Y] menghasilkan 0 baris` | `--row-start` ≥ jumlah baris file. Turunkan nilai. |
| Semua kolom terdeteksi satu kolom | Delimiter salah terdeteksi (misal file semicolon dibaca sebagai koma). Paksa dengan `-d ";"`. |
| `Permission denied` saat menulis chart/laporan | Folder output tidak bisa ditulis. Gunakan path lain atau jalankan dari folder yang benar. |

---

## 🧪 Testing

Jalankan seluruh test suite (41 test):

```bash
# Pastikan virtual environment aktif
pip install pytest
pytest tests/ -v
```

Struktur test: `test_loader.py` (parsing & delimiter), `test_stats.py` (statistik), `test_outliers.py` (outlier & flat-line), `test_plots.py` (chart), `test_report.py` (laporan), `test_polish.py` (filter, progress, dataset).

---

## 🗂️ Struktur Project

```
analyzer-data/
├── analyzer/               # Package utama
│   ├── __init__.py         # Versi package
│   ├── cli.py              # Entry point: daftar semua command
│   ├── commands.py         # Implementasi load / plot / report
│   ├── loader.py           # Pembacaan CSV/TSV + delimiter sniffing + filter
│   ├── stats.py            # Kalkulasi statistik (numerik, kategori, timestamp)
│   ├── outliers.py         # Deteksi outlier IQR + flat-line
│   ├── plots.py            # Generator chart PNG (matplotlib)
│   └── report.py           # Generator laporan HTML/Markdown
├── tests/
│   ├── fixtures/           # Dataset uji (clean, dirty, big, outliers, dll)
│   ├── test_loader.py      # Test pembacaan file
│   ├── test_stats.py       # Test statistik
│   ├── test_outliers.py    # Test outlier & flat-line
│   ├── test_plots.py       # Test chart
│   ├── test_report.py      # Test laporan
│   └── test_polish.py      # Test filter/progress/dataset
├── docs/                   # todo.md, progress.md, architecture.md
├── pyproject.toml          # Metadata & dependency package
├── requirements.txt        # Dependency alternatif
└── README.md               # Dokumen ini
```

---

## 📄 Lisensi

Didistribusikan di bawah [MIT License](LICENSE).
