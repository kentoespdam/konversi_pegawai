# Plan Audit, Perbaikan, dan Optimasi: `v2_7_emp_work_experience_to_pengalaman_kerja.py`

Dokumen ini disusun sebagai panduan bagi Junior Developer atau AI Model untuk memperbaiki dan mengoptimalkan script migrasi `v2_7_emp_work_experience_to_pengalaman_kerja.py` beserta pustaka pendukungnya (`core/smartoffice/emp_work_experience.py` dan `core/kepegawaian/kepeg_pengalaman_kerja.py`).

Sesuai dengan pedoman pengerjaan, **Wajib menggunakan Context 7** saat mengimplementasikan langkah-langkah di bawah ini. Hal tersebut untuk memastikan _best practice_ penulisan kode Python, penanganan exception, standar pemrosesan Pandas, dan query SQL. Selalu jalankan environment menggunakan Python dari dalam `.venv`.

## 1. Identifikasi Bug & Potensi Masalah

Berdasarkan penelusuran kode dan inspeksi skema basis data target, ditemukan sejumlah kelemahan signifikan pada skrip saat ini:

- **Kolom `version` Tidak Ada di Tabel Target**: Fungsi save di `kepeg_pengalaman_kerja.py` menyisipkan nilai _hardcoded_ `version = 0` pada query INSERT, padahal tabel `pengalaman_kerja` di database target **tidak memiliki kolom `version`**. Hal ini akan menyebabkan SQL Error saat eksekusi INSERT. Kolom ini harus dihapus dari query INSERT dan dari tuple data.

- **Idempotency Rusak (`ON DUPLICATE KEY UPDATE` Tidak Berfungsi)**: Tabel target `pengalaman_kerja` tidak memiliki _Unique Key_ selain Primary Key auto-increment `id`. Artinya, klausul `ON DUPLICATE KEY UPDATE` tidak akan pernah terpicu, dan setiap kali skrip dijalankan ulang akan menghasilkan **baris duplikat**. Diperlukan mekanisme TRUNCATE sebelum INSERT, atau penambahan _Unique Constraint_ di tabel, atau strategi DELETE+INSERT.

- **Kolom Target Tidak Terisi Lengkap**: Query fetch mengambil `tanggal_pengajuan` dan `tanggal_disetujui`, namun fungsi save **tidak pernah menyisipkan** kedua kolom tersebut ke tabel target. Selain itu, kolom `disetujui` dan `disetujui_oleh` yang ada di tabel target juga tidak diisi sama sekali.

- **INNER JOIN Menyebabkan Kehilangan Data**: Query fetch menggunakan `INNER JOIN bidang_perusahaan` yang mengakibatkan record dengan `ewe_company_type` tidak cocok di tabel referensi akan **hilang** (dari 21 record total menjadi 20 setelah join). Seharusnya menggunakan `LEFT JOIN` agar semua data pengalaman kerja tetap terjaga.

- **Kolom `approve_by` Tidak Di-fetch dari Sumber**: Tabel `emp_work_experience` memiliki kolom `approve_by` yang diperlukan untuk mengisi `disetujui_oleh` di tabel target, namun query fetch pada v2_7 tidak mengambil kolom tersebut. Modul lain (v2_5 pelatihan, v2_6 pendidikan) sudah mengambil kolom ini secara konsisten.

- **Nilai `tahun_masuk` dan `tahun_keluar` Bernilai 0**: Beberapa record di database sumber memiliki nilai 0 untuk kolom tahun (tipe data `YEAR(4)` di MySQL). Fungsi cleanup melakukan `.astype(int)` tanpa menangani kasus nilai 0 yang secara semantik merupakan data tidak valid. Nilai 0 sebaiknya dikonversi menjadi `None`.

- **Error pada Pandas DataFrame Kosong**: Tidak ada pengecekan atau mekanisme _early exit_ apabila fungsi fetch (`fetch_emp_work_experience_for_pengalaman_kerja`) mengembalikan DataFrame kosong. Hal ini dapat menyebabkan error ketika memanipulasi kolom pada fungsi `cleanup` atau memicu query INSERT yang sia-sia di `save_pengalaman_kerja_from_emp_work_experience`.

- **Konversi Tipe Data Pandas NULL (`NaN`/`NaT`)**: Penggunaan `df.itertuples(index=False)` langsung setelah DataFrame memuat parameter _null_ hasil fetch DB akan membawa tipe bawaan Pandas (contohnya `NaN` bertipe float dan `NaT` bertipe datetime). Hal ini akan menimbulkan kejanggalan format atau SQL Error karena driver DB Python kesulitan melakukan parse literal `NaN`/`NaT` dibandingkan nilai natif `None`.

- **Flag `disetujui` Tidak Diisi**: Kolom `disetujui` di tabel target sama sekali tidak diisi oleh fungsi save. Seharusnya menggunakan logika dinamis berdasarkan keberadaan nilai pada kolom `tanggal_disetujui` (bernilai `True` hanya jika `tanggal_disetujui` tidak NULL), konsisten dengan pola di v2_5 dan v2_6.

- **Minimnya Log Pengaman (Error Handling)**: Pada siklus data extraction hingga load (_saving_), skrip sama sekali tidak dilindungi _Try-Except Block_, yang berarti satu masalah koneksi DB atau iterasi tipe data salah akan menghentikan seluruh program secara paksa tanpa notifikasi terstruktur. Skrip juga tidak mencatat berapa banyak record yang berhasil di-fetch maupun di-save.

- **Redundansi `biodata_id=VALUES(biodata_id)` di Klausul Update**: Klausul `ON DUPLICATE KEY UPDATE` menyertakan pembaruan `biodata_id` yang merupakan bagian identifikasi record. Pembaruan kolom ini redundan dan tidak memiliki fungsi.

- **Tidak Ada `updated_at=CURRENT_TIMESTAMP` di Klausul Update**: Berbeda dengan modul `kepeg_pelatihan.py` dan `kepeg_pendidikan.py` yang sudah dioptimasi, klausul update pada v2_7 tidak menyertakan pembaruan _timestamp_, sehingga waktu perubahan terakhir tidak tercatat.

## 2. Rekomendasi Perbaikan (Bug Fixes)

Berikut adalah tahap mitigasi teknis untuk kendala di atas:

1. **Hapus Kolom `version` dari Query INSERT**: Buang kolom `version` dan nilai _hardcoded_ `0` dari daftar kolom INSERT dan dari tuple data di fungsi `save_pengalaman_kerja_from_emp_work_experience`. Kolom ini tidak ada di skema tabel target.

2. **Perbaiki Strategi Idempotency**: Karena tabel `pengalaman_kerja` tidak memiliki _Unique Key_, terapkan strategi **TRUNCATE sebelum INSERT** untuk mencegah duplikasi saat re-run. Implementasikan dengan menambahkan eksekusi `TRUNCATE TABLE pengalaman_kerja` di awal fungsi save sebelum `executemany`. Alternatif lain: koordinasi dengan DBA untuk menambahkan _Unique Constraint_ pada kombinasi `biodata_id` + `nama_perusahaan` + `tahun_masuk`.

3. **Tambahkan Kolom yang Hilang ke INSERT**: Sertakan kolom `tanggal_pengajuan`, `tanggal_disetujui`, `disetujui`, dan `disetujui_oleh` ke dalam query INSERT dan tuple data, agar selaras dengan skema tabel target.

4. **Ubah INNER JOIN Menjadi LEFT JOIN**: Pada query di `emp_work_experience.py`, ganti `INNER JOIN bidang_perusahaan` menjadi `LEFT JOIN bidang_perusahaan` agar record dengan `ewe_company_type` yang tidak terdaftar tetap diambil (dengan `type_perusahaan` bernilai NULL).

5. **Tambahkan Fetch Kolom `approve_by`**: Pada query fetch, tambahkan `ew.approve_by AS disetujui_oleh` ke daftar SELECT agar data pemberi persetujuan ikut diambil dari sumber.

6. **Sanitasi Nilai Tahun 0**: Di fungsi `cleanup`, setelah casting `tahun_masuk` dan `tahun_keluar` ke int, ganti nilai 0 menjadi `None` menggunakan `.replace(0, None)` karena tahun 0 bukan data yang valid.

7. **Sanitasi Ketersediaan DataFrame**: Imbuhkan filter pengecekan `if df.empty: return` pada inisial alur di main script sesudah fetch, dan berikan _logging info_ memadai untuk mencegah pemrosesan memori sia-sia.

8. **Mekanisme Penanganan Nilai Kosong Pandas**: Terapkan prosedur _casting default_ dengan melakukan replace Numpy/Pandas null (seperti `NaN`, `NaT`, `pd.NA`) ke native Python `None` secara global pada instance DataFrame sebelum looping mapping data berlangsung di fungsi save.

9. **Logika Dinamis Pengisian Flag Persetujuan**: Tambahkan kolom `disetujui` di fungsi `cleanup` dengan kondisi dinamis berdasarkan keberadaan `tanggal_disetujui` (bernilai `True` hanya jika `tanggal_disetujui` tidak NULL), konsisten dengan pola v2_5 dan v2_6.

10. **Koreksi Logika Resolusi Duplikasi (`ON DUPLICATE KEY UPDATE`)**: Perbaiki klausul update agar mencakup semua kolom atribut operasional dan sertakan `updated_at=CURRENT_TIMESTAMP` di akhir daftar, sejalan dengan pola yang sudah diterapkan pada modul `kepeg_pelatihan.py` dan `kepeg_pendidikan.py`.

11. **Enkapsulasi Galat Global**: Tangkap siklus eksekusi ke dalam _Try-Except Block_ dipadukan instruksi _logger_. Rekam informasi detail (_stack trace_) jikalau terdapat _fatal execution_ terhadap integrasi query basis data.

12. **Pencatatan Jumlah Record**: Tambahkan logging jumlah baris setelah fetch dan setelah save agar proses migrasi dapat diverifikasi keseluruhannya.

## 3. Rekomendasi Optimasi Performa & Kerapian Kode

1. **Pemurnian Transformasi Clean-Up**: Konfirmasikan seluruh manipulasi data (seperti boolean check `.eq(1)` untuk `is_deleted`, konversi tahun `.astype(int)`) diselesaikan melalui metode implementasi Pandas _vectorized operations_ demi mencegah overhead menyalin memori secara repetitif.

2. **Potensi Eksekusi Chunk (`Bulk Insert`) Database**: Apabila muatan row migrasi memuncak tajam di atas ratusan ribu, sarankan integrasi _bulk processing chunking_, agar mengurangi _overhead iterasi_ pengiriman statement INSERT.

3. **Standardisasi Modul Import**: Bersihkan fungsi yang berpotensi _unused imports_, tambahkan import `logging`, `traceback`, dan `numpy` yang dibutuhkan untuk error handling dan sanitasi NaN. Pusatkan pemanggilan formatter tanggal selayaknya standar sistem `v2_helper` agar menghindari _magic strings_.

4. **Konsistensi Pola dengan v2_5 dan v2_6**: Pastikan struktur skrip (import, inisialisasi LOGGER, try-except di main, empty check, record count logging, NaN sanitization, dynamic `disetujui`) mengikuti pola yang sudah diterapkan pada modul v2_5 dan v2_6 agar seluruh pipeline migrasi seragam.

## 4. Langkah-Langkah Pengerjaan

Dokumen ini disusun sebagai instrumen _checklist_. Pedomani runtutan step teknis berikut saat proses _fixing_ modul migrasi versi 7:

- [ ] **Aktivasi Environment & Referensi**: Posisikan di direktori _root_ proyek dan login ke dalam virtual environment via `source .venv/bin/activate`. Selalu panggil rujukan berbasis **Context 7** menyangkut implementasi _Python best practices_ maupun perlakuan SQL.

- [ ] **Perbaikan Query Fetch Sumber (`core/smartoffice/emp_work_experience.py`)**: Ubah `INNER JOIN bidang_perusahaan` menjadi `LEFT JOIN bidang_perusahaan` untuk mencegah kehilangan data. Tambahkan kolom `ew.approve_by AS disetujui_oleh` pada daftar SELECT agar data pemberi persetujuan ikut terambil.

- [ ] **Perbaikan Fungsi Save Target (`core/kepegawaian/kepeg_pengalaman_kerja.py`)**: Hapus kolom `version` dan nilai _hardcoded_ `0` dari query INSERT dan tuple data. Tambahkan kolom `tanggal_pengajuan`, `tanggal_disetujui`, `disetujui`, dan `disetujui_oleh` ke query INSERT dan tuple data. Ganti parameter `disetujui` yang di-_hardcode_ dengan referensi kolom `row.disetujui` dari DataFrame. Perbaiki klausul `ON DUPLICATE KEY UPDATE` agar mencakup semua kolom atribut operasional (hapus entri redundan `biodata_id=VALUES(biodata_id)`), dan sertakan `updated_at=CURRENT_TIMESTAMP` di akhir daftar. Pertimbangkan menambahkan `TRUNCATE TABLE pengalaman_kerja` di awal fungsi save untuk menjamin idempotency selama tabel belum memiliki _Unique Key_.

- [ ] **Pengaman Penanganan Data (`v2/v2_7_emp_work_experience_to_pengalaman_kerja.py`)**: Tambahkan import `logging`, `traceback`, dan `numpy`. Inisialisasi `LOGGER` dari `core.config`. Letakkan sistem pengaman `if df.empty: return` sebelum DataFrame dipoles (`cleanup()`). Tambahkan logging jumlah record setelah fetch dan setelah save. Tambahkan logika dinamis kolom `disetujui` berdasarkan keberadaan `tanggal_disetujui` di fungsi `cleanup`. Sanitasi nilai `tahun_masuk` dan `tahun_keluar` yang bernilai 0 menjadi `None`. Berikan mekanisme substitusi _null value_ Pandas ke `None` sebelum return dari `cleanup`. Tutupi langkah inti di _Try-Except Global_ dengan standar luaran penulisan _error log_ beserta _stack trace_.

- [ ] **Testing dan Assessment Terminal**: Uji finalisasi script menekan baris eksekusi `python -m v2.v2_7_emp_work_experience_to_pengalaman_kerja`. Pantau kemunculan log durasi waktu migrasi dan jumlah record untuk menyimpulkan integrasi valid di console, nihil _runtime crash_. Verifikasi bahwa tabel `pengalaman_kerja` terisi lengkap dengan kolom `tanggal_pengajuan`, `tanggal_disetujui`, `disetujui`, dan `disetujui_oleh`. Pastikan tidak ada baris duplikat jika script dijalankan ulang.
