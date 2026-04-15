# Plan Audit dan Optimasi: `v2_3_emp_card_to_kartu_identitas.py`

## Latar Belakang
Dokumen ini merupakan panduan pengerjaan untuk mengaudit, memperbaiki bug, dan mengoptimalkan performa pada skrip migrasi data `v2/v2_3_emp_card_to_kartu_identitas.py`. Panduan ini ditujukan bagi junior developer atau agen AI, dengan instruksi langkah-demi-langkah (high-level) tanpa memuat detail source code yang spesifik.

## Lingkungan Eksekusi (Environment)
- Selalu gunakan interpreter Python dari environment virtual proyek saat mengeksekusi atau menguji skrip (`.venv/bin/python`).

## Best Practices & Standardisasi
- **Gunakan Context 7**: Selalu rujuk dan manfaatkan extension/server `context7` (atau tools/server terkait) untuk mendapatkan *best practice* terbaru terkait pengelolaan data menggunakan Pandas (khususnya untuk proses mapping yang efisien dan vektorisasi).
- **Gunakan Seluruh Skill yang Ada**: Manfaatkan kapabilitas terminal/shell, pencarian kode, baca/tulis file untuk memastikan proses modifikasi, pembaruan data, hingga testing tereksekusi dengan baik.
- **Semua Perubahan Harus Diuji**: Konfirmasi setiap proses refactoring dengan menjalankan skrip dan memeriksa log performa serta integritas data (tidak ada data null yang bocor/tidak tertangani).

---

## Langkah-langkah Pengerjaan

### 1. Analisis Kinerja dan Pembersihan (Optimasi Data Mapping)
Terdapat masalah performa utama pada modul ini di mana pencarian *ID kartu identitas* (`jenis_kitas_id`) dilakukan secara iteratif pada DataFrame (`apply`), di dalam iterasinya juga memanggil query Pandas yang berat (`query("nama==@jenis_kitas")`).

**Tugas:**
- **Hindari Iterasi Baris-per-baris:** Hapus blok kode yang menggunakan pola `.apply(lambda ...)` untuk mapping data.
- **Gunakan Pendekatan Vektorisasi:** Ubah strategi pencarian dengan menggunakan dictionary mapping (mengubah DataFrame referensi `jenis_kartu_df` menjadi key-value dictionary terlebih dahulu) dan eksekusi instruksi Pandas bawaan seperti `.map()` atau gunakan proses `.merge()`. Hal ini akan mempercepat performa skrip dari O(N*M) menjadi O(N).
- **Nilai Fallback:** Pastikan bahwa hasil mapping yang tidak memiliki pasangan (kosong atau null) diisi (*fallback*) ke default value (contoh: ID `0`), dan kolom *foreign key* tersebut dikonversi kembali ke tipe data bawaannya, yakni integer standar (bukan float atau object).

### 2. Validasi Tipe Data dan Struktur (Bug Fixing)
Terdapat bagian validasi data yang kurang ketat dan rentan memunculkan *unexpected return* saat menangani DataFrame berekspektasi tertentu.

**Tugas:**
- **Penanganan Null / Empty Type:** Periksa kembali pola evaluasi nilai string kosong. Evaluasi `None` atau string kosong (`""`) lebih disarankan menggunakan kapabilitas Pandas (`pd.isna()` atau `.fillna()`) dibandingkan mengevaluasi per satu *entry* secara langsung dengan ekspresi standar Python.
- **Tipe Data `is_deleted`:** Hati-hati dengan konversi `df["is_deleted"].eq(1)`. Proses ini mengubah data menjadi array Boolean `True/False`. Apabila skema tabel database selanjutnya mengharapkan nilai numerik (`1` atau `0` / TINYINT), ada kemungkinan akan terjadi *type error* atau penolakan oleh driver SQL. Coba periksa apakah diperlukan `.astype(int)` untuk mempertahankan struktur integer.

### 3. Implementasi Skema Error Handling
Proses saat ini mencatat durasi menggunakan `log_duration()`, namun tidak memiliki mitigasi kegagalan proses.

**Tugas:**
- **Tambahkan Try-Except:** Bungkus pemanggilan fungsi ekstraksi `fetch_emp_card_for_kartu_identitas()`, transformasi `cleanup()`, hingga penyimpanan sinkronisasi `save_kartu_identitas_from_emp_card()` ke dalam blok *try-except*.
- **Logging Exception:** Apabila terjadi galat, gunakan modul logging standar untuk mencatat Exception secara spesifik beserta pesannya tanpa memutus eksekusi bila sedang memproses sistem queueing.

### 4. Review Akhir dan Uji Coba Kinerja
**Tugas:**
- Cek dan sesuaikan kembali unit test apabila file tes untuk fungsi ini tersedia.
- Jalankan ulang berkas konversi: `.venv/bin/python -m v2.v2_3_emp_card_to_kartu_identitas` (atau skrip padanannya).
- Periksa konsol logging: Catat durasinya, seharusnya langkah optimasi vektorisasi di tahap (1) akan mendatangkan lonjakan kecepatan yang signifikan pada pemrosesan Pandas DataFrame.
