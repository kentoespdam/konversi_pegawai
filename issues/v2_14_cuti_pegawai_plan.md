# Plan Audit, Perbaikan, dan Optimasi: `v2_14_cuti_pegawai.py`

Dokumen ini disusun sebagai panduan bagi Junior Developer atau AI Model untuk
memperbaiki dan mengoptimalkan script migrasi `v2_14_cuti_pegawai.py`
beserta pustaka pendukungnya (`core/smartoffice/eo_cuti_pegawai.py` dan
`core/kepegawaian/kepeg_cuti_pegawai.py`).

Sesuai dengan pedoman pengerjaan, **Wajib menggunakan Context 7** saat
mengimplementasikan langkah-langkah di bawah ini. Hal tersebut untuk memastikan
_best practice_ penulisan kode Python, penanganan exception, standar pemrosesan
Pandas, dan query SQL. Selalu jalankan environment menggunakan Python dari
dalam `.venv`.

## 1. Identifikasi Bug & Potensi Masalah

Berdasarkan penelusuran kode, ditemukan beberapa kelemahan pada skrip saat ini:

- **Ketidaksesuaian Skema Database (Kolom `version`)**: Pada berkas `core/kepegawaian/kepeg_cuti_pegawai.py`, terdapat upaya untuk menyimpan kolom `version` (diset 0) di SQL `INSERT` maupun `ON DUPLICATE KEY UPDATE`. Berdasarkan pengecekan *schema* tabel database `kepegawaian_migrasi.cuti_pegawai`, tidak ada eksistensi dari kolom `version`. Ini akan menyebabkan `SQL Syntax Error` seketika apabila eksekusi dijalankan.
- **Konversi Tipe Data Pandas NULL (`NaN`/`NaT`)**: Tidak ada tahapan memurnikan data *Null* tipe Pandas (`pd.NaT`, `np.nan`, tipe lainnya) di fungsi bersih utama (cleanup). Hal ini sangat rentan mengakibatkan *error* saat PyMySQL melakukan parameter *mapping* karena tak mengenal _Null_ tersebut.
- **Anomali pada Query `ON DUPLICATE KEY UPDATE`**: Query ini tidak pernah mengatur ulang nilai `updated_at=CURRENT_TIMESTAMP`. 
- **Minimnya Log Pengaman (Error Handling)**: Struktur main program sama sekali belum menampung pelacakan galat yang andal menggunakan blok _try-except_. Skandal operasional (hilangnya koneksi server, *missing param*, dll) dibiarkan merusak alur aplikasi tanpa *track record*.
- **Sanitasi Ketersediaan DataFrame**: Tidak ada pengecekan atau mekanisme _early exit_ apabila proses klausa `fetch` dari `eo_cuti_pegawai` me-return *DataFrame* tanpa data atau kosong. Memaksakan pengolahan akan menyuguhkan *error* baris di logika DataFrame selanjutnya.

## 2. Rekomendasi Perbaikan (Bug Fixes)

Berikut adalah tahap mitigasi teknis untuk kendala di atas:

1. **Sinkronisasi Schema Database**: Di dalam skrip penyimpan `save_cuti_pegawai`, secara eksplisit hapuskan penulisan baris tuple yang menambahkan angka `0` sebagai penanda akhir, hapus baris instruksi untuk list schema `version`, pun hilangkan _fallback_ SQL `version=VALUES(version)`. 
2. **Pemurnian Transformasi _Clean-Up_ Pandas NULL**: Setibanya di akhir fungsi konversi data (di berkas file python `_cleanup_claim`), injeksikan satu langkah proteksi dengan memanggil _mapper replace None_ (`.replace({np.nan: None, pd.NaT: None, pd.NA: None})`) sebelum mengirim *DataFrame* ke pemanggilnya.
3. **Modifikasi Klausa Update Waktu**: Lengkapi SQL Query baris ekor `ON DUPLICATE KEY UPDATE` dengan membubuhkan tag `updated_at=CURRENT_TIMESTAMP`.
4. **Enkapsulasi Galat Global**: Tutupi instrumen pemrosesan pengolah fungsi di bawah _main()_ ke dalam lingkup `try-except Exception as e:`.
5. **Proteksi Return Awal (Early Exit) DataFrame**: Taruhkan parameter penjamin di fase pertama proses `fetch`. Jika keadaannya *empty*, tembakkan pesan _log warning/info_ lalu lemparkan `return`.

## 3. Rekomendasi Optimasi Performa & Kerapian Kode

1. **Standardisasi Modul Import Logging**: Menghilangkan modul standar `time` dan mengoper _import library_ sentral proyek `LOGGER` bersama dengan `log_duration` atau elemen lainnya berbasis `core.config`.
2. **Rekaman Aktivitas Log Penuh**: Suguhkan instrumen log dengan melampirkan konfirmasi `len(df)` sehabis blok persetujuan _fetch_ maupun akhir fase klausa penyimpan (`save_cuti_pegawai`).

## 4. Langkah-Langkah Pengerjaan

Dokumen ini disusun sebagai instrumen _checklist_. Pedomani runtutan step
teknis berikut saat proses _fixing_ modul migrasi versi 14:

- [ ] **Aktivasi Environment & Referensi**: Posisikan di direktori _root_
  proyek dan login ke dalam virtual environment via `source .venv/bin/activate`.
  Selalu panggil rujukan berbasis **Context 7** untuk menyajikan best-practice pola solusi.
- [ ] **Perbaikan Fungsi Save Target (`core/kepegawaian/kepeg_cuti_pegawai.py`)**:
    - Usap/hapuskan frasa kolom penanda `version` dari klausa tuple (`0` angka), elemen `INSERT`, dari serangkaian parameter string MySQL, serta `ON DUPLICATE KEY UPDATE`.
    - Tambahkan set modifikasi `updated_at=CURRENT_TIMESTAMP` pada _block update duplikat_ yang bersinggungan.
- [ ] **Pengamanan Pembersihan Data DataFrame (`v2/v2_14_cuti_pegawai.py`)**: 
    - Tambahkan modul konversi nilai `NULL` dengan fungsi pemetaan ke nilai dasar _None_ (`replace({np.nan: ... })`) sebelum _return framework_ di fungsi `_cleanup_claim`.
- [ ] **Pengaman Penanganan Data dan Log (`v2/v2_14_cuti_pegawai.py`)**:
    - Terapkan objek `core.config.LOGGER`. Selubungi badan _try-catch_ keseluruhan proses logik fungsi main.
    - Implementasikan skema filter *DataFrame (empty return)* sehabis operan `fetch`.
- [ ] **Testing dan Assessment Terminal**: Uji finalisasi script menekan
  baris eksekusi `python -m v2.v2_14_cuti_pegawai`. Pantau kemunculan
  log durasi waktu migrasi dan jumlah akumulasi baris rekam kesuksesan lewat konsol.

> **Contoh Nilai Database Referensi (`smartoffice.cuti_pegawai`)**
> `cp_id` = 2
> `cp_type` = 1 (*Akan dimasukkan ke formula transform -1 untuk jenis pengajuan*)
> `cp_ref_id` = 0
> `cp_approved_at` = NULL
> `cp_work_days` = 3
> `cp_before` = 24
> `cp_after` = 21
> `cp_approval_status` = 4 (*Akan melintasi proses transform -1*)
