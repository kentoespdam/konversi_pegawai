# Migration Plan: Cuti Approval Chain (`v2_15_cuti_approval_chain.py`)

## 1. Tujuan
Dokumen ini berisi panduan tingkat tinggi (high-level) untuk melakukan audit, perbaikan bug, dan optimasi pada skrip migrasi `v2_15_cuti_approval_chain.py`. Skrip ini bertanggung jawab memindahkan data chain approval cuti pegawai dari database sumber (`smartoffice`) ke database target (`kepegawaian_migrasi`). Dokumen ini akan menjadi acuan bagi junior developer atau agen AI dalam pengerjaan tugas.

## 2. Struktur Data dan Contoh Value
Berikut merupakan representasi baris data dari database sumber yang telah di-fetch, agar Anda **tidak perlu lagi melakukan fetch ulang untuk melihat skema dan tipe data**:

| id | ref_cuti_id | jabatan_id | jabatan_nama | approval_level | read_write_status |
|---|---|---|---|---|---|
| 1 | 2 | 49 | Ka. Sub Bag. Adm. & Pengembangan | 1 | 1 |
| 3 | 2 | 49 | Ka. Sub Bag. Adm. & Pengembangan | 3 | 1 |

*Perhatian: Contoh data ini sudah merepresentasikan hasil output dari query sumber. Silakan gunakan struktur ini sebagai acuan pemetaan data (data mapping).*

## 3. Identifikasi Masalah & Potensi Bug
Skrip saat ini (`v2_15_cuti_approval_chain.py`) menarik data secara keseluruhan dan mem-postingnya. Hal ini memiliki beberapa celah:
- **Data Sanitization & Missing Values:** Terdapat potensi kolom integer (seperti `jabatan_id` atau `approval_level`) berisi NaN jika tidak dipetakan dengan benar, yang jika masuk ke dalam Pandas DataFrame tanpa casting tipe `Int64`, akan berubah menjadi `float`. Ini akan menyebabkan script SQL gagal dieksekusi.
- **Ketiadaan Chunking (Performa):** Mengambil keseluruhan data konversi (`fetch_cuti_approval_chain()`) berimbas fatal terhadap RAM dan eksekusi memori (Out Of Memory) apabila data yang diambil berukuran masif (ratusan ribu baris data).
- **Graceful Error Handling:** Jika terdapat satu baris data korup yang masuk ke kepegawaian, belum terdapat `try-except` di fungsi `main()` untuk meredam panic exception.
- **Idempotensi Kurang Ketat:** Walaupun *ON DUPLICATE KEY UPDATE* sudah tertera, data null/kosong pada string `jabatan_nama` yang tidak ditangani sebelum batch update dapat membersihkan data lama.

## 4. Instruksi Pengerjaan (Langkah demi Langkah)
1. **Gunakan Environment yang Tepat:**
   Dalam pengujian script, pastikan eksekusi dilakukan secara teratur dengan Python virtual environment lokal yang ada: `./.venv/bin/python`.
   
2. **Pelajari Best Practice (Wajib):**
   Gunakan tools atau prompt untuk memanggil **Context 7** guna mengeksplor referensi optimasi Pandas dan penulisan skrip pipeline ETL yang terbaik (best practice).
   
3. **Audit dan Buat Batasan Tarik Data:**
   Buka file sumber pengambilan data. Lakukan inspeksi jika memungkinkan untuk mengubah query menjadi membatasi limit batch (misalnya offset per 5.000 data) agar RAM tereksekusi dengan ringan, namun tetap dapat memproses seluruh data dengan aman.
   
4. **Implementasikan Vectorized Operation (Pandas):**
   Di fungsi pipeline antara *fetch* dan *save*:
   - Gunakan metode built-in dari Pandas untuk mencari nulls (`.fillna()`) dan mengganti string kosong.
   - Buat cast secara eksplisit untuk key yang sifatnya bilangan bulat ke format `<Int64>`, hindari penggunaan float untuk ID atau Relational Schema ID.
   - *Penting:* Jangan gunakan `iterrows()` atau iterasi for loop Python murni jika proses dapat diselesaikan menggunakan operasi kolom berbasis _vectorized_.

5. **Tambahkan Error Block & Logging:**
   Bungkus eksekusi ke ranah proteksi `Exception` dan berikan pesan log komprehensif ketika operasi transfer berhasil atau ketika ada record yang menjadi *blocker*.

## 5. Ekspektasi Validasi
Skrip hasil refactor haruslah stabil (idempotent), berjalan lebih cepat dan anti-OOM, terkomputasi dengan bersih (bersih dari warning NaN DataFrame), serta menggunakan semua skill / standar yang ada pada sistem.
