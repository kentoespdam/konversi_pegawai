# Plan Audit, Perbaikan, dan Optimasi: `v2_4_emp_skill_to_keahlian.py`

Dokumen ini disusun sebagai panduan bagi Junior Developer atau AI Model untuk memperbaiki dan mengoptimalkan script migrasi `v2_4_emp_skill_to_keahlian.py` beserta pustaka pendukungnya (`core/smartoffice/emp_skill.py` dan `core/kepegawaian/kepeg_keahlian.py`).

Sesuai dengan pedoman pengerjaan, **Wajib menggunakan Context 7** saat mengimplementasikan langkah-langkah di bawah ini. Hal tersebut untuk memastikan _best practice_ penulisan kode Python, penanganan exception, standar pemrosesan Pandas, dan query SQL. Selalu jalankan environment menggunakan Python dari dalam `.venv`.

## 1. Identifikasi Bug & Potensi Masalah

Berdasarkan penelusuran kode, ditemukan beberapa kelemahan pada skrip saat ini:
- **Error pada Pandas DataFrame Kosong**: Tidak ada proteksi atau proses *early exit* jika query dari database gagal mengembalikan data. Hal ini akan memicu error lanjutan ketika memproses list kompilasi atau *insert* data.
- **Kesalahan Tipe Data Abstrak (`NaN` / `NULL`)**: Pandas default membaca relasi kosong (contoh: `jenis_keahlian_id`, kolom `tahun`, dsb.) sebagai Object/Float `NaN`. Evaluasi seperti asersi angka (`> 0`) dapat memicu `TypeError`. Jika nilai `NaN` diteruskan ke `INSERT INTO` SQL, driver DB berisiko *crash* atau salah menginput data.
- **Logika Resolusi Konflik `ON DUPLICATE KEY UPDATE` Kurang Tepat**: Blok query saat kondisi duplikasi saat ini hanya memaksa pembaruan parameter _Primary Key_ (`biodata_id=VALUES(biodata_id)`). Logika ini tidak bermanfaat. Jika baris berkonflik, kolom-kolom penunjang dan nilai aktualnya yang harus ter- _update_ (contoh: status sertifikasi, kualifikasi, dsb).
- **Nilai *Hardcoded* untuk Flag Penunjang**: Saat menyusun tuple untuk disisipkan, flag parameter `disetujui` diberikan nilai absolut `True`. Nilai statis ini menabrak kaidah kebenaran data; ia seharusnya menggunakan logika dinamis berdasarkan data referensi (misalnya apakah `tanggal_disetujui` sudah terisi).
- **Minimnya Keamanan Eksekusi (Error Handling)**: Pada siklus data extraction → cleanup → saving, skrip akan _break_ dan menghentikan seluruh _flow_ tanpa penjelasan logging memuaskan jika terjadi putus koneksi atau iterasi nilai buruk dari DB.

## 2. Rekomendasi Perbaikan (Bug Fixes)

Ikuti langkah mitigasi teknis berikut ini untuk mengatasi anomali tersebut:
1. **Validasi Ketersediaan Data Pipeline**: Tambahkan pengecekan khusus `if df.empty:` di awal alur `main()` atau segera setelah proses `fetch_`. Berikan instruksi logging info dan `return` awal (*early exit*) jika kondisinya memicu *True*.
2. **Mapping Aman Pada Nilai `NaN` Tipe Pandas**: Konversi DataFrame null dari standar Numpy `NaN` ke native Python `None`  sebelum proses loop row ke struktur tuple. Serta, berikan sanitasi error atau cast kondisional saat memvalidasi `row.jenis_keahlian_id`.
3. **Pemberian Syarat Dinamis Pengisian Data**: Kaitkan parameter di Tuple mapping. Jadikan kolom boolean `disetujui` berindikasi *True* saat dan hanya jika terdapat konten pada format `tanggal_disetujui`. 
4. **Perbaikin Query `INSERT ... ON DUPLICATE UPDATE`**: Ganti _dummy statement_ saat bentrok _Unique/Primary_ dari ID, menjadi update operasional. Perbarui instrumen nilai nyata dari data profil pekerja tersebut (misalnya `is_deleted=VALUES(is_deleted)`, `institusi=VALUES(institusi)`, dsb).
5. **Block Kontrol Exception Global**: Bungkus siklus eksekusi memori di dalam instrumen `Try-Except`, dan pergunakan modul/fungsi logging guna memberikan rekam jejak konsol jika ada _fatal crash_.

## 3. Rekomendasi Optimasi Performa & Kerapian Kode

1. **Pemurnian Transformasi *Clean-Up***: Jalankan operasi *vectorized* dari Pandas di blok `cleanup()`. Pastikan pembersihan parameter semacam `sertifikasi` atau flag boolean dilakukan efektif tanpa boros memori salinan (copy).
2. **Siklus Insert per Batch (*Chunk*)**: Jika limitasi memori sistem tidak sanggup menanggung tuple massal sekaligus (contoh volume pekerja ratusan ribu), berikan opsi batch _bulk insert_. (Opsional - pastikan helper `save_update_kepegawaian` kompatibel dengan pemrosesan *many* berulang).
3. **Standardisasi Impor dan Naming Conventions**: Patuhi kaidah penulisan direktori standar konversi, konsolidasi referensi format ke `v2_helper` jika dipandang sejalan, dan hindari sisa _magic strings_ atau konstanta acak tersembunyi.

## 4. Langkah-Langkah Pengerjaan

Dokumen ini adalah target pelacakan, silakan jalankan langkah _checklist_ berikut dalam implementasi program Anda:

- [ ] **Persiapan dan Referensi**: Masuk ke root dan nyalakan virtual environment `source .venv/bin/activate` (atau ekuivalennya). Analisa panduan **Context 7** untuk _best practice_ referensi.
- [ ] **Modifikasi Query Basis Data (`core/kepegawaian/kepeg_keahlian.py`)**: Hapus `ON DUPLICATE KEY UPDATE` keliru, lalu susun target kolom-kolom _non-primary_ yang perlu pembaruan secara sistematis. Modifikasi logic tuples agar _property_ null (`NaN`) dikonversi jadi parameter `None` yang dipahami DB.
- [ ] **Perbaiki Blok `fetch` & _Clean-Up_ (`core/smartoffice/emp_skill.py` & util di script)**: Buat logika penggantian boolean pada kolom `status`, serta _dynamic checking_ nilai boolean `disetujui`.
- [ ] **Pengaman Blok Utama (`v2/v2_4_emp_skill_to_keahlian.py`)**: Pasang pengintai `df.empty`, bungkus alinea operasional dalam balutan _Try-Except Global_ dengan standar log (info dan error).
- [ ] **Pengujian (*Trial Execute*)**: Uji _script_ menggunakan command `python -m v2.v2_4_emp_skill_to_keahlian`. Telusuri output log di terminal _console_ guna memastikan durasi tercatat akurat dan tidak melahirkan _Tracing Error_ semu untuk data `NaN`.
