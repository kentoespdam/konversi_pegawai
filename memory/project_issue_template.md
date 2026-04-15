---
name: Issue Document Template & Convention
description: Template penulisan issue plan dalam Bahasa Indonesia untuk junior dev / AI model, format standar v2_5+
type: reference
---

## Lokasi File
`issues/v2_N_<source>_to_<target>_plan.md`

## Template Standar (v2_5+ format)

```markdown
# Plan Audit, Perbaikan, dan Optimasi: `v2_N_<source>_to_<target>.py`

Dokumen ini disusun sebagai panduan bagi Junior Developer atau AI Model untuk
memperbaiki dan mengoptimalkan script migrasi `v2_N_<source>_to_<target>.py`
beserta pustaka pendukungnya (`core/smartoffice/<source>.py` dan
`core/kepegawaian/kepeg_<target>.py`).

Sesuai dengan pedoman pengerjaan, **Wajib menggunakan Context 7** saat
mengimplementasikan langkah-langkah di bawah ini. Hal tersebut untuk memastikan
_best practice_ penulisan kode Python, penanganan exception, standar pemrosesan
Pandas, dan query SQL. Selalu jalankan environment menggunakan Python dari
dalam `.venv`.

## 1. Identifikasi Bug & Potensi Masalah

Berdasarkan penelusuran kode, ditemukan beberapa kelemahan pada skrip saat ini:

- **[Judul Bug Bold]**: [Deskripsi masalah, dampak, konteks teknis]
- **[Judul Bug Bold]**: [...]
[... urutkan dari severity tertinggi]

## 2. Rekomendasi Perbaikan (Bug Fixes)

Berikut adalah tahap mitigasi teknis untuk kendala di atas:

1. **[Judul Fix]**: [Instruksi perbaikan spesifik tanpa source code]
2. **[...]**: [...]

## 3. Rekomendasi Optimasi Performa & Kerapian Kode

1. **[Judul Optimasi]**: [Deskripsi]
[... biasanya 3-4 poin]

## 4. Langkah-Langkah Pengerjaan

Dokumen ini disusun sebagai instrumen _checklist_. Pedomani runtutan step
teknis berikut saat proses _fixing_ modul migrasi versi N:

- [ ] **Aktivasi Environment & Referensi**: Posisikan di direktori _root_
  proyek dan login ke dalam virtual environment via `source .venv/bin/activate`.
  Selalu panggil rujukan berbasis **Context 7**...
- [ ] **Perbaikan Query Fetch Sumber (`core/smartoffice/<source>.py`)**: [...]
- [ ] **Perbaikan Fungsi Save Target (`core/kepegawaian/kepeg_<target>.py`)**: [...]
- [ ] **Pengaman Penanganan Data (`v2/v2_N_<source>_to_<target>.py`)**: [...]
- [ ] **Testing dan Assessment Terminal**: Uji finalisasi script menekan
  baris eksekusi `python -m v2.v2_N_<source>_to_<target>`. Pantau kemunculan
  log durasi waktu migrasi dan jumlah record...
```

## Konvensi Gaya Penulisan

| Aspek | Aturan |
|-------|--------|
| **Bahasa** | Indonesia formal/teknis |
| **Audience** | Junior developer atau AI model kecil |
| **Level detail** | High-level tanpa source code, tapi spesifik |
| **Bold** | Judul bug, istilah kritis: `**Context 7**`, `**WAJIB**` |
| **Italic** | Istilah teknis asing: _early exit_, _try-except_, _checklist_ |
| **Code backtick** | Nama fungsi, kolom, tabel: `` `cleanup()` ``, `` `biodata_id` `` |
| **Urutan bug** | Severity tertinggi di atas (SQL error > data loss > missing feature) |
| **Checklist** | `- [ ] **Section**: Deskripsi` |
| **Context 7** | Wajib disebut di pembuka dan di checklist langkah pertama |
| **Testing** | Selalu item terakhir di checklist |

## Frasa Kunci Berulang

- "tidak ada pengecekan atau mekanisme _early exit_"
- "Konversi Tipe Data Pandas NULL (`NaN`/`NaT`)"
- "Nilai _Hardcoded_ untuk Flag"
- "Minimnya Log Pengaman (Error Handling)"
- "Anomali pada Query `ON DUPLICATE KEY UPDATE`"
- "Enkapsulasi Galat Global"
- "Sanitasi Ketersediaan DataFrame"
- "Logika Dinamis Pengisian Flag Persetujuan"
- "Pemurnian Transformasi _Clean-Up_"
- "Standardisasi Modul Import"

## Langkah Membuat Issue Baru (untuk AI)

1. Baca memory `project_migration_index.md` → cari entry script yang dituju
2. Baca memory `project_bug_patterns.md` → gunakan checklist audit
3. **Akses database** jika perlu: `DESCRIBE <target_table>`, sample data source
4. Baca source code 3 file: `v2/v2_N_*.py`, `core/smartoffice/*.py`, `core/kepegawaian/kepeg_*.py`
5. Bandingkan kolom fetch vs INSERT vs target schema → identifikasi mismatch
6. Tulis issue menggunakan template di atas
7. Gunakan Context 7 untuk referensi best practice jika diperlukan
