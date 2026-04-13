# Issue #002: Bug Fix & Optimasi — `core/config.py`

**Prioritas:** Medium-High  
**Modul:** `core/config.py`  
**Tipe:** Bug Fix & Optimasi  
**Tanggal:** 2026-04-13

---

## Latar Belakang

File `core/config.py` adalah modul inti yang menangani seluruh koneksi database dalam project ini. Modul ini menyediakan connection pool, fungsi fetch data (SELECT), dan fungsi save/update (INSERT/UPDATE) untuk dua database: **smartoffice** (sumber) dan **kepegawaian** (target).

Karena seluruh operasi database di project melewati modul ini (digunakan oleh **57 file**), bug atau inefisiensi di sini berdampak luas ke seluruh proses migrasi data.

Setelah dilakukan review, ditemukan **6 bug** dan **5 rekomendasi optimasi**.

---

## Daftar Bug yang Ditemukan

### Bug 1: Connection Pool Dibuat Ulang Setiap Pemanggilan (Critical)

**Masalah:** Fungsi `get_smartoffice_connection_pool()` dan `get_kepegawaian_connection_pool()` membuat objek `ConnectionPool` baru setiap kali dipanggil, mengambil satu koneksi, lalu pool-nya dibuang. Ini mengalahkan tujuan connection pooling — seharusnya pool dibuat sekali dan dipakai berulang.

**Dampak:** Overhead pembuatan pool berulang kali, koneksi database tidak di-reuse, bisa menyebabkan "too many connections" error pada MySQL terutama saat batch processing besar.

**Rekomendasi:** Gunakan pola singleton atau module-level variable agar pool dibuat sekali saat modul pertama kali di-import, lalu koneksi diambil dari pool yang sama.

**Referensi:** Gunakan Context7 untuk mencari best practice `pymysqlpool` connection pool singleton pattern.

---

### Bug 2: Tidak Ada Validasi Environment Variable

**Masalah:** Konfigurasi database langsung membaca environment variable tanpa validasi. Contohnya, konversi `DB_PORT` ke integer akan langsung crash dengan `TypeError` jika variabel tidak di-set di file `.env`.

**Dampak:** Program crash dengan error yang tidak informatif saat environment variable tidak lengkap. Developer baru akan kesulitan men-debug masalah ini.

**Rekomendasi:** Tambahkan validasi di awal modul yang mengecek keberadaan semua environment variable yang diperlukan. Berikan pesan error yang jelas jika ada yang kosong. Berikan nilai default untuk variabel yang memungkinkan (misalnya port default 3306).

**Referensi:** Gunakan Context7 untuk mencari best practice `python-dotenv` environment variable validation.

---

### Bug 3: Error Handling Terlalu Generik dan Menelan Error

**Masalah:** Fungsi `_do_save_update` menangkap semua `Exception` secara generik, hanya mencatat log, lalu melakukan rollback. Fungsi ini **tidak** melempar ulang (re-raise) error ke pemanggil. Akibatnya, kode yang memanggil fungsi ini tidak pernah tahu bahwa operasi database gagal.

**Dampak:** Proses migrasi bisa melanjutkan eksekusi meskipun ada data yang gagal disimpan, menyebabkan data tidak konsisten antara sumber dan target tanpa ada peringatan yang jelas.

**Rekomendasi:** Setelah logging dan rollback, lempar ulang exception agar pemanggil bisa menangani kegagalan secara tepat. Atau minimal, kembalikan status berhasil/gagal dari fungsi ini.

**Referensi:** Gunakan Context7 untuk mencari best practice Python error handling pattern pada database operations.

---

### Bug 4: FOREIGN_KEY_CHECKS Tidak Di-restore Saat Error

**Masalah:** Di fungsi `_do_save_update`, perintah `SET FOREIGN_KEY_CHECKS=0` dijalankan di awal, tapi `SET FOREIGN_KEY_CHECKS=1` hanya dijalankan setelah commit berhasil. Jika terjadi error dan masuk ke blok `except`, foreign key checks **tidak pernah di-aktifkan kembali** untuk koneksi tersebut.

**Dampak:** Jika koneksi di-reuse (setelah pool diperbaiki), operasi selanjutnya akan berjalan tanpa validasi foreign key, memungkinkan data inkonsisten masuk ke database.

**Rekomendasi:** Gunakan blok `finally` untuk memastikan `SET FOREIGN_KEY_CHECKS=1` selalu dijalankan, baik saat berhasil maupun saat error.

**Referensi:** Gunakan Context7 untuk mencari best practice penggunaan `try/except/finally` pada operasi MySQL yang menonaktifkan foreign key checks.

---

### Bug 5: Pengecekan None Tidak Pythonic

**Masalah:** Fungsi `_get_fetch_result` menggunakan `if not where is None` untuk mengecek apakah parameter `where` memiliki nilai. Penulisan ini secara logika benar tapi tidak mengikuti konvensi Python dan bisa membingungkan developer lain.

**Dampak:** Risiko rendah secara fungsional, tapi menurunkan kualitas kode dan bisa menyebabkan kesalahpahaman saat maintenance.

**Rekomendasi:** Ubah menjadi `if where is not None` yang merupakan cara penulisan standar Python (sesuai PEP 8).

**Referensi:** Cek PEP 8 style guide untuk perbandingan dengan `None`.

---

### Bug 6: Maxsize Pool Kepegawaian Terlalu Besar

**Masalah:** Pool koneksi kepegawaian dikonfigurasi dengan `maxsize=1000`. Angka ini sangat besar dan berpotensi membanjiri MySQL server, terutama jika server digunakan bersama oleh aplikasi lain.

**Dampak:** Bisa menyebabkan MySQL kehabisan koneksi dan mengganggu layanan lain yang menggunakan server database yang sama.

**Rekomendasi:** Turunkan maxsize ke nilai yang wajar (misalnya 20-50). Sesuaikan dengan konfigurasi `max_connections` di MySQL server. Sebagai panduan, maxsize pool sebaiknya tidak lebih dari 10-20% dari total `max_connections` MySQL.

**Referensi:** Gunakan Context7 untuk mencari best practice konfigurasi `pymysqlpool` pool size dan hubungannya dengan MySQL `max_connections`.

---

## Rekomendasi Optimasi

### Optimasi 1: Singleton Pattern untuk Connection Pool

**Kondisi Saat Ini:** Setiap pemanggilan fungsi membuat pool baru.

**Rekomendasi:** Buat pool sebagai module-level singleton yang hanya diinisialisasi sekali. Sediakan fungsi `get_connection()` yang mengambil koneksi dari pool yang sudah ada.

**Langkah:**
1. Buat variabel module-level `_smartoffice_pool` dan `_kepegawaian_pool` yang diinisialisasi `None`.
2. Pada pemanggilan pertama, buat pool dan simpan di variabel tersebut.
3. Pemanggilan berikutnya langsung menggunakan pool yang sudah ada.

**Referensi:** Gunakan Context7 untuk mencari pattern singleton connection pool di Python.

---

### Optimasi 2: Tambahkan Retry Mechanism

**Kondisi Saat Ini:** Jika koneksi database gagal, operasi langsung error tanpa percobaan ulang.

**Rekomendasi:** Tambahkan mekanisme retry sederhana (misalnya 3 kali percobaan dengan jeda) untuk operasi database. Ini meningkatkan ketahanan terhadap gangguan jaringan sesaat.

**Referensi:** Gunakan Context7 untuk mencari library `tenacity` retry pattern untuk database operations di Python.

---

### Optimasi 3: Buat File `.env.example`

**Kondisi Saat Ini:** Tidak ada dokumentasi variabel environment yang diperlukan. File `.env` yang berisi kredensial asli kemungkinan ikut ter-commit.

**Rekomendasi:**
1. Buat file `.env.example` berisi daftar variabel tanpa nilai sensitif.
2. Pastikan `.env` ada di `.gitignore`.
3. Tambahkan komentar penjelasan untuk setiap variabel.

---

### Optimasi 4: Konsistensi Logging

**Kondisi Saat Ini:** Beberapa modul menggunakan `LOGGER`, sebagian lain menggunakan `ic()` (icecream), dan ada yang tidak punya logging sama sekali.

**Rekomendasi:** Standarisasi penggunaan `LOGGER` dari `core/config.py` di seluruh modul. Ubah level logging dari hardcoded `DEBUG` ke pembacaan dari environment variable agar bisa diatur per environment (development/production).

**Referensi:** Gunakan Context7 untuk mencari best practice Python logging configuration.

---

### Optimasi 5: Pisahkan Konfigurasi dari Logic

**Kondisi Saat Ini:** File `config.py` menggabungkan konfigurasi database, pembuatan pool, dan fungsi-fungsi utility database dalam satu file.

**Rekomendasi:** Pertimbangkan untuk memisahkan:
- Konfigurasi dan validasi environment variable (config)
- Manajemen connection pool (pool)
- Fungsi-fungsi utility fetch/save (database operations)

Ini memudahkan testing dan maintenance.

---

## Langkah Pengerjaan

Berikut langkah-langkah pengerjaan yang harus diikuti secara berurutan:

### Tahap 1: Persiapan & Riset

1. **Baca dan pahami** file `core/config.py` secara menyeluruh.
2. **Gunakan Context7** untuk riset best practice:
   - Jalankan: `npx ctx7@latest library pymysqlpool "connection pool singleton pattern"`
   - Jalankan: `npx ctx7@latest library python-dotenv "environment variable validation"`
   - Jalankan: `npx ctx7@latest library pymysql "error handling best practice"`
3. **Identifikasi** semua file yang mengimport dari `core/config.py` agar tahu dampak perubahan.

### Tahap 2: Perbaikan Bug (Prioritas Tinggi)

4. **Perbaiki Bug 1** — Ubah pembuatan connection pool menjadi singleton.
5. **Perbaiki Bug 4** — Tambahkan `finally` block untuk restore `FOREIGN_KEY_CHECKS`.
6. **Perbaiki Bug 3** — Tambahkan re-raise exception setelah rollback di `_do_save_update`.
7. **Perbaiki Bug 2** — Tambahkan validasi environment variable di awal modul.

### Tahap 3: Perbaikan Bug (Prioritas Rendah)

8. **Perbaiki Bug 5** — Ubah `not where is None` menjadi `where is not None`.
9. **Perbaiki Bug 6** — Turunkan `maxsize` pool kepegawaian ke nilai wajar.

### Tahap 4: Optimasi

10. **Implementasi Optimasi 2** — Tambahkan retry mechanism jika disetujui.
11. **Implementasi Optimasi 3** — Buat file `.env.example`.
12. **Implementasi Optimasi 4** — Standarisasi logging (ubah level dari hardcoded ke env var).

### Tahap 5: Testing & Verifikasi

13. **Jalankan test yang ada:** `python -m pytest tests/`
14. **Test manual:** Jalankan salah satu migration step (misalnya `python -m v2.v2_1_emp_profile_to_biodata`) dan pastikan berjalan normal.
15. **Verifikasi** tidak ada regression pada modul lain yang menggunakan `config.py`.

### Tahap 6: Review & Dokumentasi

16. **Jalankan** `/simplify` atau review mandiri untuk memastikan kualitas kode.
17. **Commit** perubahan dengan pesan yang jelas per bug/optimasi.

---

## Catatan untuk Developer

- **Jangan ubah interface/signature fungsi** yang sudah ada kecuali benar-benar diperlukan, karena 57 file bergantung pada modul ini.
- **Selalu gunakan Context7** (`npx ctx7@latest`) untuk mendapatkan referensi terbaru sebelum implementasi.
- **Test setiap perubahan** secara incremental, jangan batch semua perubahan sekaligus.
- Jika ragu, tanyakan sebelum mengubah — lebih baik bertanya daripada memperkenalkan bug baru.
