# Issue Plan: Audit & Refactor `v2_9_2_emp_sk_to_riwayat_sk.py`

**Tanggal dibuat:** 2026-04-14  
**Script target:** `v2/v2_9_2_emp_sk_to_riwayat_sk.py`  
**Core files terkait:**  
- `core/smartoffice/emp_sk.py` → `fetch_emp_sk_for_riwayat_sk()`, `update_init_smartoffice_no_sk()`  
- `core/kepegawaian/kepeg_riwayat_sk.py` → `save_riwayat_sk_from_emp_sk()`  

---

## Konteks & Tujuan

Script ini bertugas memindahkan data Surat Keputusan (SK) pegawai dari tabel source `emp_sk` (SmartOffice) ke tabel target `riwayat_sk` (kepegawaian_migrasi). Script saat ini belum memiliki error handling, logging, maupun validasi data yang memadai. Tujuan audit ini adalah memastikan integritas data, idempotency, dan ketahanan script sebelum digunakan di produksi.

---

## Informasi Database (Tidak Perlu Fetch Ulang)

### Source: Tabel `emp_sk` (SmartOffice)

| Kolom | Tipe | Catatan |
|-------|------|---------|
| id | int unsigned | PK auto_increment |
| emp_id | int | FK ke employee |
| no_sk | varchar(64) | Bisa NULL / kosong / "-" |
| jenis_sk | int | Nilai 1–9 (lihat distribusi) |
| tgl_sk | date | Tanggal SK |
| tmt_sk | date | TMT berlaku SK |
| golongan_id | int | Sering NULL — 5.749 dari 7.780 record NULL/0 |
| gaji_pokok | int | Bisa NULL atau 0 |
| mkg_tahun, mkg_bulan | int | Bisa NULL atau 0 |
| kenaikan_berikutnya | date | Bisa NULL |
| mkgb_tahun, mkgb_bulan | int | Bisa NULL atau 0 |
| flag_update_master | int | Digunakan sebagai boolean `update_master` |
| keterangan | text | Catatan bebas |
| status | int | `3` = is_deleted |

**Distribusi `jenis_sk`:**

| jenis_sk | Jumlah |
|----------|--------|
| 1 | 1.381 |
| 2 | 297 |
| 3 | 332 |
| 4 | 625 |
| 5 | 1.260 |
| 6 | 2 |
| 7 | 636 |
| 8 | 1.528 |
| 9 | 1.719 |

**Statistik kualitas data:**
- Total record: **7.780**
- `no_sk` kosong/NULL: **7**
- `golongan_id` NULL atau 0: **5.749** (73,9% — mayoritas!)
- `is_deleted` (`status=3`): **86**

**Contoh data source:**
```
id=1 | emp_id=245 | no_sk="SK.0TEST0/2017" | jenis_sk=1 | tgl_sk=2017-12-17 | tmt_sk=2017-11-01 | golongan_id=None | gaji_pokok=None | status=1
id=2 | emp_id=269 | no_sk="TEST"          | jenis_sk=1 | tgl_sk=2017-12-19 | tmt_sk=2018-01-01 | golongan_id=None | gaji_pokok=None | status=3
id=3 | emp_id=1   | no_sk="813.1/982/..."  | jenis_sk=4 | tgl_sk=1984-05-01 | tmt_sk=1984-05-01 | golongan_id=None | gaji_pokok=None | status=3
```

### Target: Tabel `riwayat_sk` (kepegawaian_migrasi)

| Kolom | Tipe | Null | Key | Default |
|-------|------|------|-----|---------|
| id | bigint(20) | NO | PRI | auto_increment |
| created_at | timestamp | YES | | current_timestamp() |
| created_by | varchar(255) | YES | | NULL |
| is_deleted | tinyint(1) | YES | MUL | 0 |
| updated_at | timestamp | YES | | current_timestamp() ON UPDATE |
| updated_by | varchar(255) | YES | | NULL |
| gaji_pokok | double | YES | | NULL |
| jenis_sk | tinyint(4) | YES | | NULL |
| kenaikan_berikutnya | date | YES | | NULL |
| mkg_bulan | int(11) | YES | | NULL |
| mkg_tahun | int(11) | YES | MUL | NULL |
| mkgb_bulan | int(11) | YES | | NULL |
| mkgb_tahun | int(11) | YES | MUL | NULL |
| nama | varchar(255) | YES | MUL | NULL |
| nipam | varchar(255) | YES | MUL | NULL |
| nomor_sk | varchar(255) | YES | MUL | NULL |
| notes | text | YES | | NULL |
| tanggal_sk | date | YES | MUL | NULL |
| tmt_berlaku | date | YES | | NULL |
| update_master | bit(1) | YES | | NULL |
| golongan_id | bigint(20) | YES | MUL | NULL |
| pegawai_id | bigint(20) | YES | MUL | NULL |

> ⚠️ **Tidak ada UNIQUE KEY** selain PRIMARY KEY. ON DUPLICATE KEY UPDATE tidak berfungsi.  
> ⚠️ **Tidak ada kolom `version`** — kolom ini ada di INSERT query sekarang (hardcoded `0`) → menyebabkan error SQL.

**Contoh data target (sudah ada dari migrasi sebelumnya):**
```
id=1 | nipam=811200424 | nomor_sk=TEST | jenis_sk=0 | gaji_pokok=0.0 | mkg_tahun=0 | update_master=b'\x00' | golongan_id=None | is_deleted=1
id=2 | nipam=641100143 | nomor_sk=813.1/982/V/1984 | jenis_sk=3 | gaji_pokok=0.0 | update_master=b'\x00'
```

---

## Bug yang Ditemukan & Rekomendasi

### Bug Kritis

#### BUG-1: Kolom `version` Tidak Ada di Tabel Target
- **Lokasi:** `core/kepegawaian/kepeg_riwayat_sk.py` → fungsi `save_riwayat_sk_from_emp_sk()`
- **Masalah:** Query INSERT menyertakan kolom `version` dan nilai hardcoded `0`, padahal kolom ini **tidak ada** di tabel `riwayat_sk` → menyebabkan SQL error pada saat migrasi.
- **Rekomendasi:** Hapus kolom `version` dari daftar INSERT dan tuple data.

#### BUG-2: Tidak Ada ON DUPLICATE KEY UPDATE → Duplikasi Data
- **Lokasi:** `core/kepegawaian/kepeg_riwayat_sk.py` → fungsi `save_riwayat_sk_from_emp_sk()`
- **Masalah:** Query hanya INSERT tanpa ON DUPLICATE KEY UPDATE. Karena tabel hanya punya PK auto_increment (tidak ada unique key lain), setiap eksekusi berulang akan menambahkan duplikat record.
- **Rekomendasi:** Implementasikan strategi idempotency. Pilihan:
  1. TRUNCATE tabel target sebelum INSERT (lebih simpel, aman jika tidak ada FK dependency)
  2. Koordinasi dengan DBA untuk menambahkan unique constraint (misalnya kombinasi `pegawai_id + nomor_sk + jenis_sk`)
  - Verifikasi terlebih dahulu apakah ada tabel lain yang merujuk ke `riwayat_sk` sebelum memilih strategi.

#### BUG-3: Tidak Ada Error Handling
- **Lokasi:** `v2/v2_9_2_emp_sk_to_riwayat_sk.py` → fungsi `main()`
- **Masalah:** Tidak ada try-except → jika terjadi error SQL atau koneksi terputus, script crash tanpa log yang informatif.
- **Rekomendasi:** Tambahkan try-except global di `main()` dengan `LOGGER.error(..., exc_info=True)`.

#### BUG-4: Tidak Ada Guard DataFrame Kosong
- **Lokasi:** `v2/v2_9_2_emp_sk_to_riwayat_sk.py` → fungsi `main()`
- **Masalah:** Jika `fetch_emp_sk_for_riwayat_sk()` mengembalikan DataFrame kosong, proses cleanup dan save akan tetap dieksekusi dan berpotensi error.
- **Rekomendasi:** Tambahkan pengecekan `if df.empty: return` setelah fetch, disertai log informatif.

#### BUG-5: NaN/NaT Tidak Disanitasi di `cleanup()`
- **Lokasi:** `v2/v2_9_2_emp_sk_to_riwayat_sk.py` → fungsi `cleanup()`
- **Masalah:** Setelah transformasi boolean, nilai `NaN` / `NaT` / `pd.NA` masih bisa ada di kolom numerik dan tanggal, lalu dikirim ke pymysql → menyebabkan error atau penyimpanan data tidak valid.
- **Rekomendasi:** Tambahkan `df.replace({np.nan: None, pd.NaT: None, pd.NA: None})` di akhir fungsi `cleanup()`, sebelum `return`.

### Bug/Peringatan Sedang

#### BUG-6: Nilai Integer 0 Tidak Bermakna di Kolom Numerik
- **Lokasi:** `core/kepegawaian/kepeg_riwayat_sk.py` → fungsi `save_riwayat_sk_from_emp_sk()`
- **Masalah:** Kolom seperti `gaji_pokok`, `mkg_tahun`, `mkg_bulan`, `mkgb_tahun`, `mkgb_bulan` di source bisa bernilai `0` hasil dari `IFNULL(..., 0)` di query. Nilai `0` tidak memiliki makna bisnis untuk data SK dan sebaiknya disimpan sebagai NULL.
- **Rekomendasi:** Di `cleanup()`, ganti nilai `0` ke `None` untuk kolom numerik tersebut menggunakan `.replace(0, None)`.

#### BUG-7: Tidak Ada Logging Jumlah Record
- **Lokasi:** `v2/v2_9_2_emp_sk_to_riwayat_sk.py` → fungsi `main()`
- **Masalah:** Tidak ada log berapa record yang di-fetch dan di-save, sehingga sulit memverfikasi hasil eksekusi.
- **Rekomendasi:** Tambahkan `LOGGER.info(f"Fetched {len(df)} records.")` setelah fetch dan `LOGGER.info(f"Successfully processed {len(df)} records.")` setelah save.

#### BUG-8: `jenis_sk` Di-offset dengan `-1` di Query Fetch
- **Lokasi:** `core/smartoffice/emp_sk.py` → fungsi `fetch_emp_sk_for_riwayat_sk()`
- **Masalah:** Query SELECT menggunakan `es.jenis_sk - 1 AS jenis_sk`. Ini menggeser nilai (misal: `jenis_sk=1` menjadi `0`). Verifikasi apakah offset ini memang disengaja sesuai mapping enum di sistem target, atau merupakan bug.
- **Rekomendasi:** Verifikasi dengan stakeholder/dokumentasi sistem target apakah mapping `jenis_sk` memang dimulai dari 0 (target) vs 1 (source). Dokumentasikan hasilnya.

---

## Langkah-langkah Pengerjaan

> Gunakan **Context7** untuk mendapatkan best practice Pandas, pymysql, dan pola ETL Python

### 1. Persiapan Lingkungan
- Gunakan Python dari `./.venv/bin/python`
- Pastikan koneksi database ke SmartOffice dan kepegawaian_migrasi berfungsi
- Buat branch baru sesuai branching strategy sebelum mengerjakan kode

### 2. Audit & Verifikasi Schema (Sudah Dilakukan — Lihat Bagian "Informasi Database")
- Konfirmasi tidak ada kolom `version` di `riwayat_sk` ✅
- Konfirmasi tidak ada unique key selain PK di `riwayat_sk` ✅
- Konfirmasi distribusi dan kualitas data `emp_sk` ✅

### 3. Perbaiki `core/kepegawaian/kepeg_riwayat_sk.py`
- [ ] Hapus kolom `version` dan nilai `0` dari INSERT query dan tuple data **(BUG-1)**
- [ ] Putuskan dan implementasikan strategi idempotency **(BUG-2)**:
  - Verifikasi tidak ada FK dependency ke `riwayat_sk` dari tabel lain
  - Jika aman → tambahkan TRUNCATE sebelum INSERT di fungsi `save_riwayat_sk_from_emp_sk()`
- [ ] Pastikan semua kolom di tuple data sudah sesuai urutan dengan kolom di INSERT query

### 4. Perbaiki `v2/v2_9_2_emp_sk_to_riwayat_sk.py`
- [ ] Import `LOGGER` dari `core.config` dan `numpy as np` **(untuk BUG-3, BUG-4, BUG-5)**
- [ ] Tambahkan try-except di fungsi `main()` **(BUG-3)**
- [ ] Tambahkan empty DataFrame guard setelah fetch **(BUG-4)**
- [ ] Tambahkan logging jumlah record setelah fetch dan setelah save **(BUG-7)**
- [ ] Di fungsi `cleanup()`, tambahkan NaN/NaT sanitization di akhir **(BUG-5)**
- [ ] Di fungsi `cleanup()`, ganti nilai `0` ke `None` untuk kolom numerik yang tidak bermakna **(BUG-6)**

### 5. Verifikasi `jenis_sk` Offset
- [ ] Konfirmasi apakah `jenis_sk - 1` di query fetch memang disengaja **(BUG-8)**
- [ ] Bandingkan contoh data source vs target untuk memastikan mapping benar
- [ ] Dokumentasikan hasil verifikasi di plan ini atau di komentar kode

### 6. Testing & Validasi
- [ ] Jalankan script dengan `./.venv/bin/python v2/v2_9_2_emp_sk_to_riwayat_sk.py`
- [ ] Verifikasi log output: jumlah record fetch = jumlah record yang ada di source
- [ ] Cek tabel `riwayat_sk` setelah eksekusi: `SELECT COUNT(*) FROM riwayat_sk`
- [ ] Cek tidak ada NULL pada kolom wajib (`pegawai_id`, `nomor_sk`, `jenis_sk`, `tanggal_sk`)
- [ ] Jalankan ulang script untuk memverifikasi idempotency (jumlah record tidak bertambah jika TRUNCATE digunakan)
- [ ] Bandingkan jumlah record di source dan target: `SELECT COUNT(*) FROM emp_sk` vs `SELECT COUNT(*) FROM riwayat_sk`

### 7. Review & Dokumentasi
- [ ] Review semua perubahan sebelum merge
- [ ] Update memory jika ada temuan penting tentang schema atau logika bisnis

---

## Referensi Pola Standar Proyek

Gunakan struktur berikut sebagai acuan (query Context7 untuk best practice tambahan):

- **Struktur `main()`**: Lihat `memory/project_bug_patterns.md` bagian "Struktur main() Teroptimasi"
- **Struktur `cleanup()`**: Lihat `memory/project_bug_patterns.md` bagian "Struktur cleanup() Teroptimasi"
- **Checklist audit**: Lihat `memory/project_bug_patterns.md` bagian "Checklist Audit Script Baru"
- **Schema referensi**: Lihat `memory/project_db_schema.md`
