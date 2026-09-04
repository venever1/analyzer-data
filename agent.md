# AGENT.md — Rules untuk AI Coding Agent

Dokumen ini adalah aturan wajib untuk AI agent (Claude Code, OpenCode, Cursor, dll) yang mengerjakan project **Data Analyzer CLI**. Tujuannya: mencegah halusinasi, menjaga konsistensi kode, dan memastikan progress bisa dilacak dengan akurat.

---

## 1. Prinsip Utama

1. **Jangan pernah mengklaim sesuatu selesai tanpa menjalankannya.** Setiap task yang ditandai selesai di `progress.md` HARUS sudah dijalankan dan diverifikasi bekerja (bukan cuma "kelihatannya benar" dari membaca kode).
2. **Jangan asumsikan struktur file/folder yang belum dibuat.** Selalu cek isi direktori aktual (`ls`, `find`, atau tool file-listing) sebelum mengedit atau mereferensikan sebuah file.
3. **Jangan mengarang nama library, fungsi, atau parameter.** Kalau tidak yakin API dari `pandas`, `matplotlib`, `plotly`, atau `typer`, cek dokumentasi resmi atau source code library yang ter-install, jangan menebak dari ingatan.
4. **Jangan mengarang hasil analisis data.** Semua angka statistik, jumlah baris/kolom, atau contoh output yang dilaporkan ke user harus berasal dari eksekusi kode nyata terhadap dataset nyata — bukan dikira-kira.
5. **Satu fase, satu langkah.** Kerjakan **hanya fase yang diminta** sesuai urutan di `todo.md`. Jangan lompat fase atau mengerjakan beberapa fase sekaligus tanpa diminta eksplisit.

---

## 2. Alur Kerja Wajib per Task

Untuk setiap item checklist yang dikerjakan:

1. **Baca ulang** `todo.md` dan `progress.md` dulu sebelum mulai, supaya tahu state project saat ini.
2. **Implementasikan** perubahan seminimal mungkin untuk menyelesaikan satu item checklist.
3. **Jalankan** kode/testnya secara nyata (bukan hanya dibaca) untuk membuktikan itu bekerja.
4. **Tunjukkan bukti** ke user: output command, error jika ada, atau contoh hasil eksekusi.
5. **Update `progress.md`** — centang item yang selesai, catat tanggal, catat file yang diubah/dibuat, catat masalah/keterbatasan yang ditemukan.
6. **Berhenti** dan minta review/konfirmasi user sebelum lanjut ke item/fase berikutnya, kecuali diminta lanjut otomatis.

---

## 3. Larangan Keras (Anti-Halusinasi)

- ❌ Jangan menulis "berhasil diimplementasikan" tanpa menjalankan kodenya.
- ❌ Jangan menandai checklist selesai di `progress.md` kalau belum diuji.
- ❌ Jangan membuat file dummy/placeholder lalu melaporkannya sebagai fitur lengkap.
- ❌ Jangan mengarang nama command CLI yang belum benar-benar diimplementasi (misal menyebut `analyzer summary` di dokumentasi padahal command-nya belum dibuat).
- ❌ Jangan mengubah tech stack (Python, Typer/argparse, pandas, matplotlib/plotly) tanpa persetujuan eksplisit dari user.
- ❌ Jangan menghapus atau menulis ulang file besar tanpa alasan yang dijelaskan ke user terlebih dahulu.

---

## 4. Konvensi Kode

- **Bahasa**: Python 3.10+
- **Struktur CLI**: gunakan `Typer` sebagai default, kecuali user secara eksplisit minta `argparse`.
- **Import**: gunakan absolute import dari package `analyzer/`.
- **Error handling**: setiap fungsi yang baca file harus punya try/except dengan pesan error yang jelas ke user (bukan raw traceback tanpa konteks).
- **Testing**: setiap fitur baru di Fase 2 ke atas sebaiknya punya minimal 1 contoh dataset uji (bisa file CSV kecil di `tests/fixtures/`).
- **Docstring**: setiap fungsi publik wajib punya docstring singkat (apa input, apa output).

---

## 5. Sumber Kebenaran (Source of Truth)

Urutan prioritas dokumen kalau ada konflik informasi:

1. `todo.md` — rencana & tahapan fase (jangan diedit oleh agent kecuali diminta).
2. `progress.md` — status aktual project saat ini (WAJIB selalu up to date, ini yang paling sering berubah).
3. `architecture.md` — struktur project (update kalau struktur folder/module berubah).
4. `README.md` — dokumentasi user-facing (update kalau ada command/fitur baru yang sudah stabil).

Kalau `progress.md` bilang sesuatu belum selesai, JANGAN percaya asumsi lain — anggap belum selesai sampai diverifikasi ulang.

---

## 6. Kapan Harus Bertanya ke User (bukan menebak)

- Format output laporan (Markdown vs HTML) kalau belum ditentukan di task saat ini.
- Struktur kolom dataset kalau contoh CSV/log belum disediakan.
- Threshold deteksi outlier (Z-score vs IQR, dan nilai batasnya) sebelum Fase 4 dimulai.
- Nama command atau argumen CLI yang belum ada presedennya di `todo.md`.

Jangan menebak asumsi besar sendirian — lebih baik berhenti dan tanya daripada mengarang lalu membuat inkonsistensi di fase berikutnya.
