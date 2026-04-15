# Rencana Audit dan Optimasi: `v2/v2_helper.py`

## Latar Belakang
File `v2/v2_helper.py` merupakan _module_ utilitas berisi fungsionalitas pendukung untuk pemrosesan DataFrames pada project migrasi, melingkupi format serial tanggal (`format_date_series`, `format_datetime_series`), pengukuran waktu `log_duration`, dan konversi angka (`str_to_float`). Skrip ini perlu diaudit untuk memastikan bahwa tidak ada fungsionalitas turunan skalar yang membebani kinerja operasi Pandas (`df.apply()`), serta memastikan ketahanan handling data `Null` / kosong untuk persiapan penulisan raw SQL di _layer_ selanjutnya.

## Panduan Pengerjaan Utama

- **Gunakan _Virtual Environment_:** Wajib eksekusi semua skrip menggunakan Python dari `./.venv/bin/python`.
- **Gunakan Context 7:** Wajib menanyakan `Context 7` untuk mendapatkan _best practice_ pemrosesan *vectorized operations* di ekosistem Pandas terkini, terutama pengganti konversi string scalar menjadi tipe matriks seri (Series).
- **Gunakan All Available Skills:** Pahami aturan project dari panduan _Memory_ / dokumentasi arsitektur di sistem untuk `Pandas usage`, error logging, dan `NaN sanitization`.
- **Berpikir pada Level High-Level (Tanpa Menulis Kode Rinci di Sini):** Dokumen ini adalah penunjuk jalan logis. AI Agent / Junior dev harus merancang implementasinya di kode utama dan mengujinya sendiri.

## Langkah-Langkah (Action Plan)

### 1. Audit dan Vectorization Fungsi `str_to_float`
- **Target Masalah (Bug Identified):**
  - Fungsi `str_to_float(x: str)` yang ada saat ini merupakan fungsi skalar (*row-by-row operation*). Apabila sebuah dataset berisi jutaan _record_, pemanggilan fungsi ini pada level baris akan mengurangi kinerja yang signifikan.
- **Rekomendasi Perbaikan:**
  - Buat atau perbarui pendekatan fungsi ini ke skala *full vectorized Pandas Series* (contoh menerima argumen `s: pd.Series` ketimbang `x: str`).
  - Gunakan fungsionalitas `.str.replace(',', '.')` dsb, untuk membersihkan pola karakter _missing_ (seperti `"-"` atau `""`) ke dalam komputasi matriks (*vectorized string operation*), kemudian _cast_ tipe menggunakan `pd.to_numeric(s, errors='coerce')` atau dispesifikasikan pengisian `.fillna(0)`.
  - Jika diperlukan _error logging_, log baris kolom yang tidak tervalidasi alih-alih me-log satu per satu _value string_ dengan blok _try-except_.

### 2. Audit Konversi Waktu `format_date_series` & `format_datetime_series`
- **Target Masalah:**
  - `pd.to_datetime(s, errors="coerce")` sangat umum, tapi dapat menyebabkan limitasi peforma apabila input format di database sangat bervariasi (*mixed formatting*).
- **Rekomendasi Perbaikan:**
  - Pastikan bahwa return dari utilitas *date*, apabila valid, aman dikoversi kembali ke `Pymysql` sebagai `None` utuh ketika kondisi tak valid (jangan sampai kembalian berjenis numpy `NaT` atau string `"NaT"`).
  - Tinjau apakah perlu menyertakan _inference format_ date di Pandas atau parameter opsional bagi tanggal-tanggal default spesifik.

### 3. Sanitasi Tipe Data & Standar Logging
- Pastikan standard logging menggunakan instruksi _project formatting_: modul error logging merespon secara konklusif kepada operasi batch yang gagal diparsing tanpa mencetak *spam messages*.
- `log_duration(prefix: str, start_time: float)` di module sudah cukup baik; pertahankan untuk profil operasi _batch-size_ yang besar.

## Referensi Data (Contoh Value yang Sering Digunakan)

Sebagai bantuan agar developer/AI tipe turunan tak perlu mem-fetch ulang pada database, contoh nilai dari `smartoffice` yang biasanya di-handle `v2_helper.py`:

**Format Date / Datetime Column:**
- `None`, `""` : _Empty String/NULL_ -> Diharapkan menjadi `None` saat penulisan sql, (atau dikonversi ke tanggal pas standar default bila _flagging default=True_ aktif misalnya `"1945-08-17"`).
- `"2020-05-15 11:22:33"` : Tanggal terisi penuh -> Bisa diparsing aman oleh format tanggal.

**String / Numeric (Gaji dsb. jika ada pemanggilan string):**
- `"-"` : Data yang dikosongi dengan format teks strip -> Diharapkan dikoersikan ke nol (0) atau _NULL_ numerik.
- `""` : Teks kosong murni.
- `"1.250.500,50"` / `"1500,50"` : Penggunaan _separator_ gaya ribuan atau koma (*European Decimal Pattern* umumnya ditemukan di sistem indo). (Ganti koma menjadi tipe Float standar ANSI).

## Target Kriteria Selesai (Acceptance Criteria)

- [ ] `v2_helper.py` diperbarui sepenuhnya menjadi _vectorized-first_ untuk semua fungsi konversi tipe datanya.
- [ ] Menggunakan panduan _Context 7_ pada tahapan modifikasi, terutama saat menstrukturkan penggantian `str_to_float(x)`.
- [ ] Pengujian manual dilakukan sebelum penutupan PR atau commit; setiap rujukan skrip (contoh perbandingan jika ia dipakai pada `v2_8`, `v2_9`, dst) jika berdampak harus diproteksi dengan fungsi kompatibel.
- [ ] Menyertakan dokumentasi penanganan input parameter tak terduga (*Edge Case input*), menggunakan _docstrings_ di Python.
