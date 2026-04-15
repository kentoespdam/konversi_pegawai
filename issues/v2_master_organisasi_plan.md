# Rencana Migrasi Master Organisasi (`v2_master_organisasi.py`)

## Tujuan
Melakukan audit, perbaikan bug, dan optimasi performa pada script migrasi `v2/v2_master_organisasi.py` serta file modul dependency-nya yaitu `core/kepegawaian/kepeg_organisasi.py`. Dokumen ini menjadi pedoman utama pengerjaan untuk AI model atau junior developer.

## Temuan Bug & Issue
1. **Fungsi Hilang (Syntax Error):** Pada `core/kepegawaian/kepeg_organisasi.py`, definisi penutup untuk fungsi `def update_organisasi_from_organization(df):` terhapus atau tidak sengaja tertimpa. Pemrosesan `data = [...]` dan `query` saat ini langsung diletakkan di module root level, yang dapat memicu `ImportError` atau merusak _flow_ saat script di-*import*.
2. **Tidak Idempotent (Risiko Kehilangan Insert Baru):** Query di dalam `kepeg_organisasi.py` saat ini menggunakan *pure* `UPDATE`. Ini berarti apabila ada entri organisasi baru yang ditambahkan di *smartoffice*, script ini akan gagal menyimpannya ke database *kepegawaian*. Script wajib menggunakan format **Upsert** (`INSERT ... ON DUPLICATE KEY UPDATE`).
3. **Sanitasi Nilai `NaN` ke `None`:** Data String yang rentan berisi *NaN/Null* seperti `category` tidak secara eksplisit di-replace menjadi `None` murni. Hal ini akan memicu *DataError* pada library pymysql.
4. **Tipe Data Boolean:** Konversi operan `df["org_status"].ne("Enabled")` akan menghasilkan tipe *Boolean* primitif pandas. Sebaiknya dilakukan *casting* paksa ke bentuk *integer* agar konsisten dengan `TINYINT(1)` di database MySQL.

## Rekomendasi Perbaikan & Optimasi
1. Rapikan struktur file `core/kepegawaian/kepeg_organisasi.py` agar pembentukan variabel `query` dan `data` berada sepenuhnya di dalam *scope* fungsi `update_organisasi_from_organization()`.
2. Ubah Statement SQL menjadi query **Upsert** (`ON DUPLICATE KEY UPDATE`). Pastikan urutan parameter mapping `data` dievaluasi ulang untuk match dengan argumen `%s`.
3. Di dalam fungsi `_cleanup` pada `v2_master_organisasi.py`:
   - Konversikan `is_deleted` ke tipe data integer secara eksplisit (`astype(int)`).
   - Terapkan Pandas Sanitasi untuk kolom-kolom string seperti mengganti nilai `np.nan` menjadi string kosong `""` atau pure `None`.
4. Tambahkan validasi penanganan dataframe kosong (misal: `if df.empty: return`) untuk memotong pemrosesan di awal apabila sumber data tidak mengembalikan row satupun.

## Sampel Data Database Referensi
Berikut adalah referensi shape objek row per table (untuk mencegah kebutuhan _fetch_ yang berulang):

**Source (SmartOffice - `organization`):**
```json
[
  {
    "org_id": 1, "org_code": "DPW", "org_name": "DEWAN PENGAWAS", 
    "org_status": "Enabled", "mail_code": "", "category": null
  },
  {
    "org_id": 2, "org_code": "D1", "org_name": "DIREKTORAT UTAMA", 
    "org_status": "Enabled", "mail_code": "DIR", "category": "ADM"
  }
]
```

**Target (Kepegawaian - `organisasi`):**
```json
[
  {
    "id": 1, "nama": "DEWAN PENGAWAS", "short_name": "", 
    "category": null, "is_deleted": 0
  },
  {
    "id": 2, "nama": "DIREKTORAT UTAMA", "short_name": "DIR", 
    "category": "ADM", "is_deleted": 0
  }
]
```

## Langkah-Langkah Eksekusi
1. **Persiapan Virtual Environment:** Pastikan selalu menggunakan environment python internal project pada alamat `./.venv/bin/python`.
2. **Perbaikan Syntax Core:** Buka file `core/kepegawaian/kepeg_organisasi.py`, buat ulang blok penutup untuk definisi fungsi `update_organisasi_from_organization(df: pd.DataFrame)` dan rapikan indentasi baris-baris *statement query* MySQL dan mapping `data` ke dalam function body tersebut.
3. **Update Query Idempotency:** Modifikasi deklarasi _raw string_ variable `query` menjadi berformat *Upsert* (menangani `INSERT` yang di back-up `ON DUPLICATE KEY UPDATE`).
   - Contoh mapping `INSERT INTO organisasi (id, nama, short_name, category, is_deleted) VALUES (%s, %s, %s, %s, %s) ON DUPLICATE KEY UPDATE nama = VALUES(nama), short_name = VALUES(short_name), ...`
   - Sesuaikan urutan tuple assignment pada blok list/iterator baris `data = [...]` karena format query pastinya akan menuntut letak bind value `%s` yang berbeda.
4. **Optimasi Cleanup:** Buka file utama di `v2/v2_master_organisasi.py`, modifikasi blok fungsi `_cleanup(df)`:
   - *Cast pipeline:* Tambahkan casting integer untuk operasi boolean ke tipe boolean MySQL primitif.
   - Bersihkan nilai Pandas Null / *NaN* menjadi murni `None` sebelum masuk ke fase insert.
   - Import dan gunakan `numpy as np` (jika memanfaatkan `replace(np.nan, None)`) atau pakai fitur pandas standar (`df = df.where(pd.notnull(df), None)`).
5. **Quality Control & Best Practices:** Evaluasi solusi terakhir dengan panduan **Context 7** standar dari proyek - pastikan iterasi tuple menggunakan `df.itertuples(index=False)` sehingga pertukaran array ke pymysql tetap optimal.
6. **Testing Validation:** Coba eksekusi kode menggunakan perintah migrasi `./.venv/bin/python -m v2.v2_master_organisasi`. Periksa log konsole untuk mensertifikasi bahwasanya proses sinkronisasi telah sukses, durasi berjalan efisien, dan data ter-update aman.
