# Plan Audit, Perbaikan, dan Optimasi: `eo_salary_allowance.py`

Dokumen ini disusun sebagai panduan bagi **Junior Developer atau AI Model** untuk memperbaiki dan mengoptimalkan modul `core/smartoffice/eo_salary_allowance.py` yang merupakan bagian dari pipeline migrasi Master Gaji (`v2/v2_master_gaji.py`).

Modul pendukung yang terlibat:
- `core/smartoffice/eo_salary_allowance.py` — fetch dan cleanup data tunjangan dari sumber
- `core/kepegawaian/kepeg_gaji_tunjangan.py` — query INSERT ke tabel target `gaji_tunjangan`
- `v2/v2_master_gaji.py` — orchestrator yang memanggil fetch, cleanup, dan save

Sesuai pedoman pengerjaan, **wajib menggunakan Context 7** saat mengimplementasikan langkah-langkah di bawah ini untuk memastikan _best practice_ penulisan kode Python, penanganan _exception_, standar pemrosesan Pandas, dan query SQL. Selalu jalankan environment menggunakan Python dari dalam `.venv` (`./.venv/bin/python`).

---

## 1. Contoh Value Database (Referensi)

Untuk meminimalisir pengambilan data ulang ke database selama perbaikan, berikut adalah **snapshot sample data** dari tabel sumber.

### Source: `smartoffice.salary_allowance` (Total: 63 baris)

| id | jenis_tunjangan (code) | level_id (ref_type) | golongan_id (ref_id) | nominal (value) |
| :--- | :--- | :--- | :--- | :--- |
| 1 | jabatan | 1 | 4 | 1500000 |
| 2 | jabatan | 1 | 5 | 1000000 |
| 3 | jabatan | 2 | 1 | 250000 |
| 7 | jabatan | 2 | 5 | 275000 |
| 11 | jabatan | 2 | 9 | 300000 |
| 15 | tkk | 1 | 4 | 2500000 |

### Fakta Domain Penting

- **Distinct `code`**: `jabatan`, `tkk`, `beras`, `air` — dipetakan ke integer 0–3 melalui dict `JENIS_TUNJANGAN_CODES`
- **Distinct `ref_type` (level_id)**: `1`, `2`
- **Total data**: Hanya **63 baris** — dataset sangat kecil
- **Mapping `level_id`**: Jika `level_id == 1` dan `golongan_id == 4` → menjadi `5`; jika `golongan_id == 5` → menjadi `6`; selainnya → `7`
- **Mapping `golongan_id`**: Jika `level_id` hasil transformasi bernilai `5` atau `6`, maka `golongan_id` diubah menjadi `-1`

### Target: `kepegawaian_migrasi.gaji_tunjangan`

Kolom inti yang dipetakan: `id`, `jenis_tunjangan`, `level_id`, `golongan_id`, `nominal`.

---

## 2. Identifikasi Bug & Potensi Masalah

Berdasarkan penelusuran kode dan analisis performa, ditemukan beberapa kelemahan pada modul saat ini:

### Bug 1 — Penggunaan `dask.dataframe` yang Tidak Proporsional (Overhead Performa)

Fungsi `cleanup_salary_allowance()` menggunakan `dask.dataframe` untuk memproses data yang hanya berjumlah **63 baris**. Pipeline Dask yang diterapkan:
1. Konversi Pandas DataFrame ke Dask DataFrame dengan 4 partisi (`dd.from_pandas(df, npartitions=4)`)
2. Eksekusi `map_partitions()` pada setiap partisi
3. Pemanggilan `compute()` untuk mengonversi kembali ke Pandas DataFrame

Hal ini **sangat tidak proporsional** karena:
- Overhead pembuatan partisi, serialisasi data, dan penjadwalan _task_ Dask jauh **melebihi** waktu komputasi aktual untuk 63 baris
- Fungsi `_transform_partition()` yang dipanggil di dalamnya **sudah menggunakan operasi _vectorized_ Pandas dan NumPy** (`np.where`, `.map()`, `.fillna()`, `.astype()`) yang merupakan _best practice_ menurut dokumentasi resmi Pandas melalui **Context 7**
- Dask menambahkan dependensi _library_ yang berat ke proyek (±14 paket transitif: `dask`, `distributed`, `cloudpickle`, `fsspec`, `locket`, `msgpack`, `partd`, dll.)

**Referensi Context 7**: Dokumentasi Pandas menyatakan bahwa operasi _vectorized_ langsung pada DataFrame signifikan lebih cepat dibandingkan `apply()` maupun framework paralel untuk dataset kecil. Pemanggilan langsung fungsi transformasi tanpa Dask adalah pendekatan yang tepat.

### Bug 2 — Tidak Ada Guard untuk DataFrame Kosong

Fungsi `cleanup_salary_allowance()` tidak memiliki pengecekan atau mekanisme _early exit_ ketika menerima DataFrame kosong. Jika DataFrame kosong diteruskan, pipeline Dask tetap dieksekusi (membuat partisi kosong, memanggil `compute()`) tanpa menghasilkan data apapun — membuang sumber daya komputasi.

### Bug 3 — Tidak Ada _Error Handling_ pada Fungsi Cleanup

Fungsi `cleanup_salary_allowance()` tidak memiliki blok `try-except`. Jika terjadi error pada proses transformasi (misalnya tipe data tidak sesuai atau kolom tidak ditemukan), program akan berhenti secara paksa tanpa notifikasi _logging_ yang terstruktur.

### Bug 4 — Tidak Ada _Logging_ Jumlah Record setelah Cleanup

Fungsi `cleanup_salary_allowance()` tidak mencatat berapa banyak record yang berhasil ditransformasi. Hal ini menyulitkan verifikasi dan pemantauan proses migrasi, tidak konsisten dengan pola _logging_ yang sudah diterapkan di fungsi-fungsi lain pada `v2_master_gaji.py`.

---

## 3. Rekomendasi Perbaikan (Bug Fixes)

Berikut adalah tahap mitigasi teknis untuk kendala di atas:

1. **Hapus Dependensi Dask Sepenuhnya dari `eo_salary_allowance.py`**: Hapus baris `import dask.dataframe as dd`. Ganti seluruh pipeline Dask di dalam fungsi `cleanup_salary_allowance()` (yaitu `dd.from_pandas`, `map_partitions`, dan `compute()`) dengan pemanggilan langsung fungsi `_transform_partition(df)`. Fungsi tersebut sudah menerima `pd.DataFrame` dan mengembalikan `pd.DataFrame` dengan operasi _vectorized_. Pertahankan baris sanitisasi `df.replace({np.nan: None, pd.NaT: None, pd.NA: None})` setelah pemanggilan transformasi.

2. **Tambahkan Guard DataFrame Kosong**: Sisipkan mekanisme _early exit_ di awal fungsi `cleanup_salary_allowance()` yang mengembalikan DataFrame kosong jika input tidak memiliki baris data. Ikuti pola yang sudah ada di modul lain seperti `kepeg_potongan_tkk.py`.

3. **Tambahkan _Error Handling_ Terstruktur**: Bungkus logika transformasi di dalam `cleanup_salary_allowance()` dengan blok `try-except` yang mencatat error menggunakan `LOGGER.error()` dan melakukan _re-raise_ agar caller (`v2_master_gaji.py`) dapat menangkap kegagalan. Import `LOGGER` dari `core.config` jika belum tersedia.

4. **Tambahkan _Logging_ Record Count**: Tambahkan pesan _log_ yang mencatat jumlah baris sebelum dan/atau sesudah proses cleanup menggunakan `LOGGER.info()`, konsisten dengan pola _logging_ pada `v2_master_gaji.py`.

---

## 4. Rekomendasi Optimasi Performa & Kerapian Kode

1. **Pemanggilan Langsung Fungsi Transformasi _Vectorized_**: Karena `_transform_partition()` sudah menggunakan operasi _vectorized_ (`np.where`, `Series.map()`, `.fillna()`, `.astype()`), pemanggilan langsung tanpa Dask akan menghasilkan performa yang **lebih cepat** untuk dataset 63 baris ini. Ini sesuai dengan _best practice_ Pandas yang divalidasi melalui **Context 7**.

2. **Pertimbangkan Rename Fungsi `_transform_partition`**: Setelah Dask dihapus, nama `_transform_partition` tidak lagi akurat karena fungsi tersebut tidak lagi memproses partisi. Pertimbangkan untuk mengganti nama menjadi `_transform_salary_allowance` demi kejelasan kode. Ini bersifat opsional.

3. **Konsistensi Pola Fetch dengan Modul Lain**: Fungsi `fetch_salary_allowance()` menggunakan _manual cursor_ (`get_smartoffice_connection_pool()` → `cursor.execute()`), sedangkan modul sumber lainnya seperti `eo_salary_non_taxable_income.py` menggunakan fungsi generik `fetch_smartoffice(query)` dari `core/config.py`. Pertimbangkan untuk menyeragamkan pola fetch menggunakan fungsi generik tersebut agar lebih konsisten dan mudah dipelihara. Ini bersifat opsional dan di luar lingkup utama issue ini.

---

## 5. Langkah-Langkah Pengerjaan

Dokumen ini disusun sebagai instrumen _checklist_. Pedomani runtutan _step_ teknis berikut saat proses _fixing_ modul ini:

- [ ] **Aktivasi Environment & Referensi**: Posisikan di direktori _root_ proyek dan jalankan environment melalui `./.venv/bin/python`. Selalu panggil rujukan berbasis **Context 7** untuk memvalidasi _best practice_ Pandas terkini — gunakan query _"Pandas vectorized operations replace apply numpy where"_ dan _"Pandas DataFrame map replace Dask best practice"_ untuk mendapatkan referensi terbaru. Baca juga file `memory/project_bug_patterns.md` untuk memahami pola bug standar proyek.

- [ ] **Penghapusan Dask dari `cleanup_salary_allowance()` (`core/smartoffice/eo_salary_allowance.py`)**: Hapus baris `import dask.dataframe as dd` dari bagian import. Di dalam fungsi `cleanup_salary_allowance()`, hapus seluruh blok kode yang melibatkan `dd.from_pandas()`, `ddf.map_partitions()`, dan `ddf.compute()`. Gantikan dengan pemanggilan langsung fungsi `_transform_partition(df)` yang sudah ada. Pastikan baris sanitisasi (`df.replace(...)`) tetap dipertahankan setelah pemanggilan transformasi. Validasi bahwa `import numpy as np` dan `import pandas as pd` tetap tersedia karena masih digunakan oleh fungsi transformasi dan sanitisasi.

- [ ] **Penambahan Guard DataFrame Kosong (`core/smartoffice/eo_salary_allowance.py`)**: Tambahkan pengecekan `if df.empty` di awal fungsi `cleanup_salary_allowance()` yang langsung mengembalikan DataFrame kosong. Hal ini mencegah eksekusi transformasi yang sia-sia dan konsisten dengan pola _early exit_ di modul lain.

- [ ] **Penambahan _Error Handling_ dan _Logging_ (`core/smartoffice/eo_salary_allowance.py`)**: Tambahkan blok `try-except` pada fungsi `cleanup_salary_allowance()` dengan _logging_ error yang terstruktur menggunakan `LOGGER` dari `core.config`. Tambahkan juga _logging_ jumlah record yang berhasil ditransformasi. Rujuk pola _error handling_ yang sudah diterapkan di `v2_master_gaji.py` (blok `try-except` pada fungsi `main()`).

- [ ] **Opsional: Rename Fungsi `_transform_partition`**: Jika memungkinkan, ubah nama fungsi menjadi `_transform_salary_allowance` untuk meningkatkan kejelasan kode. Pastikan semua referensi internal di file yang sama diperbarui.

- [ ] **Testing dan Validasi Terminal**: Uji finalisasi script dengan menjalankan `./.venv/bin/python -m v2.v2_master_gaji`. Pantau kemunculan log berikut:
  - Jumlah record yang berhasil di-fetch (`Fetched N salary allowances`)
  - Jumlah record yang berhasil di-cleanup (log baru yang ditambahkan)
  - Durasi eksekusi (`log_duration` sudah tersedia di `v2_master_gaji.py`)
  - Tidak ada error atau _traceback_ terkait Dask
  - Pastikan data yang tersimpan di tabel target `gaji_tunjangan` tetap **identik** dengan hasil sebelumnya (63 baris, mapping `jenis_tunjangan`, `level_id`, `golongan_id` sesuai dengan tabel referensi di atas)
  - Jalankan juga test suite jika tersedia: `./.venv/bin/python -m pytest tests/test_master.py`
