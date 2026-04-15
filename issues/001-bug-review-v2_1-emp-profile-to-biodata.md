# Issue #001: Review Bug & Perbaikan v2_1.emp_profile_to_biodata.py

## Latar Belakang

File `v2/v2_1.emp_profile_to_biodata.py` adalah script migrasi tahap pertama yang mengkonversi data `emp_profile` dari database smartoffice ke tabel `biodata` di database kepegawaian. Script ini juga menyimpan data kartu identitas awal dari NIK.

Ditemukan beberapa potensi bug dan kelemahan yang perlu ditinjau dan diperbaiki agar proses migrasi data berjalan lebih andal dan konsisten.

---

## Daftar Temuan Bug / Potensi Masalah

### Bug 1: Data Duplikat Akibat GROUP BY Tanpa Agregasi

**Masalah:** Query SQL di `core/smartoffice/emp_profile.py` menggunakan `GROUP BY ep.emp_profile_id`, tetapi ada kolom-kolom dari tabel lain (seperti `ref_edu.text`, `em.emp_flag`) yang tidak diagregasi. Ini bisa menghasilkan data yang tidak konsisten karena MySQL akan mengambil nilai acak dari baris yang di-group.

**Dampak:** Nilai `pendidikanTerakhir` dan `emp_flag` bisa salah untuk pegawai yang memiliki lebih dari satu record pendidikan atau relasi employee.

**File terkait:** `core/smartoffice/emp_profile.py`

### Bug 2: Tidak Ada Penanganan Data Kosong (Empty DataFrame)

**Masalah:** Fungsi `main()` dan `transform_biodata()` tidak memeriksa apakah DataFrame yang dihasilkan kosong. Jika query mengembalikan 0 baris, operasi transformasi dan penyimpanan tetap dijalankan tanpa perlu.

**Dampak:** Proses berjalan sia-sia dan berpotensi error pada operasi DataFrame yang mengasumsikan data ada.

**File terkait:** `v2/v2_1.emp_profile_to_biodata.py`

### Bug 3: Kolom `emp_flag` Bisa NULL

**Masalah:** JOIN ke tabel `employee` menggunakan `LEFT JOIN`, sehingga kolom `emp_flag` bisa bernilai `NULL` jika tidak ada record employee yang cocok. Kemudian `df["is_pegawai"] = df["emp_flag"].ne(0)` akan menghasilkan `True` untuk NULL (karena NULL != 0 adalah True di Pandas).

**Dampak:** Orang yang bukan pegawai (tidak punya record employee) justru ditandai sebagai `is_pegawai = True`.

**File terkait:** `v2/v2_1.emp_profile_to_biodata.py` (baris 45)

### Bug 4: Mapping `pendidikan_id` Lambat Karena Iterasi Per-Baris

**Masalah:** Fungsi `get_jenjang_pendidikan_id()` dipanggil per baris menggunakan `.apply()` dengan operasi `DataFrame.query()` di dalamnya. Ini sangat lambat untuk dataset besar.

**Dampak:** Performa buruk pada volume data tinggi. Seharusnya menggunakan operasi merge/join DataFrame.

**File terkait:** `v2/v2_1.emp_profile_to_biodata.py` (baris 39-41, 50-55)

### Bug 5: Tidak Ada Error Handling di Fungsi `main()`

**Masalah:** Fungsi `main()` tidak memiliki try-except. Jika terjadi error di tengah proses (misalnya koneksi database putus), tidak ada logging error yang informatif dan proses langsung crash.

**Dampak:** Sulit melakukan debugging saat terjadi kegagalan di production.

**File terkait:** `v2/v2_1.emp_profile_to_biodata.py` (baris 14-18)

### Bug 6: Tipe Data `is_deleted` Tidak Konsisten

**Masalah:** Di SQL, `is_deleted` dihasilkan sebagai `IF(ep.emp_status=3,TRUE,FALSE)` yang menghasilkan integer 1/0. Kemudian di Python dikonversi ke boolean dengan `df["is_deleted"].eq(1)`. Namun saat disimpan ke database, boolean Python bisa diinterpretasi berbeda tergantung driver MySQL.

**Dampak:** Nilai `is_deleted` di tabel target bisa tidak sesuai ekspektasi.

**File terkait:** `v2/v2_1.emp_profile_to_biodata.py` (baris 44), `core/smartoffice/emp_profile.py`

---

## Langkah-Langkah Pengerjaan

### Tahap 1: Persiapan dan Pemahaman Kode

1. Baca dan pahami alur kerja file `v2/v2_1.emp_profile_to_biodata.py` dari awal sampai akhir.
2. Baca file pendukung:
   - `core/smartoffice/emp_profile.py` (sumber data)
   - `core/kepegawaian/kepeg_biodata.py` (penyimpanan biodata)
   - `core/kepegawaian/kepeg_kartu_identitas.py` (penyimpanan kartu identitas)
   - `v2/v2_helper.py` (fungsi utilitas)
3. Pahami struktur tabel sumber (`emp_profile`, `employee`, `emp_education`, `sys_reference`) dan tabel target (`biodata`, `kartu_identitas`).

### Tahap 2: Perbaikan Query SQL (Bug 1)

1. Buka `core/smartoffice/emp_profile.py`.
2. Perbaiki query agar kolom yang di-select dari tabel JOIN menggunakan fungsi agregasi (misalnya `MAX()` atau `MIN()`), atau hilangkan `GROUP BY` dan gunakan subquery/window function untuk menghindari duplikasi.
3. Pastikan setiap `emp_profile_id` hanya menghasilkan 1 baris data.
4. **Referensi:** Gunakan Context7 untuk mencari best practice penulisan query SQL dengan GROUP BY:
   ```bash
   npx ctx7@latest library mysql "GROUP BY with non-aggregated columns best practice"
   npx ctx7@latest docs <libraryId> "GROUP BY with non-aggregated columns"
   ```

### Tahap 3: Perbaikan Penanganan NULL pada `emp_flag` (Bug 3)

1. Buka `v2/v2_1.emp_profile_to_biodata.py`.
2. Sebelum baris `df["is_pegawai"] = df["emp_flag"].ne(0)`, tambahkan penanganan NULL:
   - Isi nilai NULL pada kolom `emp_flag` dengan 0 terlebih dahulu.
   - Baru kemudian lakukan perbandingan `ne(0)`.
3. **Referensi:** Gunakan Context7 untuk mencari cara handling NULL di Pandas:
   ```bash
   npx ctx7@latest library pandas "fillna handle missing values"
   npx ctx7@latest docs <libraryId> "fillna handle NaN None values"
   ```

### Tahap 4: Optimasi Mapping `pendidikan_id` (Bug 4)

1. Buka `v2/v2_1.emp_profile_to_biodata.py`.
2. Ganti pendekatan `.apply()` + `DataFrame.query()` per baris dengan operasi `pd.merge()` atau `df.map()` menggunakan dictionary lookup.
3. Buat dictionary mapping dari `jenjang_pendidikan_df` lalu gunakan `Series.map()`.
4. Jangan lupa handle kasus tidak ditemukan (default ke `DEFAULT_ID = 0`).
5. **Referensi:** Gunakan Context7 untuk mencari best practice mapping data di Pandas:
   ```bash
   npx ctx7@latest library pandas "merge map replace values efficiently"
   npx ctx7@latest docs <libraryId> "Series.map dictionary lookup with default value"
   ```

### Tahap 5: Penanganan DataFrame Kosong dan Error Handling (Bug 2 & 5)

1. Di fungsi `main()`, tambahkan pengecekan apakah DataFrame kosong sebelum melanjutkan proses transformasi dan penyimpanan.
2. Bungkus proses utama dengan try-except dan logging error yang informatif menggunakan `LOGGER` yang sudah tersedia dari `core.config`.
3. Pastikan jika terjadi error, pesan error mencantumkan konteks yang jelas (tahap mana yang gagal).

### Tahap 6: Konsistensi Tipe Data `is_deleted` (Bug 6)

1. Pastikan nilai `is_deleted` yang disimpan ke database adalah tipe integer (0 atau 1), bukan boolean Python.
2. Konversi eksplisit ke integer setelah operasi `.eq(1)` menggunakan `.astype(int)`.
3. Lakukan hal yang sama untuk kolom `is_pegawai`.

### Tahap 7: Pengujian

1. Jalankan test yang sudah ada:
   ```bash
   python -m pytest tests/ -v
   ```
2. Jalankan script secara manual dengan sample data kecil untuk memverifikasi perubahan:
   ```bash
   python -m v2.v2_1.emp_profile_to_biodata
   ```
3. Periksa data hasil migrasi di tabel `biodata` dan `kartu_identitas` untuk memastikan:
   - Tidak ada duplikasi
   - Nilai `is_pegawai` benar untuk yang punya dan tidak punya record employee
   - Nilai `pendidikan_id` cocok dengan master `jenjang_pendidikan`
   - Nilai `is_deleted` tersimpan sebagai 0 atau 1

---

## Prioritas Perbaikan

| Prioritas | Bug | Alasan |
|-----------|-----|--------|
| **Tinggi** | Bug 1 (GROUP BY) | Menyebabkan data salah secara silent |
| **Tinggi** | Bug 3 (NULL emp_flag) | Menghasilkan status pegawai yang salah |
| **Sedang** | Bug 6 (tipe is_deleted) | Inkonsistensi data di database target |
| **Sedang** | Bug 4 (performa mapping) | Lambat tapi hasil tetap benar |
| **Rendah** | Bug 2 (DataFrame kosong) | Edge case, jarang terjadi |
| **Rendah** | Bug 5 (error handling) | Tidak mengubah hasil, hanya memperbaiki debugging |

---

## Catatan Penting

- Selalu backup database target sebelum menjalankan script migrasi yang sudah diperbaiki.
- Uji perubahan di environment development terlebih dahulu, jangan langsung di production.
- Gunakan `icecream` (`ic()`) untuk debugging selama pengembangan, hapus sebelum commit final.
- Jika ragu dengan perubahan query SQL, konsultasikan ke senior developer terlebih dahulu.
