# Issue Plan: Audit & Optimasi `v2_10_emp_work_history_to_riwayat_mutasi.py`

**Tanggal dibuat:** 2026-04-14  
**Script target:** `v2/v2_10_emp_work_history_to_riwayat_mutasi.py`  
**Core modules terkait:**
- `core/smartoffice/emp_work_history.py` — fungsi fetch source data
- `core/kepegawaian/kepeg_riwayat_mutasi.py` — fungsi save ke target DB

---

## Konteks & Tujuan

Script ini memigrasikan data riwayat mutasi pegawai dari tabel `emp_work_history` (SmartOffice) ke tabel `riwayat_mutasi` (kepegawaian_migrasi). Proses melibatkan pengayaan data (enrichment) dari tabel master SK, golongan, dan profesi sebelum disimpan.

Audit ini bertujuan memperbaiki bug kritis, memastikan integritas data, dan menyesuaikan script dengan standar proyek.

---

## Informasi Schema (sudah diverifikasi dari DB)

### Target: `riwayat_mutasi` (kepegawaian_migrasi)

Dijalankan dengan:
```sql
DESCRIBE riwayat_mutasi;
SHOW INDEX FROM riwayat_mutasi WHERE Non_unique = 0;
```

**Kolom lengkap:**

| Kolom | Tipe | Nullable | Keterangan |
|---|---|---|---|
| `id` | bigint(20) | NO | PK auto_increment |
| `pegawai_id` | bigint(20) | YES | FK ke pegawai |
| `riwayat_sk_id` | bigint(20) | YES | FK ke riwayat_sk |
| `nipam` | varchar(255) | YES | |
| `nama` | varchar(255) | YES | |
| `tmt_berlaku` | date | YES | |
| `tanggal_berakhir` | date | YES | |
| `jenis_mutasi` | tinyint(4) | YES | |
| `organisasi_id` | bigint(20) | YES | |
| `nama_organisasi` | varchar(255) | YES | |
| `jabatan_id` | bigint(20) | YES | |
| `nama_jabatan` | varchar(255) | YES | |
| `profesi_id` | bigint(20) | YES | |
| `nama_profesi` | varchar(255) | YES | |
| `golongan_id` | bigint(20) | YES | |
| `nama_golongan` | varchar(255) | YES | |
| `golongan_lama_id` | bigint(20) | YES | **⚠️ TIDAK diisi script saat ini** |
| `nama_golongan_lama` | varchar(255) | YES | **⚠️ TIDAK diisi script saat ini** |
| `organisasi_lama_id` | bigint(20) | YES | |
| `nama_organisasi_lama` | varchar(255) | YES | |
| `jabatan_lama_id` | bigint(20) | YES | |
| `nama_jabatan_lama` | varchar(255) | YES | |
| `profesi_lama_id` | bigint(20) | YES | |
| `nama_profesi_lama` | varchar(255) | YES | |
| `notes` | varchar(255) | YES | |
| `is_deleted` | tinyint(1) | YES | |
| `created_at` | timestamp | YES | |
| `created_by` | varchar(255) | YES | |
| `updated_at` | timestamp | YES | auto update |
| `updated_by` | varchar(255) | YES | |

**Unique Key yang ada:**
```
UK3kcomkcxj12ct7qpphyrfgf7a → (pegawai_id, riwayat_sk_id)
```
→ `ON DUPLICATE KEY UPDATE` **bisa digunakan**, tetapi hanya berlaku untuk kombinasi unik `(pegawai_id, riwayat_sk_id)`.

> **Catatan penting:** `version` column **TIDAK ADA** di tabel target. INSERT saat ini menyertakan `version=0` → **menyebabkan SQL error**.

---

### Source: `emp_work_history` (SmartOffice)

Dijalankan dengan:
```sql
SELECT ewh_id, emp_code, ewh_sk_no, ewh_type, ewh_status, ewh_sdate, ewh_edate,
       ewh_org_name, ewh_pos_name, ewh_note
FROM emp_work_history LIMIT 5;
```

**Contoh data source (5 baris pertama):**

| ewh_id | emp_code | ewh_sk_no | ewh_type | ewh_status | ewh_sdate | ewh_edate | ewh_org_name | ewh_pos_name | ewh_note |
|---|---|---|---|---|---|---|---|---|---|
| 1 | 641100143 | Init SmartOffice | 1 | 1 | 2016-08-24 | 2025-11-10 | DIREKTORAT UTAMA | Direktur Utama | None |
| 2 | 690700169 | Init SmartOffice | 1 | 1 | 2016-08-24 | 2025-11-10 | DIREKTORAT ADMIN & KEUANGAN | Direktur Adm. & Keuangan | None |
| 3 | 561100297 | Init SmartOffice | 1 | 1 | 2016-08-24 | 2016-11-10 | DIREKTORAT TEKNIK | Direktur Teknik | None |
| 4 | 710100239 | Init SmartOffice | 1 | 1 | 2016-08-24 | 2020-11-24 | BID. PENGAWASAN INTERNAL | Ka. Bid. Pengawasan Internal | None |
| 5 | 721100225 | Init SmartOffice | 1 | 1 | 2016-08-24 | 2017-11-01 | SUB BID PENJAMINAN MUTU | Ka. Sub Bid. Penjaminan Mutu | None |

**Total record:** 1.217 baris

**Nilai `ewh_type` yang ada di data:** `1`, `2`, `4`

**Mapping `jenis_mutasi` (ewh_type → kepegawaian):**
| ewh_type (source) | jenis_mutasi (target) |
|---|---|
| 1 | 0 |
| 2 | 1 |
| 3 | 4 |
| 4 | 6 |

> Perhatikan: `ewh_type = 4` dipetakan ke `jenis_mutasi = 6`, tetapi tidak ada baris `ewh_type = 3` di data aktual. Verifikasi apakah mapping ini sudah benar.

---

## Bug yang Ditemukan

### Bug 1 — `version` column tidak ada di tabel target (KRITIS)
**Lokasi:** `core/kepegawaian/kepeg_riwayat_mutasi.py`, baris INSERT  
**Masalah:** Query INSERT menyertakan kolom `version` dan nilai `0`, tetapi kolom `version` **tidak ada** di tabel `riwayat_mutasi`.  
**Dampak:** Script akan gagal dengan SQL error saat dijalankan.  
**Perbaikan:** Hapus `version` dari daftar kolom INSERT dan hapus nilai `0` dari tuple data.

---

### Bug 2 — `ON DUPLICATE KEY UPDATE` tidak lengkap
**Lokasi:** `core/kepegawaian/kepeg_riwayat_mutasi.py`  
**Masalah:** Klausa `ON DUPLICATE KEY UPDATE` hanya mengisi `pegawai_id=VALUES(pegawai_id)` — kolom lain tidak ikut diperbarui.  
**Dampak:** Jika data di source berubah dan script dijalankan ulang, perubahan tidak akan tersimpan (data stale).  
**Perbaikan:** Update **semua kolom atribut** di klausa `ON DUPLICATE KEY UPDATE`, tambahkan `updated_at=CURRENT_TIMESTAMP`.

---

### Bug 3 — Kolom `golongan_lama_id` dan `nama_golongan_lama` tidak diisi
**Lokasi:** `v2_10_emp_work_history_to_riwayat_mutasi.py` fungsi `cleanup()` dan `core/kepegawaian/kepeg_riwayat_mutasi.py`  
**Masalah:** Tabel target memiliki kolom `golongan_lama_id` dan `nama_golongan_lama`, namun script tidak mengisi kedua kolom ini. Tidak ada logika di `cleanup()` untuk memetakan golongan lama dari data SK terdahulu.  
**Dampak:** Kedua kolom selalu bernilai `NULL` di target.  
**Perbaikan:** Tentukan strategi pengisian — apakah dari `riwayat_sk` sebelumnya berdasarkan `riwayat_sk_id` lama, atau dari data source lain. Jika tidak tersedia di source, dokumentasikan keputusan ini.

---

### Bug 4 — Tidak ada LOGGER dan error handling
**Lokasi:** `v2_10_emp_work_history_to_riwayat_mutasi.py`, fungsi `main()`  
**Masalah:** Script tidak menggunakan `LOGGER` dari `core.config` dan tidak ada `try-except` di `main()`.  
**Dampak:** Jika terjadi error, tidak ada log terstruktur. Sulit debugging di production.  
**Perbaikan:** Import `LOGGER` dari `core.config`, bungkus seluruh `main()` dengan `try-except`, tambahkan logging jumlah record yang difetch dan disimpan.

---

### Bug 5 — Tidak ada empty DataFrame guard
**Lokasi:** `v2_10_emp_work_history_to_riwayat_mutasi.py`, fungsi `main()`  
**Masalah:** Jika `fetch_emp_work_history_for_riwayat_mutasi()` mengembalikan DataFrame kosong, script tetap melanjutkan ke `cleanup()` dan `save_...()` tanpa pengecekan.  
**Dampak:** Potensi error atau operasi yang tidak perlu.  
**Perbaikan:** Tambahkan guard `if df.empty: LOGGER.info("..."); return` setelah fetch.

---

### Bug 6 — NaN/NaT tidak disanitasi sebelum save
**Lokasi:** `v2_10_emp_work_history_to_riwayat_mutasi.py`, fungsi `cleanup()`  
**Masalah:** Tidak ada langkah sanitasi `df.replace({np.nan: None, pd.NaT: None, pd.NA: None})` di akhir `cleanup()`.  
**Dampak:** Nilai `NaN` atau `NaT` Pandas dapat lolos ke pymysql dan menyebabkan error atau data corrupt di SQL.  
**Perbaikan:** Tambahkan sanitasi NaN sebagai langkah **terakhir** di `cleanup()` sebelum `return df`.

---

### Bug 7 — Join INNER di fetch source dapat menghilangkan data
**Lokasi:** `core/smartoffice/emp_work_history.py`, fungsi `fetch_emp_work_history_for_riwayat_mutasi()`  
**Masalah:** Query menggunakan `INNER JOIN employee` dan `INNER JOIN emp_profile`. Jika ada data `emp_work_history` yang orphan (emp_code tidak match di `employee`), data tersebut akan hilang diam-diam.  
**Dampak:** Data loss tanpa peringatan.  
**Perbaikan:** Evaluasi apakah `INNER JOIN` sudah tepat secara bisnis. Jika ada kemungkinan data orphan, dokumentasikan atau ganti dengan `LEFT JOIN` dan tambahkan filter.

---

### Bug 8 — Filter `riwayat_sk_id > 0` membuang data tanpa SK yang valid
**Lokasi:** `v2_10_emp_work_history_to_riwayat_mutasi.py`, baris filter di `main()`  
**Masalah:** `work_history_df[work_history_df["riwayat_sk_id"] > 0]` membuang semua record yang tidak berhasil di-resolve ke `riwayat_sk`. Tidak ada log berapa banyak record yang dibuang.  
**Dampak:** Data loss terselubung. Perlu diketahui berapa % data yang kehilangan mapping SK.  
**Perbaikan:** Tambahkan `LOGGER.warning(f"Skipping {n} records without riwayat_sk_id")` sebelum filter.

---

## Langkah-Langkah Pengerjaan

> **Prasyarat:** Gunakan `context7` untuk mendapatkan best practice terbaru terkait Pandas dan pymysql sebelum menulis kode.  
> **Python:** Gunakan selalu `./.venv/bin/python` untuk menjalankan script.

### Langkah 1 — Perbaiki `core/kepegawaian/kepeg_riwayat_mutasi.py`
1. Hapus `version` dari daftar kolom INSERT dan hapus nilai `0` dari tuple data.
2. Lengkapi klausa `ON DUPLICATE KEY UPDATE` untuk update semua kolom atribut.
3. Tambahkan `updated_at=CURRENT_TIMESTAMP` di `ON DUPLICATE KEY UPDATE`.
4. Tambahkan kolom `golongan_lama_id` dan `nama_golongan_lama` ke INSERT dan tuple (setelah mapping di `cleanup()` selesai — lihat Langkah 2).

### Langkah 2 — Perbaiki `cleanup()` di script utama
1. Tambahkan logika untuk memetakan `golongan_lama_id` dan `nama_golongan_lama`. Diskusikan dengan tim apakah data ini bisa diturunkan dari SK sebelumnya atau harus `NULL`.
2. Tambahkan import `numpy as np` dan `LOGGER` dari `core.config`.
3. Tambahkan sanitasi NaN sebagai langkah terakhir: `df = df.replace({np.nan: None, pd.NaT: None, pd.NA: None})`.

### Langkah 3 — Perbaiki `main()` di script utama
1. Bungkus seluruh isi `main()` dengan `try-except Exception as e: LOGGER.error(...)`.
2. Tambahkan `if work_history_df.empty:` guard langsung setelah fetch.
3. Tambahkan `LOGGER.info(f"Fetched {len(work_history_df)} records.")` setelah fetch.
4. Tambahkan `LOGGER.warning(f"Skipping {n} records without riwayat_sk_id")` sebelum filter `riwayat_sk_id > 0`.
5. Tambahkan `LOGGER.info(f"Successfully processed {len(work_history_df)} records.")` setelah save.

### Langkah 4 — Evaluasi JOIN di fetch source
1. Buka `core/smartoffice/emp_work_history.py`.
2. Cek apakah ada data `emp_work_history` yang orphan dengan query:
   ```sql
   SELECT COUNT(*) FROM emp_work_history ewh
   LEFT JOIN employee em ON ewh.emp_code = em.emp_code
   WHERE em.emp_code IS NULL;
   ```
3. Jika ada, putuskan apakah data tersebut perlu dimigrasikan atau memang diabaikan. Dokumentasikan keputusan ini.

### Langkah 5 — Verifikasi & Testing
1. Jalankan script dengan `./.venv/bin/python -m v2.v2_10_emp_work_history_to_riwayat_mutasi`.
2. Periksa output log untuk memastikan jumlah record yang difetch, dilewati, dan disimpan.
3. Verifikasi di DB target bahwa kolom `golongan_lama_id`, `nama_golongan_lama`, dan semua kolom lain sudah terisi dengan benar.
4. Jalankan ulang script untuk memverifikasi idempotency (tidak ada data duplikat / data berubah sesuai source).

---

## Referensi

- Gunakan **context7** untuk best practice: Pandas vectorized operations, pymysql batch insert, dan NaN handling.
- Lihat script yang sudah dioptimasi sebelumnya: `v2_8_emp_family_to_profil_keluarga.py` dan `v2_9_2_emp_sk_to_riwayat_sk.py` sebagai referensi pola `main()`, `cleanup()`, dan `save()`.
- Checklist audit lengkap: lihat `memory/project_bug_patterns.md` bagian **Checklist Audit Script Baru**.
