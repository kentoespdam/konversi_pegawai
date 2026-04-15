# Plan: Audit & Perbaikan `v2_9_1_init_emp_sk_from_riwayat_sk_optional.py`

## Latar Belakang

Script ini bertugas melakukan **inisialisasi data `emp_sk`** di database SmartOffice (bukan kepegawaian_migrasi) berdasarkan data dari tabel `emp_work_history`. Tujuannya adalah mengisi record SK yang belum ada di `emp_sk`, khususnya SK yang berasal dari riwayat kerja pegawai.

Hasil audit menunjukkan beberapa **bug kritis dan ketidaksempurnaan** yang perlu diperbaiki sebelum script ini aman dijalankan di lingkungan produksi.

---

## Hasil Audit Awal

### Bug Kritis

#### Bug 1: Logika Boolean Salah di `filter_sk()`
- **Lokasi**: Fungsi `filter_sk()`, baris `mask = df["esk_no_sk"].isnull() or df["no_sk"].eq(no_sk)`
- **Masalah**: Operator `or` adalah operator Python bukan pandas. Penggunaan `or` pada dua pandas Series akan menghasilkan error `ValueError: The truth value of a Series is ambiguous`.
- **Rekomendasi**: Ganti operator `or` dengan operator bitwise `|`, sehingga menjadi `mask = df["esk_no_sk"].isnull() | df["no_sk"].eq(no_sk)`.

#### Bug 2: Fungsi `filter_sk()` Tidak Pernah Dipanggil
- **Lokasi**: `main()` dan `filter_sk()`
- **Masalah**: Fungsi `filter_sk()` didefinisikan tapi tidak digunakan di `main()`. Ini menunjukkan ada logika filtering yang mungkin tertinggal atau sengaja di-skip.
- **Rekomendasi**: Tentukan apakah fungsi ini masih relevan. Jika ya, integrasikan ke dalam `main()`. Jika tidak, hapus untuk menghindari kebingungan.

#### Bug 3: Tidak Ada Sanitasi NaN/NaT Sebelum Insert
- **Lokasi**: Fungsi `cleanup_init()`
- **Masalah**: Kolom `no_sk` dan `notes` bisa mengandung `None`, `NaN`, atau `NaT` dari pandas. Jika langsung dikirim ke pymysql tanpa sanitasi, bisa menyebabkan error insert atau data corrupt.
- **Rekomendasi**: Tambahkan baris `df = df.replace({np.nan: None, pd.NaT: None, pd.NA: None})` **di akhir** fungsi `cleanup_init()` sebelum `return df`.

#### Bug 4: Tidak Ada Error Handling Global
- **Lokasi**: Fungsi `main()`
- **Masalah**: Tidak ada blok `try-except` di `main()`. Jika terjadi error di tengah proses, tidak ada log terstruktur yang membantu debugging.
- **Rekomendasi**: Bungkus seluruh isi `main()` dengan `try-except Exception as e:` dan tambahkan `LOGGER.error(f"Migration failed: {e}", exc_info=True)`.

### Bug Penting (Non-Kritis)

#### Bug 5: Kolom `no_sk` Mengandung Nilai Tidak Valid
- **Temuan dari database**: Nilai `no_sk` di `emp_work_history` mencakup: `"-"`, string kosong `""`, `None`, dan nilai yang valid.
- **Masalah**: Nilai `-` dan string kosong tidak bermakna sebagai nomor SK. Nilai ini tidak boleh di-insert apa adanya ke tabel `emp_sk`.
- **Rekomendasi**: Di `cleanup_init()`, tambahkan logika untuk mengganti nilai `no_sk` yang berupa `"-"` atau string kosong dengan nilai default misalnya `"Init SmartOffice"` (konsisten dengan fungsi `update_init_smartoffice_no_sk()` yang sudah ada di module yang sama).

#### Bug 6: Format Tanggal Tidak Divalidasi
- **Temuan dari database**: Kolom `tgl_sk` dan `tmt_sk` bertipe `object` (string) saat di-fetch. Tabel target menerima tipe `date`.
- **Masalah**: Tidak ada format ulang tanggal, sehingga jika ada nilai tanggal yang malformed, insert akan gagal.
- **Rekomendasi**: Gunakan helper `format_date_series()` dari `v2_helper` untuk memformat kolom `tgl_sk` dan `tmt_sk` di dalam `cleanup_init()`.

#### Bug 7: Tidak Ada Record Count Logging
- **Masalah**: Tidak ada log berapa record yang di-fetch dan di-save. Menyulitkan monitoring dan debugging.
- **Rekomendasi**: Tambahkan `LOGGER.info(f"Fetched {len(sk_df)} records.")` setelah fetch, dan `LOGGER.info(f"Successfully processed {len(sk_df)} records.")` setelah save.

### Masalah Idempotency

#### Masalah 8: Tabel `emp_sk` Tidak Memiliki UNIQUE KEY
- **Temuan dari database (`DESCRIBE emp_sk`)**: Tabel hanya memiliki PK `id` (auto-increment). Tidak ada UNIQUE KEY pada kombinasi kolom seperti `(emp_id, no_sk)`.
- **Dampak**: Klausa `ON DUPLICATE KEY UPDATE` di `save_emp_sk_from_emp_work_history()` **tidak akan berfungsi**. Setiap eksekusi ulang script akan menyebabkan **duplikasi data**.
- **Rekomendasi**:
  1. **Opsi A (Direkomendasikan)**: Koordinasi dengan DBA untuk menambahkan UNIQUE KEY pada kombinasi kolom yang tepat, misalnya `UNIQUE KEY uq_emp_sk (emp_id, no_sk)`.
  2. **Opsi B (Fallback)**: Jika tidak bisa mengubah schema, gunakan strategi **TRUNCATE + INSERT** — hapus dulu record dengan `ref_id = 0` dan `status = 1` (record hasil inisialisasi) sebelum insert ulang.

### Masalah Desain

#### Masalah 9: Script Menulis ke Database SmartOffice (Bukan kepegawaian_migrasi)
- **Temuan**: Fungsi `save_emp_sk_from_emp_work_history()` menggunakan `save_update_smartoffice()` — artinya INSERT dilakukan ke DB sumber (`smartoffice`), bukan ke DB target `kepegawaian_migrasi`.
- **Ini mungkin disengaja** (inisialisasi data di SmartOffice), namun perlu dikonfirmasi dan didokumentasikan dengan jelas agar tidak membingungkan.
- **Rekomendasi**: Tambahkan komentar atau docstring yang menjelaskan bahwa script ini menulis ke SmartOffice sebagai tahap pra-migrasi.

---

## Langkah Pengerjaan

> Gunakan Python dari virtual environment: `./.venv/bin/python`
> Gunakan **context 7** untuk mendapatkan referensi best practice pandas, pymysql, dan logging.

### Langkah 1: Inspeksi Schema dan Sample Data
Sebelum mulai coding, verifikasi kondisi aktual database:
```
./.venv/bin/python -c "from core.config import fetch_smartoffice; df = fetch_smartoffice('DESCRIBE emp_sk'); print(df.to_string())"
```
Periksa:
- Kolom apa saja yang ada di tabel `emp_sk`
- Apakah ada UNIQUE KEY selain PK
- Sample data dari `app_work_history` untuk memahami nilai-nilai aktual

### Langkah 2: Perbaiki Bug Kritis di Script Utama

File yang diubah: `v2/v2_9_1_init_emp_sk_from_riwayat_sk_optional.py`

1. **Perbaiki `filter_sk()`**: Ganti `or` dengan `|` pada baris logika mask.
2. **Tambahkan NaN sanitasi** di akhir `cleanup_init()` menggunakan `df.replace({np.nan: None, pd.NaT: None, pd.NA: None})`.
3. **Tambahkan format tanggal** di `cleanup_init()` menggunakan `format_date_series()` dari `v2_helper`.
4. **Sanitasi kolom `no_sk`**: Ganti nilai `"-"` dan string kosong dengan `"Init SmartOffice"`.
5. **Bungkus `main()` dengan `try-except`** dan tambahkan log record count setelah fetch dan save.

### Langkah 3: Tangani Idempotency

Pilih salah satu opsi:
- **Opsi A**: Ajukan ke DBA untuk menambah UNIQUE KEY `(emp_id, no_sk)` di tabel `emp_sk`. Setelah ada, pastikan `ON DUPLICATE KEY UPDATE` di `save_emp_sk_from_emp_work_history()` juga memperbarui semua kolom + `updated_at=CURRENT_TIMESTAMP` (perhatikan: kolom `updated_at` perlu dicek apakah ada di schema).
- **Opsi B**: Implementasi cek duplikasi manual di `cleanup_init()` — filter hanya record yang `no_sk`-nya belum ada di `emp_sk`.

### Langkah 4: Perbaiki Modul Core (Jika Diperlukan)

File yang mungkin diubah: `core/smartoffice/emp_sk.py`

1. Verifikasi kolom yang di-INSERT di `save_emp_sk_from_emp_work_history()` sesuai dengan schema tabel.
2. Tambahkan `updated_at=CURRENT_TIMESTAMP` di `ON DUPLICATE KEY UPDATE` **jika** kolom `updated_at` ada di tabel.
3. Perbarui `created_by` agar menggunakan nilai string `'SYSTEM'` bukan integer `None`.

### Langkah 5: Test Eksekusi

Jalankan dry-run untuk melihat data yang akan diproses:
```
./.venv/bin/python -c "
from core.smartoffice.emp_work_history import fetch_emp_work_history_for_emp_sk
df = fetch_emp_work_history_for_emp_sk()
print('Total records:', len(df))
print(df.head(10).to_string())
"
```

Lalu jalankan script utama:
```
./.venv/bin/python -m v2.v2_9_1_init_emp_sk_from_riwayat_sk_optional
```

Verifikasi hasil:
- Tidak ada error di log
- Record count sesuai
- Tidak ada duplikasi data di tabel `emp_sk`

---

## Referensi

- Gunakan **context 7** untuk best practice:
  - Pandas: sanitasi NaN, format tanggal, vectorized operations
  - pymysql: parameterized query, connection pool
  - Python logging: LOGGER best practice
- Lihat contoh implementasi terbaik di `v2_6_emp_education_to_pendidikan.py` dan `v2_8_emp_family_to_profil_keluarga.py`
- Lihat `memory/project_bug_patterns.md` untuk checklist audit lengkap
- Lihat `memory/project_architecture.md` untuk konvensi kode proyek
