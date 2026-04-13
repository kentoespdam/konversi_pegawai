# Issue #001: Bug Fix — `set_nik_pegawai.py`

**Prioritas:** High  
**Modul:** `v2/set_nik_pegawai.py`  
**Tipe:** Bug Fix & Improvement  
**Tanggal:** 2026-04-13

---

## Latar Belakang

File `set_nik_pegawai.py` bertugas membersihkan data pegawai yang belum memiliki NIK (Nomor Induk Kependudukan). Script ini mengambil data pegawai tanpa NIK, mencocokkan dengan data kartu identitas (`emp_card`), lalu memperbarui kolom NIK di database.

Setelah dilakukan review, ditemukan beberapa bug dan potensi masalah yang perlu diperbaiki.

---

## Daftar Bug yang Ditemukan

### Bug 1: Tidak Ada Error Handling pada Operasi Database

**Masalah:** Semua fungsi yang mengakses database (`fetch_pegawai_without_nik`, `fetch_emp_cards_by_emp_codes`, `update_nik_emp_profile`) tidak memiliki blok `try/except`. Jika terjadi error saat koneksi database atau eksekusi query, program akan crash tanpa pesan error yang jelas dan tanpa rollback yang aman.

**Dampak:** Data bisa dalam kondisi tidak konsisten jika update gagal di tengah proses.

**Rekomendasi:** Tambahkan error handling dengan pola `try/except` yang sudah dipakai di modul v2 lainnya. Pastikan ada logging error dan rollback jika diperlukan.

---

### Bug 2: SQL Injection Melalui Pandas Query String

**Masalah:** Di method `_cleanup_nik_from_emp_card`, pencarian data menggunakan f-string langsung di dalam `DataFrame.query()`:
- `ec_list = self.emp_cards.query(f"emp_code == '{emp_code}'")`

Meskipun ini bukan SQL injection ke database, penggunaan f-string di dalam `DataFrame.query()` bisa menyebabkan error atau perilaku tak terduga jika nilai `emp_code` mengandung karakter khusus seperti tanda kutip.

**Dampak:** Program bisa crash jika data mengandung karakter khusus.

**Rekomendasi:** Gunakan variabel referensi `@variable` yang didukung oleh Pandas `query()`, atau gunakan metode filtering biasa dengan operator perbandingan (`==`).

---

### Bug 3: GROUP BY Tanpa Aggregasi yang Jelas

**Masalah:** Query di `fetch_pegawai_without_nik` menggunakan `GROUP BY ep.emp_profile_id` tapi memilih kolom dari tabel lain (`em.emp_code`) tanpa fungsi agregasi. Pada mode SQL strict, query ini akan error. Pada mode non-strict, hasilnya bisa tidak deterministik (nilai `emp_code` yang dikembalikan bisa acak jika ada duplikat).

**Dampak:** Bisa mengembalikan data yang salah atau error di server MySQL dengan konfigurasi strict.

**Rekomendasi:** Evaluasi apakah `GROUP BY` benar-benar diperlukan. Jika tujuannya menghindari duplikat, gunakan `DISTINCT` atau tambahkan fungsi agregasi yang tepat.

---

### Bug 4: Tidak Ada Validasi Data Sebelum Update

**Masalah:** Fungsi `update_nik_emp_profile` langsung melakukan update ke database tanpa memvalidasi apakah nilai `emp_identity_number` yang akan dimasukkan valid (misalnya: bukan string kosong, bukan None, format NIK benar).

**Dampak:** Data yang tidak valid bisa masuk ke database, menyebabkan masalah di sistem downstream.

**Rekomendasi:** Tambahkan validasi minimal sebelum update, misalnya pastikan `emp_identity_number` tidak kosong dan memiliki format yang wajar.

---

### Bug 5: Tipe Data Berubah Saat Assignment di DataFrame

**Masalah:** Di method `_cleanup_nik_from_emp_card`, assignment menggunakan `self.emp_without_nik.loc[idx, "emp_identity_type"] = KTP_IDENTITY_TYPE` pada DataFrame yang kolom `emp_identity_type`-nya bisa bertipe `float` (karena NULL dari database menjadi `NaN`). Pencampuran tipe integer dan float bisa menyebabkan masalah saat data dikirim ke database.

**Dampak:** Bisa menyebabkan error tipe data saat update ke database, atau menyimpan nilai float (misalnya `4.0` alih-alih `4`).

**Rekomendasi:** Konversi kolom ke tipe integer yang tepat sebelum melakukan update, atau gunakan `pd.Int64Dtype()` yang mendukung nullable integer.

---

### Bug 6: Log Message yang Menyesatkan

**Masalah:** Setelah proses cleanup, log menampilkan pesan `"Found {count} with NIK"` menggunakan jumlah total baris, bukan jumlah baris yang berhasil dicocokkan NIK-nya. Pesan ini menyesatkan karena mengesankan semua pegawai sudah mendapat NIK yang benar.

**Dampak:** Monitoring dan debugging menjadi sulit karena log tidak akurat.

**Rekomendasi:** Perbaiki pesan log agar mencerminkan kondisi sebenarnya, misalnya berapa yang dicocokkan dari `emp_card` vs berapa yang di-fallback ke `emp_code`.

---

## Langkah-Langkah Pengerjaan

### Tahap 1: Persiapan

1. Buat branch baru dari branch `BUG-FIX-OPTIMIZE-V2`, misalnya `fix/set-nik-pegawai`.
2. Pastikan environment sudah aktif (`source .venv/bin/activate`).
3. Jalankan test yang ada untuk memastikan kondisi awal: `python -m pytest tests/`.

### Tahap 2: Riset Best Practice

Gunakan **Context7** untuk mencari referensi dan best practice:

1. **Pandas DataFrame filtering** — cari cara terbaik untuk filtering DataFrame tanpa f-string di `query()`. Gunakan query: *"Pandas DataFrame filter rows by column value safely"*.
2. **Pandas nullable integer** — cari cara menangani kolom integer dengan NaN. Gunakan query: *"Pandas nullable integer type Int64"*.
3. **PyMySQL error handling** — cari pola error handling yang benar untuk PyMySQL. Gunakan query: *"PyMySQL execute error handling and rollback"*.

### Tahap 3: Perbaikan Bug (Kerjakan Berurutan)

1. **Perbaiki error handling** (Bug 1)
   - Tambahkan `try/except` di setiap fungsi database.
   - Pastikan ada rollback pada fungsi update jika terjadi error.
   - Log error dengan level `LOGGER.error()`.

2. **Perbaiki DataFrame query** (Bug 2)
   - Ganti semua penggunaan f-string di `DataFrame.query()` dengan metode filtering standar Pandas (misalnya: `df[df["kolom"] == nilai]`).

3. **Perbaiki SQL query** (Bug 3)
   - Evaluasi kebutuhan `GROUP BY`. Jika hanya butuh data unik, ganti dengan `DISTINCT` atau perbaiki query agar sesuai standar SQL strict.

4. **Tambahkan validasi data** (Bug 4)
   - Tambahkan pengecekan sebelum update: pastikan `emp_identity_number` tidak kosong/None.
   - Log jumlah baris yang dilewati karena tidak valid.

5. **Perbaiki tipe data** (Bug 5)
   - Konversi kolom `emp_identity_type` ke tipe integer sebelum dikirim ke database.
   - Gunakan `.astype(int)` atau `pd.Int64Dtype()` sesuai kebutuhan.

6. **Perbaiki log message** (Bug 6)
   - Buat log yang membedakan: berapa yang NIK-nya dari `emp_card`, berapa yang fallback ke `emp_code`.

### Tahap 4: Testing

1. Buat atau perbarui unit test di `tests/test_set_nik_pegawai.py`.
2. Test harus mencakup:
   - Pegawai tanpa NIK dan tanpa data kartu → fallback ke `emp_code`.
   - Pegawai tanpa NIK tapi punya kartu KTP → ambil dari kartu.
   - Pegawai tanpa NIK, punya kartu tapi bukan KTP → fallback ke `emp_code`.
   - Data kosong (tidak ada pegawai tanpa NIK).
   - `emp_code` mengandung karakter khusus.
3. Jalankan semua test: `python -m pytest tests/ -v`.

### Tahap 5: Review & Commit

1. Review semua perubahan: `git diff`.
2. Pastikan tidak ada perubahan yang merusak fungsionalitas lain.
3. Commit dengan pesan yang jelas, contoh: `fix: perbaikan bug pada set_nik_pegawai`.
4. Buat Pull Request ke branch `v2`.

---

## Kriteria Selesai

- [ ] Semua 6 bug sudah diperbaiki.
- [ ] Tidak ada penggunaan f-string di `DataFrame.query()`.
- [ ] Error handling tersedia di semua fungsi database.
- [ ] Unit test tersedia dan semua passing.
- [ ] Log message akurat dan informatif.
- [ ] Code review sudah dilakukan.
