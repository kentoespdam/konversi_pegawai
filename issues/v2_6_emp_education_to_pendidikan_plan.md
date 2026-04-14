# Plan Audit, Perbaikan, dan Optimasi: `v2_6_emp_education_to_pendidikan.py`

Dokumen ini disusun sebagai panduan bagi Junior Developer atau AI Model untuk memperbaiki dan mengoptimalkan script migrasi `v2_6_emp_education_to_pendidikan.py` beserta pustaka pendukungnya (`core/smartoffice/emp_education.py` dan `core/kepegawaian/kepeg_pendidikan.py`).

Sesuai dengan pedoman pengerjaan, **Wajib menggunakan Context 7** saat mengimplementasikan langkah-langkah di bawah ini. Hal tersebut untuk memastikan _best practice_ penulisan kode Python, penanganan exception, standar pemrosesan Pandas, dan query SQL. Selalu jalankan environment menggunakan Python dari dalam `.venv`.

## 1. Identifikasi Bug & Potensi Masalah

Berdasarkan penelusuran kode, ditemukan beberapa kelemahan pada skrip saat ini:

- **Error pada Pandas DataFrame Kosong**: Tidak ada pengecekan atau mekanisme *early exit* apabila fungsi fetch (`fetch_emp_education_for_pendidikan`) mengembalikan DataFrame kosong. Hal ini dapat menyebabkan error ketika memanipulasi kolom pada fungsi `cleanup` (khususnya saat mapping `jenjang_pendidikan` ke `jenjang_id`) atau memicu *query insert* yang sia-sia di `save_pendidikan_from_emp_education`.
- **Konversi Tipe Data Pandas NULL (`NaN`/`NaT`)**: Penggunaan `df.itertuples(index=False)` langsung setelah DataFrame memuat parameter *null* hasil fetch DB akan membawa tipe bawaan Pandas (contohnya `NaN` bertipe float dan `NaT` bertipe datetime). Hal ini akan menimbulkan kejanggalan format atau *SQL Error* karena driver DB Python kesulitan melakukan parse literal `NaN`/`NaT` dibandingkan nilai natif `None`.
- **Nilai *Hardcoded* untuk Flag `disetujui`**: Dalam mapping row di fungsi save, flag boolean `disetujui` diberikan nilai absolut `True` secara statis. Nilai ini menabrak kaidah kebenaran data; ia seharusnya menggunakan logika dinamis berdasarkan keberadaan nilai pada kolom `tanggal_disetujui` (bernilai `True` hanya jika `tanggal_disetujui` tidak *NULL*).
- **Pengecekan String Kosong yang Redundan pada Fungsi Save**: Pada fungsi `save_pendidikan_from_emp_education`, terdapat validasi `row.tahun_masuk != ""` dan `row.tahun_lulus != ""` yang sebenarnya sudah ditangani oleh query SQL sumber (`IF(eed.edu_sdate = "", NULL, eed.edu_sdate)`). Pengecekan ganda ini mengaburkan alur data dan menambah kompleksitas yang tidak perlu.
- **Anomali pada Query `ON DUPLICATE KEY UPDATE`**: Klausul update saat konflik duplikasi menyertakan `biodata_id=VALUES(biodata_id)` yang kemungkinan besar merupakan bagian dari *Unique Key* tabel. Pembaruan kolom kunci ini redundan dan tidak berfungsi. Selain itu, klausul tersebut tidak menyertakan `updated_at=CURRENT_TIMESTAMP` untuk mencatat waktu pembaruan terakhir, berbeda dengan modul pelatihan (`kepeg_pelatihan.py`) yang sudah menerapkan pola ini.
- **Konversi GPA Tanpa Indikasi Kesalahan Data**: Fungsi `str_to_float` mengembalikan nilai `0` secara diam-diam ketika menemukan format GPA yang tidak valid. Tidak ada logging atau penanda bahwa data asli bermasalah, sehingga nilai GPA `0` di target bisa merupakan nilai asli maupun hasil konversi gagal tanpa bisa dibedakan.
- **Minimnya Log Pengaman (Error Handling)**: Pada siklus data extraction hingga load (*saving*), skrip sama sekali tidak dilindungi *Try-Except Block*, yang berarti satu masalah koneksi DB atau iterasi tipe data salah akan menghentikan seluruh program secara paksa tanpa notifikasi terstruktur. Skrip juga tidak mencatat berapa banyak record yang berhasil di-fetch maupun di-save.

## 2. Rekomendasi Perbaikan (Bug Fixes)

Berikut adalah tahap mitigasi teknis untuk kendala di atas:

1. **Sanitasi Ketersediaan DataFrame**: Imbuhkan filter pengecekan `if df.empty: return` pada inisial alur di main script sesudah *fetch*, dan berikan *logging info* memadai untuk mencegah pemrosesan memori sia-sia.
2. **Mekanisme Penanganan Nilai Kosong Pandas**: Terapkan prosedur _casting default_ dengan melakukan replace Numpy/Pandas null (seperti `NaN`, `NaT`, `pd.NA`) ke native Python `None` secara global pada instance DataFrame sebelum looping mapping data berlangsung di fungsi save.
3. **Logika Dinamis Pengisian Flag Persetujuan**: Koreksi penetapan statik/hardcoded boolean `disetujui`. Berikan kondisi pada Pandas di fungsi `cleanup`, menjadikan nilai boolean `disetujui` berindikasi `True` saat kolom `tanggal_disetujui` memuat nilai riil, bukan *NULL*.
4. **Hapus Pengecekan String Kosong Redundan**: Bersihkan validasi `row.tahun_masuk != ""` dan `row.tahun_lulus != ""` pada fungsi save, mengingat konversi string kosong ke `NULL` sudah ditangani di level query SQL sumber.
5. **Koreksi Logika Resolusi Duplikasi (`ON DUPLICATE KEY UPDATE`)**: Hapus entri `biodata_id=VALUES(biodata_id)` yang redundan dari klausul update saat konflik. Tambahkan `updated_at=CURRENT_TIMESTAMP` di akhir daftar kolom update, sejalan dengan pola yang sudah diterapkan pada modul `kepeg_pelatihan.py`.
6. **Enkapsulasi Galat Global**: Tangkap siklus memori eksekutor ke dalam _Try-Except Block_ dipadukan instruksi *logger*. Rekam informasi detail (*stack trace*) jikalau terdapat *fatal execution* terhadap integrasi query basis data.
7. **Pencatatan Jumlah Record**: Tambahkan logging jumlah baris setelah fetch dan setelah save agar proses migrasi dapat diverifikasi keseluruhannya.

## 3. Rekomendasi Optimasi Performa & Kerapian Kode

1. **Pemurnian Transformasi *Clean-Up***: Konfirmasikan seluruh manipulasi data (seperti boolean checks `.eq(1)` untuk `is_lulus`, `is_latest`, `is_deleted`) diselesaikan melalui metode implementasi Pandas _vectorized operations_ demi mencegah overhead menyalin memori secara repetitif. Pastikan hasil konversi GPA `.map(str_to_float)` tidak memerlukan `.astype(float)` tambahan yang redundan.
2. **Potensi Eksekusi Chunk (`Bulk Insert`) Database**: Apabila muatan row migrasi memuncak tajam di atas ratusan ribu, sarankan integrasi *bulk processing chunking*, agar mengurangi _overhead iterasi_ pengiriman statement _insert_.
3. **Standardisasi Modul Import**: Bersihkan fungsi yang berpotensi *unused imports*, tambahkan import `logging` dan `numpy` yang dibutuhkan untuk error handling dan sanitasi NaN. Pusatkan pemanggilan formatter tanggal selayaknya standar sistem `v2_helper` agar menghindari *magic strings*.

## 4. Langkah-Langkah Pengerjaan

Dokumen ini disusun sebagai instrumen _checklist_. Pedomani runtutan step teknis berikut saat proses *fixing* modul migrasi versi 6:

- [ ] **Aktivasi Environment & Referensi**: Posisikan di direktori _root_ proyek dan login ke dalam virtual environment via `source .venv/bin/activate`. Selalu panggil rujukan berbasis **Context 7** menyangkut implementasi *Python best practices* maupun perlakuan SQL.
- [ ] **Perbaikan *Data Upsert* Basis Data (`core/kepegawaian/kepeg_pendidikan.py`)**: Hapus entri redundan `biodata_id=VALUES(biodata_id)` dari klausul `ON DUPLICATE KEY UPDATE`. Tambahkan `updated_at=CURRENT_TIMESTAMP` di akhir daftar kolom update. Hapus pengecekan string kosong redundan untuk `tahun_masuk` dan `tahun_lulus` pada pembuatan tuple data. Ganti parameter `disetujui` yang di-hardcode `True` dengan referensi kolom `row.disetujui` dari DataFrame.
- [ ] **Pemutakhiran Kueri DB (opsional di `core/smartoffice/emp_education.py`)**: Inspeksi kembali rancangan kolom *fetching* guna memastikan `IF` conditional pada `edu_sdate`, `edu_edate`, `edu_gpa` dan status boolean tidak terinjeksi nilai bias/error saat di-parse oleh Pandas di Python. Verifikasi bahwa query tidak memerlukan penyesuaian tambahan.
- [ ] **Pengaman Penanganan Data (`v2/v2_6_emp_education_to_pendidikan.py`)**: Tambahkan import `logging` dan `numpy`. Inisialisasi `LOGGER`. Letakkan sistem pengaman `df.empty` sebelum DataFrame dipoles (`cleanup()`). Tambahkan logika dinamis kolom `disetujui` berdasarkan keberadaan `tanggal_disetujui` di fungsi `cleanup`. Berikan mekanisme substitusi null value ke `None` sebelum return dari `cleanup`. Tutupi langkah inti di _Try-Except Global_ dengan standar luaran penulisan *error log* beserta *stack trace*. Tambahkan log jumlah baris yang diproses.
- [ ] **Testing dan Assessment Terminal**: Uji finalisasi *script* menekan baris eksekusi `python -m v2.v2_6_emp_education_to_pendidikan`. Pantau kemunculan log durasi waktu migrasi dan jumlah record untuk menyimpulkan integrasi valid di console, nihil *runtime crash*.
