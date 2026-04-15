# Issue Plan: Audit & Optimasi `v2_11_emp_contract_to_riwayat_kontrak.py`

**Tanggal dibuat:** 2026-04-14  
**Script target:** `v2/v2_11_emp_contract_to_riwayat_kontrak.py`  
**Core modules terkait:**
- `core/smartoffice/emp_contract.py` — fungsi fetch source data
- `core/kepegawaian/kepeg_riwayat_kontrak.py` — fungsi save ke target DB
- `core/kepegawaian/kepeg_biodata.py` — fungsi fetch biodata untuk lookup `pegawai_id`

---

## Konteks & Tujuan

Script ini memigrasikan data kontrak pegawai dari tabel `emp_contract` (SmartOffice) ke tabel `riwayat_kontrak` (kepegawaian_migrasi). Proses melibatkan enrichment `pegawai_id` dari biodata, normalisasi tanggal sentinel, dan derivasi kolom `jenis_kontrak` serta `is_latest`.

Audit ini bertujuan memperbaiki bug kritis, memastikan integritas data, dan menyesuaikan script dengan standar proyek.

---

## Informasi Schema (sudah diverifikasi dari DB)

### Target: `riwayat_kontrak` (kepegawaian_migrasi)

Dijalankan dengan:
```sql
DESCRIBE riwayat_kontrak;
SHOW INDEX FROM riwayat_kontrak WHERE Non_unique = 0;
```

**Kolom lengkap:**

| Kolom | Tipe | Nullable | Keterangan |
|---|---|---|---|
| `id` | bigint(20) | NO | PK auto_increment |
| `created_at` | timestamp | YES | default current_timestamp |
| `created_by` | varchar(255) | YES | |
| `is_deleted` | tinyint(1) | YES | default 0 |
| `updated_at` | timestamp | YES | auto update |
| `updated_by` | varchar(255) | YES | |
| `is_latest` | bit(1) | YES | |
| `jenis_kontrak` | tinyint(4) | YES | |
| `nama` | varchar(255) | YES | |
| `nipam` | varchar(255) | YES | |
| `nomor_kontrak` | varchar(255) | YES | MUL |
| `notes` | varchar(255) | YES | |
| `tanggal_mulai` | date | YES | MUL |
| `tanggal_selesai` | date | YES | |
| `tanggal_sk` | date | YES | |
| `jabatan_id` | bigint(20) | YES | MUL |
| `organisasi_id` | bigint(20) | YES | MUL |
| `pegawai_id` | bigint(20) | YES | MUL |

**⚠️ Kolom `version` TIDAK ADA di tabel target.** Script saat ini menyertakan `version=0` di INSERT → menyebabkan **SQL error**.

**Unique Key yang ada:**
```
UK29scgdjh0pqy24y60lq1mtecq → (pegawai_id, nomor_kontrak)
```
→ `ON DUPLICATE KEY UPDATE` **bisa digunakan** dengan kombinasi unik `(pegawai_id, nomor_kontrak)`.

---

### Source: `emp_contract` + `employee` + `emp_profile` + `position` (SmartOffice)

**Total record (setelah INNER JOIN):** 296 baris  
**Total `emp_contract` keseluruhan:** 343 baris  
**Record orphan (tidak match ke `employee`):** **47 baris** — hilang karena INNER JOIN

**Distribusi `ec_status`:**
| ec_status | Jumlah |
|---|---|
| 1 (aktif) | 294 |
| 2 (non-aktif/deleted) | 49 |

**Distribusi `emp_work_status` (pada data joined):**
| emp_work_status | Jumlah |
|---|---|
| 6 (KaryawanAktif) | 166 |
| 8 (BerhentiOrKeluar) | 130 |

**Distribusi prefix NIPAM:**
| Kategori | Jumlah |
|---|---|
| `nipam` berawalan `KO-` | 165 |
| `nipam` tidak berawalan `KO-` | 178 |

**Contoh data source (5 baris pertama):**

| ec_id | nik | nipam | nama | status_kerja | nomor_kontrak | tanggal_sk | tanggal_mulai | tanggal_selesai | jabatan_id | organisasi_id | ec_status |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 2 | 201608001 | 201608001 | Guntur Widodo | 8 | - | 2016-08-25 | 2016-08-25 | 2099-12-31 | 92 | 30 | 1 |
| 3 | T01 | T01 | Pjs. KaSubag. | 8 | SK-01 | 2016-08-08 | 2016-08-08 | 2099-12-31 | 41 | 47 | 1 |
| 13 | KO-143 | KO-143 | TARYOTO | 8 | INIT-KO-143 | 2016-08-24 | 2016-08-24 | 2017-08-24 | 85 | 27 | 1 |
| 20 | KO-163 | KO-163 | KUWAT SLAMET | 8 | INIT-KO-163 | 2016-08-24 | 2016-08-24 | 2017-08-24 | 87 | 28 | 1 |
| 49 | KO101 | KO101 | Guntur Widodo | 8 | 001 | 2016-08-27 | 2016-08-27 | 2017-08-27 | 11 | 54 | 1 |

**Sentinel `tanggal_sk` (nilai tidak valid):**
| Nilai | Jumlah |
|---|---|
| `0000-00-00` | 3 |

→ Script sudah menangani sentinel `0000-00-00` dengan replacement ke `1945-08-17`. Konfirmasi apakah replacement ini sudah benar secara bisnis.

---

## Bug yang Ditemukan

### Bug 1 — Kolom `version` tidak ada di tabel target (KRITIS)
**Lokasi:** `core/kepegawaian/kepeg_riwayat_kontrak.py`  
**Masalah:** Query INSERT menyertakan kolom `version` dengan nilai `0`, dan `ON DUPLICATE KEY UPDATE` juga menyertakan `version = version + 1`. Kolom `version` **tidak ada** di tabel `riwayat_kontrak`.  
**Dampak:** Script akan gagal dengan SQL error saat dijalankan.  
**Perbaikan:** Hapus `version` dari daftar kolom INSERT, hapus nilai `0` dari tuple data, dan hapus `version = version + 1` dari klausa `ON DUPLICATE KEY UPDATE`.

---

### Bug 2 — `ON DUPLICATE KEY UPDATE` tidak lengkap
**Lokasi:** `core/kepegawaian/kepeg_riwayat_kontrak.py`  
**Masalah:** Klausa `ON DUPLICATE KEY UPDATE` tidak menyertakan `updated_at = CURRENT_TIMESTAMP`.  
**Dampak:** Tidak ada penanda waktu update saat data berubah dan script dijalankan ulang.  
**Perbaikan:** Tambahkan `updated_at = CURRENT_TIMESTAMP` di akhir klausa `ON DUPLICATE KEY UPDATE`.

---

### Bug 3 — INNER JOIN menghilangkan 47 record orphan (DATA LOSS)
**Lokasi:** `core/smartoffice/emp_contract.py`, fungsi `fetch_emp_contract_for_riwayat_kontrak()`  
**Masalah:** Query menggunakan `INNER JOIN employee` sehingga 47 baris `emp_contract` yang tidak memiliki pasangan di tabel `employee` tidak ikut difetch. Data tersebut hilang diam-diam tanpa log peringatan.  
**Dampak:** 47 baris kontrak tidak dimigrasikan.  
**Perbaikan:** Putuskan secara bisnis apakah ke-47 record orphan ini perlu dimigrasikan atau boleh diabaikan. Jika boleh diabaikan, tambahkan log peringatan di `main()` untuk mencatat jumlah record yang dilewati. Jika perlu dimigrasikan, evaluasi penggantian `INNER JOIN` ke `LEFT JOIN`.

---

### Bug 4 — Tidak ada LOGGER dan error handling
**Lokasi:** `v2_11_emp_contract_to_riwayat_kontrak.py`, fungsi `main()`  
**Masalah:** Script tidak menggunakan `LOGGER` dari `core.config` dan tidak ada blok `try-except` di `main()`.  
**Dampak:** Jika terjadi error, tidak ada log terstruktur. Debugging di production menjadi sulit.  
**Perbaikan:** Import `LOGGER` dari `core.config`, bungkus seluruh isi `main()` dengan `try-except Exception`, tambahkan log jumlah record yang difetch dan disimpan.

---

### Bug 5 — Tidak ada empty DataFrame guard
**Lokasi:** `v2_11_emp_contract_to_riwayat_kontrak.py`, fungsi `main()`  
**Masalah:** Jika `fetch_emp_contract_for_riwayat_kontrak()` mengembalikan DataFrame kosong, script tetap melanjutkan ke `cleanup()` dan `save_...()`.  
**Dampak:** Potensi error atau operasi yang tidak perlu.  
**Perbaikan:** Tambahkan guard `if contract_df.empty: LOGGER.info("No data found. Skipping."); return` setelah fetch.

---

### Bug 6 — NaN/NaT tidak disanitasi sebelum save
**Lokasi:** `v2_11_emp_contract_to_riwayat_kontrak.py`, fungsi `cleanup()`  
**Masalah:** Tidak ada langkah sanitasi `df.replace({np.nan: None, pd.NaT: None, pd.NA: None})` di akhir `cleanup()`.  
**Dampak:** Nilai `NaN` atau `NaT` Pandas dapat lolos ke pymysql dan menyebabkan error atau data corrupt di SQL.  
**Perbaikan:** Tambahkan sanitasi NaN sebagai langkah **terakhir** di `cleanup()` sebelum `return df`.

---

### Bug 7 — `_get_pegawai_id()` tidak digunakan (dead code)
**Lokasi:** `v2_11_emp_contract_to_riwayat_kontrak.py`, fungsi `_get_pegawai_id()`  
**Masalah:** Fungsi `_get_pegawai_id()` di baris 74–80 sudah tidak dipakai (digantikan oleh `_build_pegawai_id_lookup()` yang lebih efisien), tetapi masih ada di file.  
**Dampak:** Kode yang tidak digunakan (dead code) menyulitkan pemeliharaan.  
**Perbaikan:** Hapus fungsi `_get_pegawai_id()`.

---

### Bug 8 — Logic `jenis_kontrak` perlu diverifikasi
**Lokasi:** `v2_11_emp_contract_to_riwayat_kontrak.py`, fungsi `cleanup()`  
**Masalah:** Derivasi `jenis_kontrak` menggunakan heuristik prefix `KO-` pada kolom `nipam`:
- Default `0` (PERPANJANGAN)
- `1` (PENGANGKATAN) jika nipam tidak berawalan `KO-`
- `2` jika `is_latest == True` dan `status_kerja == 8` (override ke nilai di luar `EJenisKontrak` enum: PERPANJANGAN=0, PENGANGKATAN=1)

**Masalah:** Nilai `jenis_kontrak = 2` tidak ada di `EJenisKontrak` enum (`core/enums.py`). Kemungkinan nilai ini dimaksudkan sebagai tipe kontrak tambahan yang belum terdokumentasi.  
**Dampak:** Data `jenis_kontrak = 2` dapat menyebabkan inkompatibilitas dengan sistem target yang menggunakan enum.  
**Perbaikan:** Konfirmasi dengan tim/PO apakah nilai `2` valid di sistem target atau perlu disesuaikan.

---

## Langkah-Langkah Pengerjaan

> **Prasyarat:** Gunakan `context7` untuk mendapatkan best practice terbaru terkait Pandas dan pymysql sebelum menulis kode.  
> **Python:** Gunakan selalu `./.venv/bin/python` untuk menjalankan script.

### Langkah 1 — Perbaiki `core/kepegawaian/kepeg_riwayat_kontrak.py`
1. Hapus kolom `version` dari daftar INSERT dan hapus nilai `0` dari tuple data.
2. Hapus `version = version + 1` dari klausa `ON DUPLICATE KEY UPDATE`.
3. Tambahkan `updated_at = CURRENT_TIMESTAMP` di akhir klausa `ON DUPLICATE KEY UPDATE`.

### Langkah 2 — Evaluasi dan putuskan kebijakan JOIN di `core/smartoffice/emp_contract.py`
1. Jalankan query berikut untuk memahami data orphan:
   ```sql
   SELECT ec.ec_id, ec.emp_code, ec.contract_no
   FROM emp_contract ec
   LEFT JOIN employee em ON ec.emp_code = em.emp_code
   WHERE em.emp_code IS NULL
   LIMIT 10;
   ```
2. Diskusikan dengan tim apakah 47 record orphan tersebut perlu dimigrasikan.
3. Apabila tidak perlu dimigrasikan: tambahkan log peringatan di `main()` yang mencatat jumlah record yang dilewati.
4. Apabila perlu dimigrasikan: ganti `INNER JOIN employee` dan `INNER JOIN emp_profile` menjadi `LEFT JOIN`, lakukan filtering null di `cleanup()`.

### Langkah 3 — Perbaiki `cleanup()` di script utama
1. Import `numpy as np` dan `LOGGER` dari `core.config`.
2. Verifikasi bersama tim apakah sentinel `0000-00-00` → `1945-08-17` sudah benar secara bisnis.
3. Tambahkan sanitasi NaN sebagai langkah terakhir sebelum `return df`:
   ```python
   df = df.replace({np.nan: None, pd.NaT: None, pd.NA: None})
   ```
4. Hapus fungsi `_get_pegawai_id()` yang tidak digunakan.

### Langkah 4 — Perbaiki `main()` di script utama
1. Bungkus seluruh isi `main()` dengan `try-except Exception as e: LOGGER.error(...)`.
2. Tambahkan guard `if contract_df.empty:` langsung setelah fetch.
3. Tambahkan `LOGGER.info(f"Fetched {len(contract_df)} records.")` setelah fetch.
4. Tambahkan `LOGGER.info(f"Successfully processed {len(contract_df)} records.")` setelah save.

### Langkah 5 — Klarifikasi `jenis_kontrak = 2`
1. Konfirmasi dengan tim/PO apakah nilai `jenis_kontrak = 2` valid dan didefinisikan di sistem target.
2. Jika tidak valid, sesuaikan logika derivasi (misalnya kembalikan ke `0` atau `1`).
3. Dokumentasikan keputusan ini di komentar kode.

### Langkah 6 — Verifikasi & Testing
1. Jalankan script dengan:
   ```bash
   ./.venv/bin/python -m v2.v2_11_emp_contract_to_riwayat_kontrak
   ```
2. Periksa output log: jumlah record difetch, dilewati (jika ada orphan), dan disimpan.
3. Verifikasi di DB target bahwa semua kolom terisi dengan benar:
   ```sql
   SELECT * FROM riwayat_kontrak ORDER BY id DESC LIMIT 10;
   ```
4. Jalankan ulang script untuk memverifikasi idempotency — tidak ada duplikasi data, data yang berubah di source ikut diperbarui di target.

---

## Referensi

- Gunakan **context7** untuk best practice: Pandas vectorized operations, pymysql batch insert, dan NaN handling.
- Lihat script yang sudah dioptimasi sebelumnya: `v2_8_emp_family_to_profil_keluarga.py` dan `v2_9_2_emp_sk_to_riwayat_sk.py` sebagai referensi pola `main()`, `cleanup()`, dan `save()`.
- Checklist audit lengkap: lihat `memory/project_bug_patterns.md` bagian **Checklist Audit Script Baru**.
