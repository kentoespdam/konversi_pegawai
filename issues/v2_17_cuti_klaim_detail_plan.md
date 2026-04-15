# Plan Migrasi v2.17 - Cuti Klaim Detail

## 1. Objektif
Dokumen ini menjadi panduan tingkat tinggi (high-level) bagi AI model kecil atau junior developer untuk melakukan inspeksi, perbaikan bug, dan optimisasi pada proses migrasi `v2_17_cuti_klaim_detail.py`.

## 2. Praktik Terbaik Code & Environment
1. **Environment:** Gunakan spesifik python executable dari environment project yaitu `./.venv/bin/python`.
2. **Context 7 Context:** Mengacu pada dokumentasi Context 7 untuk memvalidasi *best practices* Python terkini. Lakukan optimasi penggunaan operasi Pandas yang efisien (meminimumkan iterasi lambat `itertuples`) jika memungkinkan, penyamaan manajemen nilai kosong (`None` vs `NaN`), implementasi idempotency pada query basis data, dan penambahan *exception handling* yang andal atas tiap transaksi.

## 3. Contoh Value Database
Untuk meminimalisir kewajiban interogasi ulang ke database saat pengerjaan skrip, berikut snapshot sample data dari basis data master saat ini:

**Tabel Asal: `smartoffice.cuti_pegawai_detail`**
| id | ref_cuti_id | tanggal |
|---|---|---|
| 1 | 59 | 2019-03-14 |
| 2 | 59 | 2019-03-15 |
| 3 | 60 | 2019-03-14 |
| 4 | 60 | 2019-03-15 |
| 5 | 62 | 2019-03-18 |

**Tabel Tujuan: `kepegawaian_migrasi.cuti_klaim_detail`**
Struktur identik dan langsung memetakan `id`, `tanggal`, serta `ref_cuti_id`.

## 4. Identifikasi Bug dan Rekomendasi Perbaikan
Terdapat beberapa anomali dan resiko yang ditemui pada baris instruksi asal. Lakukan penanganan secara komprehensif pada pengerjaannya nanti:
1. **Pengecekan Kekosongan Data (Empty DataFrame Checks):** Validasi `df.empty` belum ada di skrip utama atau di fungsi penyimpan data `save_cuti_klaim_detail`. Tambahkan logika `if df.empty: return` guna memastikan kelancaran alur jika query mengembalikan hasil kosong.
2. **Isu Idempotency (ON DUPLICATE KEY UPDATE):** Fungsi `save_cuti_klaim_detail` saat ini menggunakan instruksi `INSERT INTO` standar. Modifikasi kueri ini dengan menambahkan klausa `ON DUPLICATE KEY UPDATE tanggal = VALUES(tanggal), ref_cuti_id = VALUES(ref_cuti_id)` agar skrip dapat dijalankan berulang kali tanpa menderita error duplikat *primary key*.
3. **Resiko Pemotongan Relasi di Query Asal (INNER JOIN):** `fetch_cuti_pegawai_detail` menggunakan `INNER JOIN` dengan tabel `cuti_pegawai`. Pastikan kesengajaan pendekatan ini; apabila diharapkan migrasi detail cuti dilakukan terpisah dengan integritasnya, bisa dijaga. Jika detail cuti harus selalu terekam terlepas kelengkapan tabel *parent*, gunakan `LEFT JOIN`.
4. **Sanitasi `NaN` (Nilai Kosong Khusus):** Pastikan adanya operasi sanitasi dasar `df.replace({pd.NA: None, np.nan: None})` sebelum memuat data dari *DataFrame* ke struktur data insert SQL untuk menjamin data yang nilainya kosong dapat masuk dengan mulus sebagai nilai NULL, meski pada tabel ini hanya melibatkan entitas tanggal dan integer *(best practice prevensi error float)*.

## 5. Rekomendasi Optimisasi
- Transformasi penyusunan values pada klausa `save_cuti_klaim_detail` bila perlu, hindari iterasi baris standar yang membebani memori. Gunakan metode `df.to_dict('records')` atau operasi vektor lainnya walau tidak seefektif di *bulk execute* native, perhatikan aspek pembacaan *memory overhead*.
- Utamakan implementasi pembungkusan interaksi database pada blok abstraksi *try/except* yang komprehensif, untuk menahan penghentian proses bila ada record yang invalid. Gunakan logger dari module `v2_helper` jika tersedia.
- Tambahkan logs (via `logging.info`) agar terlihat *progress tracker* saat konversi detail cuti ini dimuat dengan record yang mungkin sangat masif.
