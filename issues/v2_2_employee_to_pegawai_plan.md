# Issue: Refaktor dan Optimasi `v2_2_employee_to_pegawai.py`

## Latar Belakang
File `v2_2_employee_to_pegawai.py` membutuhkan refaktor dan optimasi. Terdapat beberapa isu terkait penggunaan memori dan kesalahan logika dalam mapping data (penggabungan atau pencocokan data) menggunakan pustaka pengolah data. Dokumen ini dibuat sebagai panduan kerja (*plan*) bagi junior developer atau AI.

## Persyaratan Lingkungan
- Gunakan *virtual environment* Python dari direktori proyek (`.venv`).
- **PENTING:** Anda diwajibkan untuk menggunakan argumen prompt/tool `context7` pada AI engine (MCP server) untuk mencari referensi atau *best practice* terkini tentang optimasi pustaka pengolah data (seperti mengelola memori DataFrame agar tidak boros, dan mapping efisien).
- Gunakan seluruh kemampuan/skill (*use all available skills*) yang dimiliki untuk membantu dalam memeriksa logika serta menguji (testing) skrip setelah diperbaiki.

## Identifikasi Bug & Kandidat Optimasi
Berdasarkan analisis file saat ini, ditemukan isu-isu berikut:

1. **Pemborosan Memori (Memory Leak):** 
   Hampir di seluruh *helper function* (untuk mapping ID seperti organisasi, jabatan, golongan, dsb.) terdapat proses pembuatan salinan (copy) keseluruhan data secara berulang. Karena set data utama berukuran sangat besar, menyalin keseluruhan tabel hanya untuk mengubah satu ruas data adalah pemborosan sumber daya dan akan menyebabkan pelambatan yang luar biasa.

2. **Kesalahan Tipe Objek (Bug):** 
   Pada fungsi pembersihan pendapatan non-pajak, hasil dari pengambilan data database berwujud koleksi biasa (list of dictionary). Namun secara logika, terdapat pemanggilan fungsi yang membutuhkan format tabel berseri (Dataframe khusus). Pemanggilan langsung terhadap fungsi-fungsi khusus DataFrame dari koleksi/list ini akan memicu error `AttributeError`.

3. **Perangkaian Kolom yang Berlebihan:** 
   *Helper function* menerima parameter berbentuk keseluruhan tabel data, padahal sebenarnya hanya membutuhkan satu kolom spesifik untuk dicocokkan (mapping). Ini memperparah isu pemborosan memori.

## Rekomendasi Perbaikan & Optimasi

1. **Ganti Argumen Helper Function:**
   Ubah parameter pada modul pembersihan spesifik agar mereka menerima kolom individu (*Series*) saja ketimbang menerima seluruh tabel keseluruhan.

2. **Hapus Penyalinan Data yang Tidak Perlu:**
   Hilangkan pemanggilan copy (misal `df = df.copy()`) di bagian awal dalam semua modul helper pembersihan (*cleanup*). 

3. **Validasi Pembuatan Objek Data:**
   Setiap hasil yang terambil dari fungsi `fetch_...` (yang masih berupa koleksi list) harus wajib dibuat (wrap) menjadi objek DataFrame terlebih dahulu, *sebelum* memanipulasi kolom atau membuat map (seperti menggunakan `set_index()`).

4. **Koreksi Tipe Data dan Eksekusi:**
   Terapkan *mapping* dan pemberian nilai pengganti (fallback) default `0` serta konversi tipe angka (`integer`) secara efisien di DataFrame induk (In-Place jika memungkinkan). Hindari memuat frame baru kecuali diwajibkan.

## Langkah-Langkah Pengerjaan

Silakan lakukan perbaikan secara terstruktur seperti alur berikut:

1. **Tahap 1: Riset Praktik Terbaik (Context 7)**
   - Jalankan tool integrasi `context 7` untuk mendapatkan referensi dokumentasi.
   - Contoh query pencarian: *pandas memory optimization, efficient multiple column map, avoid copy warning*.
   - Pelajari hasilnya dan persiapkan untuk menerapkannya di kode.

2. **Tahap 2: Koreksi *Runtime Bug***
   - Cari fungsi `cleanup_pendapatan_non_pajak`.
   - Pastikan variabel hasil database (`pnp`) sudah dikonversi secara eksplisit ke dalam objek DataFrame sebelum menggunakan method pemanipulasi index.

3. **Tahap 3: Implementasi Optimasi Memori**
   - Hapus semua baris salinan objek pada variabel asal dari dalam semua helper (*cleanup organisasi, jabatan, golongan, dll*).
   - Ubah definisi *input* helper tersebut sehingga hanya meminta satu urutan/variabel kolom.
   - Di dalam *Main cleanup block*, atur agar implementasi *map* langsung ter-*assign* atau memperbarui kolom pada *Main DataFrame* secara langsung.

4. **Tahap 4: Pengujian & Validasi (Testing)**
   - Akses python melalui `.venv`.
   - Jalankan skrip `v2_2_employee_to_pegawai.py`.
   - Lakukan inspeksi visual di console bila ada error (*stack trace*). Pantau durasi (*logged duration*) untuk membuktikan bahwa langkah optimasi di atas berhasil mengurangi waktu eksekusi.
