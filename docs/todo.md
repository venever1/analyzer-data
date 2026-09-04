# Project: Data Analyzer CLI (General Purpose)

## 🎯 Tujuan
CLI tool yang bisa baca file CSV/log, otomatis kasih ringkasan statistik, deteksi outlier/anomali, dan generate visualisasi (chart) tanpa perlu buka Excel/Python manual.

Sifatnya general purpose dulu — nanti bisa di-extend buat kasus spesifik (IoT sensor, sinyal, ML EDA, PLC log, dll).

---

## 🧱 Tech Stack (usulan)
- **Bahasa**: Python (paling gampang buat data + banyak library siap pakai)
- **CLI framework**: `Typer` atau `argparse`
- **Data handling**: `pandas`
- **Visualisasi**: `matplotlib` / `plotly` (plotly kalau mau output HTML interaktif)
- **Output laporan**: Markdown atau HTML

---

## ✅ TODO / Tahapan Development

### Fase 1 — Setup & Skeleton
- [x] Inisialisasi project (folder structure, virtualenv, requirements.txt)
- [x] Setup CLI entrypoint dasar (`analyzer --help` jalan)
- [x] Buat command dasar: `analyzer load <file.csv>` — baca file, print jumlah baris/kolom

### Fase 2 — Core: Baca & Validasi Data
- [x] Support baca CSV (dan opsional: TSV, log file dengan delimiter custom via `csv.Sniffer` 64KB multi-row sample + C engine)
- [x] Auto-detect tipe kolom (numerik, tanggal, kategori, teks)
- [x] Handle missing value / data kosong (kasih laporan berapa % kosong per kolom)
- [x] Validasi dasar (kolom kosong semua, file corrupt, dsb) + error message yang jelas

### Fase 3 — Ringkasan Statistik
- [x] Hitung statistik dasar per kolom numerik: mean, median, min, max, std dev
- [x] Hitung distribusi kolom kategori (value counts)
- [x] Deteksi rentang waktu kalau ada kolom timestamp (dari kapan sampai kapan)
- [x] Print ringkasan ke terminal dalam format rapi (tabel Rich)

### Fase 4 — Deteksi Anomali/Outlier
- [x] Implementasi deteksi outlier sederhana (IQR method, default k=1.5, opsi `--k`)
- [x] Tandai baris-baris yang keluar dari rentang normal (opsi `--show-outlier-rows N`)
- [x] Deteksi "flat line" / sensor stuck (default min run 20 baris, opsi `--flat-min-run` / `--no-flatline`)

### Fase 5 — Visualisasi
- [x] Generate line chart untuk kolom numerik terhadap waktu/index
- [x] Generate histogram/distribusi untuk kolom numerik
- [x] Highlight titik outlier di chart (warna beda, merah)
- [x] Export chart ke file PNG (matplotlib, backend Agg headless)

### Fase 6 — Laporan Otomatis
- [x] Generate laporan (Markdown & HTML): statistik + insight + chart
- [x] Command: `analyzer report <file.csv> --output report.html` (atau `.md`; ekstensi menentukan format)

### Fase 7 — Polish & UX
- [x] Progress indicator buat file besar (`--progress` / `-p` via Rich chunked reader)
- [x] Opsi filter (kolom `-c`, rentang baris `--row-start`/`--row-end`) di `load`, `plot`, dan `report`
- [x] Dokumentasi cara pakai (README.md)
- [x] Testing dengan beberapa contoh dataset (`clean.csv`, `dirty.csv`, `big.csv` 15.000 baris)

### Fase 8 (opsional, next step) — Extensibility
- [ ] Buat struktur plugin/module biar gampang nambahin analisis khusus domain (misal FFT buat sinyal, threshold alert buat IoT)
- [ ] Config file (YAML/JSON) buat custom rule anomali sesuai domain

---

## 📝 Cara Pakai Todo Ini di OpenCode
1. Copy isi file ini ke root project sebagai `todo.md`
2. Prompt ke agent: *"Baca todo.md ini, kerjakan Fase 1 dulu, checklist yang sudah selesai"*
3. Lanjut fase per fase — jangan minta semua sekaligus biar hasilnya lebih terkontrol dan gampang direview
4. Setelah tiap fase selesai, coba jalanin manual dulu sebelum lanjut ke fase berikutnya
