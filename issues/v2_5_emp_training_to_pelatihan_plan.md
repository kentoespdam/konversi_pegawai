# Plan Audit, Perbaikan, dan Optimasi: `v2_5_emp_training_to_pelatihan.py`

Dokumen ini disusun sebagai panduan bagi Junior Developer atau AI Model untuk memperbaiki dan mengoptimalkan script migrasi `v2_5_emp_training_to_pelatihan.py` beserta pustaka pendukungnya (`core/smartoffice/emp_training.py` dan `core/kepegawaian/kepeg_pelatihan.py`).

Sesuai dengan pedoman pengerjaan, **Wajib menggunakan Context 7** saat mengimplementasikan langkah-langkah di bawah ini. Hal tersebut untuk memastikan _best practice_ penulisan kode Python, penanganan exception, standar pemrosesan Pandas, dan query SQL. Selalu jalankan environment menggunakan Python dari dalam `.venv`.

## 1. Identifikasi Bug & Potensi Masalah

Berdasarkan penelusuran kode, ditemukan beberapa kelemahan pada skrip saat ini:
- **Error pada Pandas DataFrame Kosong**: Tidak ada pengecekan atau mekanisme *early exit* apabila fungsi fetch (`fetch_emp_training_for_pelatihan`) mengembalikan DataFrame kosong. Hal ini dapat menyebabkan error ketika memanipulasi kolom pada fungsi `cleanup` atau memicu *query insert* yang sia-sia di `save_pelatihan_from_emp_training`.
- **Anomali pada Query Update Konflik (`ON DUPLICATE KEY UPDATE`)**: Pada query insert di `kepeg_pelatihan.py`, penanganan duplikat hanya melakukan pembaruan parameter _Primary Key_ semu (`biodata_id=VALUES(biodata_id)`). Jika memang terjadi pembaruan data (upsert), kolom-kolom inti lainnya yang berubah wajib disertakan dalam logika update, alih-alih diabaikan seperti saat ini.
- **Konversi Tipe Data Pandas NULL (`NaN`/`NaT`)**: Penggunaan `df.itertuples(index=False)` langsung setelah dataframe memuat parameter *null* hasil fetch DB akan membawa tipe bawaan Pandas (contohnya `NaN` bertipe float). Hal ini akan menimbulkan kejanggalan format atau *SQL Error* karena driver DB Python kesulitan melakukan parse literal `NaN` dibandingkan nilai natif `None`.
- **Nilai *Hardcoded* untuk Flag**: Dalam mapping row, flag parameter boolean seperti `disetujui` masih disimplifikasi secara mentah (`TRUE AS disetujui` di dalam SQL). Seharusnya parameter boolean dipetakan lebih dinamis pada Python (misal `disetujui` bernilai `True` hanya jika `tanggal_disetujui` tidak *NULL*).
- **Minimnya Log Pengaman (Error Handling)**: Pada siklus data extraction hingga load (*saving*), skrip sama sekali tidak dilindungi *Try-Except Block*, yang berarti satu masalah koneksi DB atau iterasi tipe data salah, akan menghentikan seluruh program secara paksa tanpa notifikasi terstruktur.

## 2. Rekomendasi Perbaikan (Bug Fixes)

Berikut adalah tahap mitigasi teknis untuk kendala di atas:
1. **Sanitasi Ketersediaan DataFrame**: Imbuhkan filter pengecekan `if df.empty: return` pada inisial alur di main script sesudah *fetch*, dan berikan *logging info* memadai untuk mencegah pemrosesan memori sia-sia.
2. **Koreksi Logika Resolusi Duplikasi (`ON DUPLICATE UPDATE`)**: Ganti statemen `ON DUPLICATE KEY UPDATE biodata_id=VALUES(biodata_id)` menjadi query pembaruan properti atribut penuh (misal: `jenis_pelatihan_id=VALUES(jenis_pelatihan_id)`, `lembaga=VALUES(lembaga)`, `is_deleted=VALUES(is_deleted)` dsb).
3. **Mekanisme Penanganan Nilai Kosong Pandas**: Terapkan prosedur _casting default_ dengan melakukan replace Numpy/Pandas null (seperti *NaN*) ke native Python `None` (melalui perintah `df = df.replace({pd.NA: None, float('nan'): None, pd.NaT: None})`) secara global pada instance dataframe sebelum looping mapping data berlangsung.
4. **Logika Dinamis Pengisian *Flag* Persetujuan**: Koreksi penetapan statik/hardcoded boolean `disetujui`. Berikan kondisi pada Pandas di fungsi `cleanup`, menjadikan nilai boolean `disetujui` berindikasi *True* saat format kolom `tanggal_disetujui` memuat nilai riil, bukan *NULL*.
5. **Enkapsulasi Galat Global**: Tangkap siklus memori eksekutor ke dalam _Try-Except Block_ dipadukan instruksi *logger*. Rekam informasi detail (*stack trace*) jikalau terdapat *fatal execution* terhadap integrasi query basis data.

## 3. Rekomendasi Optimasi Performa & Kerapian Kode

1. **Pemurnian Transformasi *Clean-Up***: Konfirmasikan seluruh manipulasi data (seperti boolean checks `.eq(1)`) diselesaikan melalui metode implementasi Pandas _vectorized operations_ demi mencegah overhead menyalin memori secara repetitif.
2. **Potensi Eksekusi Chunk (`Bulk Insert`) Database**: Apabila muatan row migrasi memuncak tajam di atas ratusan ribu, sarankan integrasi *bulk processing chunking*, agar mengurangi _overhead iterasi_ pengiriman statement _insert_.
3. **Standardisasi Modul Import**: Bersihkan fungsi yang berpotensi *unused imports*, dan pusatkan pemanggilan formatter tanggal selayaknya standar sistem `v2_helper` agar menghindari *magic strings*.

## 4. Langkah-Langkah Pengerjaan

Dokumen ini disusun sebagai instrumen _checklist_. Pedomani runtutan step teknis berikut saat proses *fixing* modul migrasi versi 5:

- [ ] **Aktivasi Environment & Referensi**: Posisikan di direktori _root_ proyek dan login ke dalam virtual environment via `source .venv/bin/activate`. Selalu panggil rujukan berbasis **Context 7** menyangkut implementasi *Python best practices* maupun perlakuan SQL.
- [ ] **Perbaikan *Data Upsert* Basis Data (`core/kepegawaian/kepeg_pelatihan.py`)**: Hapus klausul baris ganjil `ON DUPLICATE KEY UPDATE biodata_id=VALUES(...)` dan jabarkan kembali semua variabel riil operasional yang dituju agar tercapai penulisan data penimpa *conflict* yang wajar.
- [ ] **Pemutakhiran Kueri DB (opsional di `core/smartoffice/emp_training.py`)**: Inspeksi kembali rancangan kolom *fetching* guna memastikan `IF` conditional pada `status` hingga boolean value tidak terinjeksi nilai bias/error saat di-parse oleh Pandas di Python. Hapus statemen *hardcoded* `TRUE AS disetujui` di kueri jika akan diproses di Pandas.
- [ ] **Pengaman Penanganan Data (`v2/v2_5_emp_training_to_pelatihan.py`)**: Letakkan sistem pengaman `df.empty` sebelum dataframe dipoles (`cleanup()`). Berikan mekanisme substitusi Null *value* ke komoditas `None`. Tutupi langkah inti di _Try-Catch Global_ dengan standar luaran penulisan *error log*.
- [ ] **Testing dan Assessment Terminal**: Uji finalisasi *script* menekan baris eksekusi `python -m v2.v2_5_emp_training_to_pelatihan`. Pantau kemunculan log durasi waktu migrasi untuk menyimpulkan integrasi valid di console, nihil *runtime crash*.
