# Plan Migrasi v2 - Master Gaji

## 1. Objektif
Dokumen ini menjadi panduan tingkat tinggi (high-level) bagi AI model kecil atau junior developer untuk melakukan inspeksi, perbaikan bug, dan optimisasi pada proses migrasi `v2_master_gaji.py` beserta modul pendukungnya di dalam `core/smartoffice/` dan `core/kepegawaian/`.

## 2. Praktik Terbaik Code & Environment
1. **Environment:** Gunakan spesifik python executable dari environment project yaitu `./.venv/bin/python`.
2. **Context 7:** Mengacu pada dokumentasi Context 7 untuk memvalidasi *best practices* Python terkini. Lakukan optimasi penggunaan operasi Pandas yang efisien (meminimumkan iterasi lambat `itertuples` atau iterasi pada Pandas ketika memungkinkan), penyamaan manajemen nilai kosong (`None` vs `NaN`), implementasi idempotency pada query basis data (penggunaan klausul `ON DUPLICATE KEY UPDATE` penuh), penyertaan logging durasi komputasi yang menyeluruh dan handal, serta penambahan *exception handling* (try-except block) global pada fungsi utamanya.
3. Gunakan *skills* agent yang tersedia bila diperlukan dan pelajari file `memory/project_bug_patterns.md` serta `memory/project_architecture.md` secara khusus.

## 3. Contoh Value Database
Untuk meminimalisir pengambilan data ulang ke database selama perbaikan, berikut adalah beberapa **snapshot sample data** dari source dan target master gaji:

### A. Gaji Tunjangan (`eo_salary_allowance` → `gaji_tunjangan`)
**Source: `smartoffice.eo_salary_allowance`**
| id | code | ref_type | ref_id | value | created_by | created |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| 20 | air | 5 | 0 | 225000 | admin | 2019-10-18 10:28:44 |

**Target: `kepegawaian_migrasi.gaji_tunjangan`**
Kolom inti yang dipetakan: `id, jenis_tunjangan, level_id, golongan_id, nominal`. Target tabel ini juga memiliki `created_by`, `updated_at`, dan `version`.

### B. Pendapatan Non Pajak (`eo_salary_non_taxable_income` → `gaji_pendapatan_non_pajak`)
**Source: `smartoffice.eo_salary_non_taxable_income`**
| id | code | value | status | created_by |
| :--- | :--- | :--- | :--- | :--- |
| 1 | TK/0 | 54000000 | 1 | admin |

**Target: `kepegawaian_migrasi.gaji_pendapatan_non_pajak`**
Kolom inti inti: `id`, `kode`, `nominal`, `notes`, `is_deleted`. Target juga menuntut `created_by` dan `updated_at`.

### C. Parameter Setting (`sys_reference` → `gaji_parameter_setting`)
**Source: `smartoffice.sys_reference`** (Difilter `code='payroll'`)
| id | code | text | num_1 | status |
| :--- | :--- | :--- | :--- | :--- |
| 1 | payroll | GajiPokok | 1 | Enable |

**Target: `kepegawaian_migrasi.gaji_parameter_setting`**
Catatan mapping: `text` -> `kode`, `num_1` -> `nominal`.

### D. Potongan TKK (`eo_salary_tkk_reduction` → `gaji_potongan_tkk`)
**Source: `smartoffice.eo_salary_tkk_reduction`**
| id | emp_flag | pos_level | golongan | potongan | is_deleted |
| :--- | :--- | :--- | :--- | :--- | :--- |
| 100 | 1 | 4 | 0 | 45000 | 1 |

**Target: `kepegawaian_migrasi.gaji_potongan_tkk`**
Mapping struktural: map enum status pegawai dari `emp_flag`, serta level (dari `pos_level`) dan golongan, nominal ke `potongan`.

## 4. Identifikasi Bug dan Rekomendasi Perbaikan
Terdapat beberapa bug berulang pada skrip `v2_master_gaji.py` dan submodulnya:
1. **Tidak Ada Guard untuk DataFrame Kosong**: Tambahkan `if df.empty: return` dan mekanisme *early-exit* sesudah data ditarik (`fetch_*`) di masing-masing sub-langkah.
2. **Tidak Ada Global Exception Handling pada Skrip Utama**: Fungsi `main()` tidak terproteksi blok `try-except` di tingkat global, sehingga seluruh proses eksekusi tidak aman bila ada sub-proses yang error. Rekomendasi perbaikan ada di `project_bug_patterns.md`.
3. **Pembersihan `NaN` / `NaT` absen (Pandas sanitization)**: Data kotor bersumber Pandas (misal object NaN/pd.NA) dimasukkan ke DB. Ini adalah anti-pattern yang dapat menebabkan gagalnya INSERT PyMySQL. Gunakan `df.replace({np.nan: None, pd.NaT: None, pd.NA: None})` sebelum iterasi target row penyimpanan.
4. **Idempotency Data (Klausa ON DUPLICATE KEY UPDATE tidak sempurna)**:
   - File seperti `kepeg_gaji_pendapatan_non_pajak.py`, `kepeg_gaji_tunjangan.py`, murni tidak meng-*update* metadata lengkap (seperti melupakan `created_by=VALUES(created_by)` atau `updated_at=CURRENT_TIMESTAMP`).
   - File `kepeg_potongan_tkk.py` melewatkan update kolom FK / lookup seperti `status_pegawai`, `level_id`, dan `golongan_id`, hanya mengupdate nominal. Pastikan update seluruh field inti pada *duplicate key update*.
5. **Logic Value 0 dan Negative Pada Sub-routine Lookup**:
   - Di file target, logika check `if row.golongan_id > 0 else None` bertemu `fillna(-1)` atau unmapped value `-1`. Hal ini dapat menyebabkan kolom integer dikirim tidak terprediksi bila input sumbernya absen atau gagal *lookup* mapping yang tersedia, harus diselaraskan secara konsisten, jika tidak ditemukan nilainya buat agar bernilai `None`. Cek logic mapping return default value `DEFAULT_UNKNOWN_INT` dan implementasinya.
6. **Kesalahan Update Field Meta Database Target**: Skrip lupa menambah atau mengubah `version`, dan parameter `is_deleted` sebaiknya dikonversi menjadi integer atau bool boolean pure sesuai requirement `tinyint(1)` target.

## 5. Rekomendasi Optimisasi
- Rapihkan alur eksekusi pada `v2_master_gaji.py` agar setiap `fetch`, `cleanup`, dan `save` berada di blok fungsinya masing-masing yang dikoordinasikan secara atomik, dan pergunakan logging standard `v2_helper` `LOGGER.info("Fetched ... records")` untuk *tracking* yang visibel.
- Seluruh perbaikan harus mengacu ke arsitektur `v2` (memisahkan modul pengambilan-database / *smartoffice*, file master eksekusi utama (v2/), dan penyimpanan database tujuan / *kepegawaian*) demi mematuhi clean code sesuai **Context 7**.
