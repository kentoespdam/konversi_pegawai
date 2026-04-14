# Plan Audit, Perbaikan, dan Optimasi: `v2_8_emp_family_to_profil_keluarga.py`

Dokumen ini disusun sebagai panduan bagi **Junior Developer atau AI Model** untuk memperbaiki dan mengoptimalkan script migrasi `v2_8_emp_family_to_profil_keluarga.py` beserta pustaka pendukungnya:
- `core/smartoffice/emp_family.py` — query fetch data sumber
- `core/kepegawaian/kepeg_profil_keluarga.py` — query INSERT ke tabel target

Sesuai pedoman pengerjaan, **wajib menggunakan Context 7** saat mengimplementasikan langkah-langkah di bawah ini untuk memastikan _best practice_ penulisan kode Python, penanganan exception, standar pemrosesan Pandas, dan query SQL. Selalu jalankan environment menggunakan Python dari dalam `.venv`.

---

## 1. Identifikasi Bug & Potensi Masalah

Berdasarkan penelusuran kode dan inspeksi skema tabel target `profil_keluarga` di database `kepegawaian_migrasi`, ditemukan sejumlah kelemahan signifikan:

### Bug 1 — Kolom `version` Tidak Ada di Tabel Target

Fungsi `save_profil_keluarga_from_emp_profile` di `kepeg_profil_keluarga.py` menyisipkan nilai _hardcoded_ `version = 0` (posisi ke-13 dalam tuple data) ke dalam query INSERT, padahal tabel `profil_keluarga` **tidak memiliki kolom `version`**. Hal ini menyebabkan SQL Error setiap kali skrip dieksekusi karena jumlah kolom dan nilai tidak sesuai.

### Bug 2 — Kolom `nik` dan `pendidikan_id` Tidak Diisi

Tabel `profil_keluarga` memiliki kolom `nik` dan `pendidikan_id` yang tidak diisi sama sekali oleh fungsi save. Query INSERT tidak mencantumkan kolom ini, sehingga data anggota keluarga tidak akan memiliki `nik` dan relasi ke tabel pendidikan tidak terbentuk.

### Bug 3 — Idempotency Rusak (`ON DUPLICATE KEY UPDATE` Tidak Efektif)

Tabel `profil_keluarga` tidak memiliki _Unique Key_ selain Primary Key auto-increment `id`. Artinya, klausul `ON DUPLICATE KEY UPDATE` **tidak akan pernah terpicu**, dan setiap kali script dijalankan ulang akan menghasilkan **baris duplikat**. Diperlukan strategi idempotency yang nyata, misalnya TRUNCATE sebelum INSERT atau penambahan _Unique Constraint_ di tabel.

### Bug 4 — Redundansi Kolom `biodata_id` di Klausul UPDATE

Klausul `ON DUPLICATE KEY UPDATE` menyertakan pembaruan `biodata_id=VALUES(biodata_id)`, padahal `biodata_id` adalah kolom identifikasi yang tidak perlu diperbarui. Ini redundan dan berpotensi menimpa data secara tidak sengaja.

### Bug 5 — Kolom `updated_at` Tidak Diperbarui di Klausul UPDATE

Klausul `ON DUPLICATE KEY UPDATE` tidak menyertakan `updated_at=CURRENT_TIMESTAMP`, sehingga waktu perubahan terakhir tidak tercatat. Ini tidak konsisten dengan modul migrasi lain (`kepeg_pelatihan.py`, `kepeg_pendidikan.py`) yang sudah menyertakannya.

### Bug 6 — Mapping `CORE_RELATION_IDS` Menggunakan Literal Int, Bukan Enum

Di `v2_8_emp_family_to_profil_keluarga.py`, variabel `CORE_RELATION_IDS` didefinisikan sebagai set nilai integer `{0, 1, 2, 3}`:
```python
CORE_RELATION_IDS = {EHubunganKeluarga.SUAMI.value, EHubunganKeluarga.ISTRI.value, ...}
```
Ini secara teknis benar karena mengambil `.value`, namun fungsi `_cleanup_status_kawin_vectorized` kemudian menggunakan `hubungan_keluarga.isin(CORE_RELATION_IDS)`. Perlu dipastikan bahwa nilai `hubungan_keluarga` hasil fetch (setelah `-1` offset) memang berpadanan dengan integer 0–3 dari Enum tersebut.

### Bug 7 — Potensi Nilai Negatif pada `status_pendidikan` dan `status_kawin`

Di query fetch `emp_family.py`, nilai dihitung dengan formula:
- `fam_pendidikan - 1 AS status_pendidikan` → Jika `fam_pendidikan = 0` (ada di data: MIN=0), hasilnya adalah **-1**.
- `fam_sts_nikah - 1 AS status_kawin` → Jika `fam_sts_nikah = 0` (ada di data: MIN=0), hasilnya adalah **-1**.

Nilai -1 adalah nilai tidak valid dan tidak terdapat di domain tabel target. Logika cleanup di v2_8 memang menangani `mask_invalid = status_pendidikan.eq(-1)`, namun logika cleanup `status_kawin` memiliki celah: baris terakhir `result.loc[status_kawin.eq(-1)] = 1` akan **menimpa semua baris** yang memiliki `status_kawin = -1` termasuk yang sudah ditangani sebelumnya (mask_anak), karena tidak ada filter tambahan. Urutan operasi masking ini perlu diperiksa ulang.

### Bug 8 — Tidak Ada Pengecekan DataFrame Kosong

Script utama tidak memeriksa apakah `family_df` kosong setelah fungsi fetch. Jika sumber data kosong, operasi pada `transform_family_df` akan tetap dipanggil dan fungsi save akan mengeksekusi query yang sia-sia.

### Bug 9 — Tidak Ada Error Handling (Try-Except)

Tidak ada satu pun blok `try-except` di seluruh alur, mulai dari fetch, transform, hingga save. Satu error koneksi database atau tipe data yang tidak sesuai akan menghentikan program secara paksa tanpa notifikasi yang terstruktur.

### Bug 10 — Tidak Ada Logging Jumlah Record

Script tidak mencatat berapa banyak record yang berhasil di-fetch dan di-save. Hal ini menyulitkan verifikasi dan pemantauan proses migrasi.

### Bug 11 — Nilai `agama` Hard-coded Tanpa Penjelasan Domain

Kolom `agama` dikunci ke nilai `1` untuk semua record. Perlu dipastikan nilai `1` ini memang merupakan representasi default yang valid dalam tabel referensi agama di sistem kepegawaian, atau apakah perlu diambil dari data sumber.

### Bug 12 — Penanganan Nilai NaN/NaT Pandas Sebelum Iterasi

Data `tanggal_lahir` yang tidak valid akan menjadi `None` setelah `format_date_series`, namun kolom lain yang mungkin bernilai `NaN` (float Pandas) atau `NaT` (datetime Pandas) tidak dibersihkan secara global sebelum `itertuples()`. Driver MySQL Python dapat mengalami masalah saat memproses tipe `NaN` atau `NaT` dibandingkan `None`.

---

## 2. Rekomendasi Perbaikan (Bug Fixes)

1. **Hapus Kolom `version` dari Query INSERT**: Buang kolom `version` dan nilai _hardcoded_ `0` dari daftar kolom INSERT dan dari tuple data di `kepeg_profil_keluarga.py`.

2. **Tambahkan Kolom `nik` ke INSERT**: Sertakan kolom `nik` ke dalam query INSERT. Nilai `nik` dapat diisi dengan `None` (karena tidak tersedia di sumber) atau dikosongkan dengan nilai default, konsisten dengan kebutuhan sistem target.

3. **Perbaiki Strategi Idempotency**: Karena tabel tidak memiliki _Unique Key_, terapkan strategi **TRUNCATE sebelum INSERT** di awal fungsi save untuk mencegah duplikasi data saat script dijalankan ulang. Alternatifnya, koordinasikan dengan DBA untuk menambahkan _Unique Constraint_ pada kombinasi kolom yang relevan.

4. **Perbaiki Klausul `ON DUPLICATE KEY UPDATE`**: Hapus entri redundan `biodata_id=VALUES(biodata_id)` dari klausul update, dan tambahkan `updated_at=CURRENT_TIMESTAMP` di akhir daftar.

5. **Perbaiki Urutan Masking `status_kawin`**: Periksa ulang urutan kondisi masking di `_cleanup_status_kawin_vectorized`. Baris `result.loc[status_kawin.eq(-1)] = 1` harus diberi filter tambahan `& ~mask_anak` agar tidak menimpa nilai yang sudah diset sebelumnya pada baris anak.

6. **Validasi Range Nilai Fetch**: Pastikan bahwa formula `-1` pada query fetch (`fam_pendidikan - 1`, `fam_sts_nikah - 1`, `rh.value - 1`) menghasilkan nilai yang valid untuk domain tabel target. Pertimbangkan penanganan nilai 0 di sumber (yang menjadi -1 setelah offset) secara eksplisit di query SQL (misalnya menggunakan `GREATEST(fam_pendidikan - 1, 0)`) atau di fungsi cleanup Python.

7. **Tambahkan Pengecekan DataFrame Kosong**: Di fungsi `main()`, tambahkan pemeriksaan `if family_df.empty: return` setelah fetch, disertai logging yang memadai.

8. **Implementasikan Error Handling Global**: Bungkus seluruh alur di fungsi `main()` dengan blok `try-except` yang mencatat pesan error dan stack trace ke logger, sehingga kegagalan tidak menghentikan program secara tiba-tiba.

9. **Tambahkan Logging Jumlah Record**: Tambahkan logging jumlah baris setelah fetch dan konfirmasi setelah save, contohnya: `LOGGER.info(f"Fetched {len(family_df)} records")`.

10. **Sanitasi Nilai NaN/NaT Global**: Sebelum DataFrame dikembalikan dari `transform_family_df`, lakukan replace nilai null Pandas (`NaN`, `NaT`, `pd.NA`) ke `None` secara global menggunakan `df.where(df.notna(), other=None)` atau `df.replace({float('nan'): None})`, agar tidak ada masalah saat `itertuples()` di fungsi save.

---

## 3. Rekomendasi Optimasi Performa & Kerapian Kode

1. **Konsistensi Pola dengan Modul v2_5 – v2_7**: Pastikan struktur skrip (import, inisialisasi `LOGGER`, try-except di `main`, empty check, record count logging, NaN sanitization) mengikuti pola yang sudah diterapkan pada modul v2_5, v2_6, dan v2_7 agar seluruh pipeline migrasi seragam.

2. **Dokumentasi Docstring pada `transform_family_df`**: Pindahkan docstring dari posisi setelah `result_df = df.copy()` ke langsung di bawah deklarasi fungsi. Saat ini posisi docstring salah (bukan string pertama fungsi), sehingga tidak dikenali sebagai docstring resmi oleh Python.

3. **Penggunaan Enum untuk Masking**: Pertimbangkan menggunakan nilai `EHubunganKeluarga.ANAK.value` secara eksplisit di `_cleanup_status_kawin_vectorized` alih-alih literal `4`, agar kode lebih mudah dibaca dan dipelihara.

4. **Pemurnian Transformasi Data**: Konfirmasikan seluruh manipulasi data diselesaikan melalui operasi _vectorized_ Pandas demi performa terbaik. Hindari penggunaan `apply()` dengan lambda jika ada alternatif _vectorized_ yang tersedia.

5. **Standarisasi Import**: Tambahkan import `logging`, `numpy` (jika diperlukan untuk sanitasi NaN), dan pastikan semua import sudah terurut dan tidak ada yang tidak terpakai (_unused imports_).

---

## 4. Langkah-Langkah Pengerjaan

Dokumen ini disusun sebagai instrumen _checklist_. Ikuti urutan langkah berikut secara sistematis:

- [ ] **Aktivasi Environment & Referensi Dokumentasi**
  - Posisikan di direktori _root_ proyek dan aktifkan virtual environment:
    ```bash
    source .venv/bin/activate
    ```
  - Gunakan **Context 7** untuk memverifikasi _best practice_ Pandas, penanganan exception Python, dan query SQL MySQL sebelum mengimplementasikan perubahan.

- [ ] **Perbaikan Query Fetch Sumber (`core/smartoffice/emp_family.py`)**
  - Periksa apakah formula `rh.value - 1`, `fam_pendidikan - 1`, dan `fam_sts_nikah - 1` sudah menghasilkan range nilai yang valid (tidak negatif).
  - Pertimbangkan menambahkan klausa `WHERE ep.emp_identity_number IS NOT NULL` untuk menghindari data dengan `biodata_id` NULL yang akan gagal di INSERT karena mungkin ada FK constraint.
  - Periksa kebutuhan kolom `nik` apakah bisa diambil dari tabel sumber atau diisi `NULL`.

- [ ] **Perbaikan Fungsi Save Target (`core/kepegawaian/kepeg_profil_keluarga.py`)**
  - Hapus kolom `version` (posisi ke-13) dan nilai `0` dari tuple data dan dari daftar kolom INSERT.
  - Tambahkan kolom `nik` ke daftar INSERT (isi dengan `None` jika tidak tersedia di sumber, atau ambil dari data jika tersedia).
  - Perbaiki klausul `ON DUPLICATE KEY UPDATE`: hapus `biodata_id=VALUES(biodata_id)`, tambahkan `updated_at=CURRENT_TIMESTAMP`.
  - Tambahkan `TRUNCATE TABLE profil_keluarga` di awal fungsi save (sebelum `executemany`) untuk menjamin idempotency selama tabel belum memiliki _Unique Key_.

- [ ] **Perbaikan Logika Transformasi (`v2/v2_8_emp_family_to_profil_keluarga.py`)**
  - Perbaiki posisi docstring di `transform_family_df` agar berada langsung setelah `def transform_family_df(...)`.
  - Perbaiki logika di `_cleanup_status_kawin_vectorized`: tambahkan filter `& ~mask_anak` pada baris terakhir (`result.loc[status_kawin.eq(-1)] = 1`) agar tidak menimpa nilai yang sudah diset untuk baris anak.
  - Tambahkan sanitasi nilai NaN/NaT global di akhir `transform_family_df` sebelum `return result_df`.

- [ ] **Pengaman dan Logging (`v2/v2_8_emp_family_to_profil_keluarga.py`)**
  - Tambahkan import yang diperlukan: `logging`, dan modul lain jika dibutuhkan.
  - Inisialisasi `LOGGER` menggunakan `from core.config import LOGGER` (jika belum ada).
  - Tambahkan pemeriksaan `if family_df.empty` setelah fetch dengan logging yang informatif.
  - Tambahkan logging jumlah record setelah fetch: `LOGGER.info(f"Fetched {len(family_df)} records")`.
  - Bungkus seluruh alur di `main()` dalam blok `try-except Exception` yang mencatat error ke logger beserta stack trace.

- [ ] **Testing dan Verifikasi**
  - Jalankan script dengan perintah:
    ```bash
    python -m v2.v2_8_emp_family_to_profil_keluarga
    ```
  - Pantau output log: pastikan muncul log durasi waktu dan jumlah record yang di-fetch.
  - Pastikan tidak ada `SQL Error`, `RuntimeError`, atau `KeyError` di console.
  - Verifikasi data di tabel target:
    ```sql
    SELECT COUNT(*), COUNT(nik), COUNT(biodata_id) FROM profil_keluarga;
    ```
  - Jalankan script **kedua kalinya** dan pastikan tidak ada duplikasi baris (idempotency terjaga).
  - Periksa beberapa record sampel untuk memvalidasi nilai `hubungan_keluarga`, `status_pendidikan`, `status_kawin`, dan `tanggungan` sudah sesuai.
