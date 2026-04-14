# Plan Migrasi v2.16 - Cuti Approval

## 1. Objektif
Dokumen ini menjadi panduan tingkat tinggi (high-level) bagi AI model kecil atau junior developer untuk melakukan inspeksi, perbaikan bug, dan optimisasi pada proses migrasi `v2_16_cuti_approval.py`.

## 2. Praktik Terbaik Code & Environment
1. **Environment:** Gunakan spesifik python executable dari environment project yaitu `./.venv/bin/python`.
2. **Context 7 Context:** Mengacu pada dokumentasi Context 7 untuk memvalidasi *best practices* Python terkini. Lakukan optimasi penggunaan operasi Pandas yang efisien (menuju pada operasi vektor) dan penghindaran loop standar jika tidak terpaksa, penyamaan manajemen nilai kosong (`None` vs `NaN`), dan *exception handling* yang andal atas tiap transaksi basis data.

## 3. Contoh Value Database
Untuk menghindari kewajiban interogasi ulang ke database saat pengerjaan skrip, berikut snapshot sample data dari basis data master saat ini:

**Tabel Asal: `smartoffice.cuti_pegawai_approval`**
| cpa_id | cp_id | ... | cpa_approval_level | cpa_note |
|---|---|---|---|---|
| 6 | 2 | ... | 1 | |
| 7 | 2 | ... | 2 | NULL |
| 8 | 2 | ... | 3 | NULL |

*Detail sebaran status `cpa_approval_status` pada master database (`smartoffice`):*
- Status 0: 66 rows
- Status 1: 12 rows
- Status 2: 4048 rows
- Status 4: 120 rows
- Status 5: 59 rows
- Status 6: 55 rows

**Tabel Tujuan: `kepegawaian_migrasi.cuti_approval`**
| id | created_at | cuti_pegawai_id | jabatan_id |
|---|---|---|---|
| 6 | 2019-01-28 10:45:21 | 2 | 48 |
| 11 | 2019-01-22 09:53:40 | 3 | 9 |

**Tabel Tujuan: `kepegawaian_migrasi.cuti_approval_chain`**
| id | approval_level | read_write_status | ref_cuti_id |
|---|---|---|---|
| 1 | 1 | 1 | 2 |
| 2 | 2 | 1 | 2 |

## 4. Identifikasi Bug dan Rekomendasi Perbaikan
Terdapat beberapa anomali dan resiko yang ditemui pada baris instruksi asal. Lakukan penanganan secara komprehensif pada pengerjaannya nanti:
1. **Pengecekan Kekosongan Data (Empty DataFrame Checks):** Validasi `df.empty` belum hadir di skrip utama atau rutin `save_cuti_approval`/`update_approval_chain`. Tambahkan perlindungan `if df.empty: return` guna memastikan bahwa saat filter mengeliminasi semua baris, loop `itertuples()` atau *db execution* tidak menimbulkan *exception*.
2. **Potensi Kesalahan Integritas `v2_16` (`cpa_approval_status - 1`):** Saat query data dari smartoffice berjalan, ada pemutakhiran ekspresi `(cpa.cpa_approval_status - 1)`. Tinjau poin di atas bahwa ada total 66 row di database yang berstatus `0`. Bila dieksekusi akan menghasilkan `-1`. Pelajari apakah field *kepegawaian_migrasi* (*target*) menerima `-1` sebagai entri yang sah, atau akan error apabila menggunakan integer *unsigned*. Rancang pemetaan alternatif bila terlarang.
3. **Kelemahan Kriteria Spesifik UPDATE Klausa WHERE:** Logika modifikasi ke tabel `cuti_approval_chain` saat ini hanya difilter oleh kriteria identitas `ref_cuti_id` dan `jabatan_id`. Apabila satu personil (satu jabatan) mengisi lebih dari satu titik permohonan (*approval_level*), instruksi ini berpotensi membahayakan riwayat dengan *over-writing* status tingkat level sebelum/sesudahnya. Rekomendasi: evaluasi inklusi field `approval_level` di argumen pencarian/WHERE.
4. **Resiko Data Terpangkas oleh `INNER JOIN`:** Relasi antar tabel master di query `fetch_cuti_approval` menggunakan metode `INNER JOIN` antara `cuti_pegawai_approval`, `employee`, dan `cuti_pegawai`. Pastikan kehilangan data (apabila kode karyawan master tak sengaja terlempar) ini dikehendaki. Transisikan dengan `LEFT JOIN` pada tabel *employee* / *cuti_pegawai* jika integritas data persetujuan dianggap prioritas tertinggi di atas relasi eksis.
5. **Sanitasi `NaN` (Bukan Angka Terhadap Nilai Kosong):** Perbaiki tipe yang diinterpretasikan pandas jika bertemu sel mati (null) yakni `NaN`. Ganti `NaN` menjadi python `None` mengadopsi standar *vector operation* dengan `df.replace({pd.NA: None, np.nan: None})` khususnya pada field catatan (*notes*) untuk membebaskan konektor basis data dari error data float.

## 5. Rekomendasi Optimisasi
- Daripada iterasi satu per satu dengan konstruksi dasar `itertuples()`, manfaatkan fitur-fitur pemrosesan list/dictionary per list mutakhir.
- Lengkapi seluruh rutin eksekusi persisten dengan blok-blok *try/except* sebagai penangkal error berantai yang terisolasi dengan menggunakan pemanggil logika *logging* seragam (`v2_helper` jika tersedia).
- Penggunaan library terpusat semacam `format_datetime_series` telah diaplikasikan baik, teruskan menjaga integritas standarisasi ini bagi elemen *datetime* minor sisa.
