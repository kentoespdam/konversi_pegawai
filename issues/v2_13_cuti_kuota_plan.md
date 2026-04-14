# Plan: Audit & Optimasi `v2_13_cuti_kuota.py`

## Tujuan

Script ini memigrasikan data kuota cuti pegawai dari tabel `cuti_kuota` (database `smartoffice`) ke tabel `cuti_kuota` (database `kepegawaian_migrasi`).

Script saat ini sangat minimalis dan mengandung beberapa potensi bug yang perlu diperbaiki sebelum aman dijalankan di production.

---

## Referensi Database

### Tabel Sumber: `cuti_kuota` (smartoffice)

| Kolom | Tipe | Contoh |
|---|---|---|
| `ck_id` | int(11) unsigned PK | `1`, `2`, `3` |
| `emp_code` | varchar(32) | `'641100143'`, `'690700169'` |
| `ck_pyear` | int(4) | `2018`, `2019` |
| `ck_kuota` | int(11) | `12` |
| `ck_diambil` | int(11) | `0`, `3` |
| `ck_sisa` | int(11) | `12`, `9` |
| `ck_expired` | date | `2019-06-30` |

**Contoh data nyata (3 baris):**
```
ck_id=1 | emp_code=641100143 | ck_pyear=2018 | ck_kuota=12 | ck_diambil=0 | ck_sisa=12 | ck_expired=2019-06-30
ck_id=2 | emp_code=690700169 | ck_pyear=2018 | ck_kuota=12 | ck_diambil=3 | ck_sisa=9  | ck_expired=2019-06-30
ck_id=3 | emp_code=660600242 | ck_pyear=2018 | ck_kuota=12 | ck_diambil=0 | ck_sisa=12 | ck_expired=2019-06-30
```

> **Catatan:** Kolom `created_at`, `created_by`, `updated_at`, `updated_by` di source banyak bernilai `NULL`.

### Tabel Target: `cuti_kuota` (kepegawaian_migrasi)

| Kolom | Tipe | Keterangan |
|---|---|---|
| `id` | bigint(20) PK auto_increment | Di-insert dari `ck_id` source |
| `pegawai_id` | bigint(20) | FK → tabel `pegawai` |
| `tahun` | int(11) | Dari `ck_pyear` |
| `kuota` | int(11) | Dari `ck_kuota` |
| `kuota_terpakai` | int(11) | Dari `ck_diambil` |
| `kuota_tambahan` | int(11) | Hardcoded `0` (tidak ada di source) |
| `sisa_kuota` | int(11) | Dari `ck_sisa` |
| `expired` | date | Dari `ck_expired` |
| `is_deleted` | tinyint(1) | Default `0` |
| `created_by` | varchar(255) | Hardcoded `'SYSTEM'` |
| `created_at` | timestamp | Auto default |
| `updated_at` | timestamp | Auto on update |

> **PENTING — Idempotency Risk:** Hasil `SHOW INDEX FROM cuti_kuota WHERE Non_unique=0` menunjukkan **hanya ada PRIMARY KEY** (kolom `id`). Tidak ada unique key lain (misal kombinasi `pegawai_id + tahun`). Artinya, `ON DUPLICATE KEY UPDATE` hanya berfungsi jika `id` sama persis. Jika `id` berubah, duplikasi data akan terjadi.

### Join: `cuti_kuota` → `employee`

Query fetch menggunakan `INNER JOIN employee ON ck.emp_code = em.emp_code`.
- Jika ada `emp_code` di `cuti_kuota` yang **tidak ada** di tabel `employee`, record tersebut akan **hilang** (tidak dimigrasikan).

---

## Bug yang Ditemukan

### Bug 1 (KRITIS): INNER JOIN Dapat Menyebabkan Data Loss

**Lokasi:** `core/smartoffice/eo_cuti_kuota.py`, JOIN `employee`.

`INNER JOIN employee` berarti pegawai yang `emp_code`-nya tidak ditemukan di tabel `employee` (misal: sudah dihapus atau data tidak konsisten) akan **tidak ikut termigrasikan** tanpa peringatan apapun.

**Rekomendasi:**
- Ganti ke `LEFT JOIN employee AS em ON ck.emp_code = em.emp_code`.
- Setelah fetch, log baris yang `pegawai_id` (alias `em.emp_id`) bernilai NULL sebagai warning.
- Filter / drop baris dengan `pegawai_id` NULL sebelum proses simpan, karena FK tidak boleh NULL.

### Bug 2 (KRITIS): Tidak Ada Guard DataFrame Kosong

**Lokasi:** `v2_13_cuti_kuota.py`, fungsi `main()`.

Jika `fetch_cuti_kuota()` mengembalikan DataFrame kosong, proses `cleanup()` dan `save_cuti_kuota()` tetap dipanggil dan berpotensi error atau tidak menghasilkan apapun tanpa log yang jelas.

**Rekomendasi:**
- Tambahkan guard: `if ck_df.empty: LOGGER.info("No data found. Skipping."); return`
- Tambahkan logging jumlah record setelah fetch: `LOGGER.info(f"Fetched {len(ck_df)} records.")`

### Bug 3 (KRITIS): Tidak Ada Error Handling

**Lokasi:** `v2_13_cuti_kuota.py`, fungsi `main()`.

Tidak ada blok `try-except`. Jika terjadi error koneksi DB, runtime error, atau data corruption, script akan crash tanpa log terstruktur.

**Rekomendasi:**
- Bungkus seluruh isi `main()` dengan `try-except Exception as e`.
- Log error menggunakan `LOGGER.error(f"Migration failed: {e}", exc_info=True)`.
- Import `LOGGER` dari `core.config`.

### Bug 4 (KRITIS): Tidak Ada Idempotency Strategy yang Aman

**Lokasi:** `core/kepegawaian/kepeg_cuti_kuota.py`, fungsi `save_cuti_kuota()`.

Tabel target `cuti_kuota` **hanya memiliki PRIMARY KEY (`id`)** — tidak ada unique constraint lain pada kombinasi `(pegawai_id, tahun)`. Ini berarti:
- `ON DUPLICATE KEY UPDATE` hanya efektif jika `id` dari source tidak berubah.
- Jika script dijalankan ulang setelah ada perubahan `id` di source, data duplikat dapat masuk.

**Rekomendasi:**
- Koordinasikan dengan DBA untuk menambahkan unique constraint: `UNIQUE KEY uk_pegawai_tahun (pegawai_id, tahun)`.
- Atau, gunakan strategi `TRUNCATE` sebelum INSERT (harus dipertimbangkan dampaknya ke tabel lain yang ber-FK ke `cuti_kuota`).
- Tambahkan `updated_at=CURRENT_TIMESTAMP` pada bagian `ON DUPLICATE KEY UPDATE`.

### Bug 5 (SEDANG): NaN / NaT Tidak Disanitasi

**Lokasi:** `v2_13_cuti_kuota.py`, fungsi `cleanup()`.

Setelah `format_date_series(df["expired"])`, nilai `NaT` atau `NaN` dari pandas tidak dikonversi ke `None` sebelum dikirim ke pymysql. Ini dapat menyebabkan SQL error atau insert nilai yang tidak valid.

**Rekomendasi:**
- Di akhir `cleanup()`, sebelum `return df`, tambahkan: `df = df.replace({np.nan: None, pd.NaT: None, pd.NA: None})`
- Import `numpy as np` dan `pandas as pd` di file yang relevan.

### Bug 6 (RINGAN): Tidak Ada Logging Jumlah Record di Save

**Lokasi:** `v2_13_cuti_kuota.py`, fungsi `main()`.

Tidak ada log yang menampilkan berapa record berhasil di-save, sehingga sulit untuk melakukan validasi hasil migrasi.

**Rekomendasi:**
- Setelah `save_cuti_kuota(ck_df)`, tambahkan: `LOGGER.info(f"Successfully processed {len(ck_df)} records.")`

---

## Langkah Pengerjaan

### Persiapan

1. Baca dokumentasi best practice menggunakan **Context7** untuk:
   - Pattern pandas DataFrame handling dan NaN sanitization.
   - Pattern INSERT dengan pymysql dan `executemany`.
   - Python logging best practices.
2. Pastikan kamu berada di direktori project dan gunakan Python dari: `./.venv/bin/python`
3. Baca file `memory/project_bug_patterns.md` untuk checklist audit standar project.

### Step 1: Perbaiki JOIN di Fetch (Bug 1)

Di file `core/smartoffice/eo_cuti_kuota.py`:
- Ubah `INNER JOIN` menjadi `LEFT JOIN` pada join ke tabel `employee`.
- **Jangan tambahkan** kondisi filter di SQL — biarkan NULL `pegawai_id` masuk ke DataFrame, lalu filter di `cleanup()`.

### Step 2: Perbaiki `cleanup()` di Script Utama (Bug 2, 5)

Di `v2_13_cuti_kuota.py`, fungsi `cleanup()`:
- Setelah format kolom `expired`, tambahkan filter untuk drop baris dengan `pegawai_id` NULL (dampak dari perbaikan Bug 1) dan log sebagai warning.
- Tambahkan sanitasi NaN/NaT di akhir fungsi sebelum `return df`.

### Step 3: Perbaiki `main()` — Error Handling & Logging (Bug 2, 3, 6)

Di `v2_13_cuti_kuota.py`, fungsi `main()`:
- Bungkus isi `main()` dengan `try-except`.
- Tambahkan guard empty DataFrame setelah fetch.
- Tambahkan logging jumlah record setelah fetch dan setelah save.
- Import `LOGGER` dari `core.config` jika belum ada.

### Step 4: Perbaiki `save_cuti_kuota()` — ON DUPLICATE KEY UPDATE (Bug 4)

Di `core/kepegawaian/kepeg_cuti_kuota.py`:
- Tambahkan `updated_at=CURRENT_TIMESTAMP` pada bagian `ON DUPLICATE KEY UPDATE`.
- Diskusikan dengan DBA tentang penambahan unique constraint `(pegawai_id, tahun)` agar idempotency terjamin.

### Step 5: Verifikasi

Jalankan script dengan perintah:
```bash
./.venv/bin/python -m v2.v2_13_cuti_kuota
```

Pastikan:
- ✅ Tidak ada error atau traceback.
- ✅ Log menampilkan jumlah record yang di-fetch dan di-save.
- ✅ Jika ada `pegawai_id` NULL (LEFT JOIN miss), muncul warning di log.
- ✅ Kolom `expired` ter-format dengan benar di tabel target.
- ✅ Tidak ada duplikasi data saat script dijalankan dua kali.

---

## Checklist Standar (dari `memory/project_bug_patterns.md`)

- [ ] INNER JOIN → LEFT JOIN agar tidak ada data loss
- [ ] Filter baris dengan FK NULL setelah fetch
- [ ] Guard empty DataFrame (`if df.empty: return`)
- [ ] NaN/NaT sanitasi sebelum save
- [ ] Error handling di `main()` (try-except + LOGGER)
- [ ] Record count logging (setelah fetch dan setelah save)
- [ ] `ON DUPLICATE KEY UPDATE` lengkap + `updated_at=CURRENT_TIMESTAMP`
- [ ] Idempotency strategy — unique constraint atau TRUNCATE strategy
