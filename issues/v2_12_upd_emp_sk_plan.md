# Plan: Audit & Optimasi `v2_12_upd_emp_sk.py`

## Tujuan
Script ini memperbarui kolom referensi SK (`ref_sk_*`) dan kolom TMT terkait pada tabel `pegawai` (database `kepegawaian_migrasi`) berdasarkan data SK terbaru per pegawai dan jenis SK yang diambil dari tabel `riwayat_sk`.

Terdapat beberapa bug kritis dan potensi masalah yang perlu diperbaiki sebelum script ini aman dijalankan di production.

---

## Referensi Database

### Tabel Sumber: `riwayat_sk` (kepegawaian_migrasi)
Query yang digunakan oleh `fetch_latest_sk_by_pegawai()` mengambil SK terbaru per `(pegawai_id, jenis_sk)` menggunakan `ROW_NUMBER() OVER (PARTITION BY pegawai_id, jenis_sk ORDER BY tmt_berlaku DESC)`.

Kolom yang di-fetch:
| Kolom | Tipe | Contoh |
|---|---|---|
| `id` | bigint | `42` |
| `pegawai_id` | bigint | `1` |
| `jenis_sk` | tinyint | `0` (SK_KENAIKAN_PANGKAT_GOLONGAN), `1` (SK_CAPEG), `2` (SK_PEGAWAI_TETAP), `3` (SK_JABATAN), `4` (SK_MUTASI) |
| `nomor_sk` | varchar | `'823/238/2007'`, `'500/516/TAHUN 2021'` |
| `tmt_berlaku` | date | `'2007-04-01'`, `'2021-09-16'` |
| `kenaikan_berikutnya` | date | `None` (banyak NULL di data nyata) |

Total record: **2.337 baris** (hasil fetch nyata dari DB, sudah de-duplikasi per `pegawai_id + jenis_sk`).

Nilai `jenis_sk` yang ada di data: `[0, 1, 2, 3, 4, 5, 6, 7, 8]` (termasuk jenis yang tidak diproses oleh script).

### Tabel Target: `pegawai` (kepegawaian_migrasi)
Kolom yang akan diupdate oleh script:
| Kolom | Tipe | Diupdate oleh jenis SK |
|---|---|---|
| `ref_sk_capeg_id` | bigint | `SK_CAPEG` |
| `ref_sk_gol_id` | bigint | `SK_KENAIKAN_PANGKAT_GOLONGAN` |
| `tmt_golongan` | date | `SK_KENAIKAN_PANGKAT_GOLONGAN` |
| `ref_sk_jabatan_id` | bigint | `SK_JABATAN` |
| `tmt_jabatan` | date | `SK_JABATAN` |
| `ref_sk_mutasi_id` | bigint | `SK_MUTASI` |
| `tmt_mutasi` | date | `SK_MUTASI` |
| `ref_sk_pegawai_id` | bigint | `SK_PEGAWAI_TETAP` |
| `tmt_pegawai` | date | `SK_PEGAWAI_TETAP` |

> **Catatan:** `SK_CAPEG` hanya mengupdate `ref_sk_capeg_id` (tanpa TMT).
> Tidak ada kolom `tmt_capeg` di tabel `pegawai`.

### Enum `EJenisSk`
| Nama | Value |
|---|---|
| `SK_KENAIKAN_PANGKAT_GOLONGAN` | `0` |
| `SK_CAPEG` | `1` |
| `SK_PEGAWAI_TETAP` | `2` |
| `SK_JABATAN` | `3` |
| `SK_MUTASI` | `4` |

---

## Bug yang Ditemukan

### Bug 1 (KRITIS): Kolom `kenaikan_berikutnya` Di-format tapi Tidak Digunakan
**Lokasi:** Fungsi `main()` baris pemanggilan `format_datetime_series`.

Kolom `kenaikan_berikutnya` di-fetch dari DB dan diformat menggunakan `format_datetime_series()`, namun **tidak pernah dimasukkan ke dalam query UPDATE apapun** di `_generate_query_sk_capeg()`. Ini adalah dead code yang mengindikasikan kemungkinan kolom ini seharusnya ikut diupdate di tabel `pegawai` (misalnya untuk jenis `SK_KENAIKAN_PANGKAT_GOLONGAN`).

**Rekomendasi:**
- Audit tabel `pegawai`: apakah ada kolom `kenaikan_berikutnya`? Jalankan `DESCRIBE pegawai` dan cek.
- Jika kolom ada → tambahkan ke query UPDATE untuk jenis SK yang relevan.
- Jika kolom tidak ada → hapus baris `format_datetime_series` untuk `kenaikan_berikutnya` dari `main()` (dead code).

### Bug 2 (KRITIS): Tuple Mismatch Potensial di `update_sk_pegawai`
**Lokasi:** Fungsi `update_sk_pegawai()` di `core/kepegawaian/kepeg_pegawai.py`.

Fungsi ini membangun tuple dengan dua format berbeda:
- Untuk `SK_CAPEG`: `(row.id, row.pegawai_id)` — 2 elemen
- Untuk jenis lainnya: `(row.id, row.tmt_berlaku, row.pegawai_id)` — 3 elemen (menggunakan `tmt_berlaku`)

Masalahnya, `row.tmt_berlaku` di sini mengacu pada kolom `tmt_berlaku` dari DataFrame `riwayat_sk`, yang sudah diformat oleh `format_datetime_series()`. Perlu dipastikan nilai ini **tidak NULL** sebelum dipakai sebagai parameter UPDATE, karena kolom TMT di tabel `pegawai` tidak boleh bernilai NULL untuk data yang valid.

**Rekomendasi:**
- Tambahkan validasi/filter pada DataFrame sebelum update: drop baris dengan `tmt_berlaku` NULL untuk jenis selain `SK_CAPEG`.
- Log peringatan jika ada baris yang di-skip karena `tmt_berlaku` NULL.

### Bug 3 (SEDANG): Tidak Ada Error Handling
**Lokasi:** Fungsi `main()`.

Tidak ada blok `try-except` di `main()`. Jika terjadi error koneksi DB atau runtime error, script akan crash tanpa log terstruktur.

**Rekomendasi:**
- Bungkus seluruh isi `main()` dengan `try-except Exception as e` dan log error menggunakan `LOGGER.error(f"Migration failed: {e}", exc_info=True)`.
- Import `LOGGER` dari `core.config`.

### Bug 4 (SEDANG): Tidak Ada Record Count Logging
**Lokasi:** Fungsi `main()` dan loop per `jenis_sk`.

Tidak ada logging jumlah record yang diproses. Sulit untuk memvalidasi hasil eksekusi tanpa informasi ini.

**Rekomendasi:**
- Tambahkan `LOGGER.info(f"Fetched {len(df)} records from riwayat_sk.")` setelah fetch.
- Di dalam loop, tambahkan log jumlah record per `jenis_sk` yang berhasil diupdate.

### Bug 5 (RINGAN): Variable Shadowing di Loop
**Lokasi:** Fungsi `main()`, baris `for jenis_sk, df in sk_by_jenis.items()`.

Variabel `df` di dalam loop mengoverwrite variabel `df` di luar loop. Meskipun tidak merusak fungsionalitas saat ini, ini adalah code smell yang dapat menyebabkan bug sulit dilacak jika `main()` dikembangkan lebih lanjut.

**Rekomendasi:**
- Ganti nama variabel loop menjadi `df_jenis` atau serupa: `for jenis_sk, df_jenis in sk_by_jenis.items()`.

---

## Langkah Pengerjaan

### Persiapan
1. Baca dokumentasi best practice menggunakan **Context7** untuk:
   - Pattern pandas DataFrame handling dan NaN sanitization.
   - Pattern UPDATE query dengan pymysql.
   - Python logging best practices.
2. Pastikan kamu berada di direktori project dan gunakan Python dari: `./.venv/bin/python`
3. Baca file `memory/project_bug_patterns.md` untuk checklist audit standar project.

### Step 1: Audit Skema Tabel
Jalankan query berikut untuk memverifikasi struktur tabel target:
```
DESCRIBE pegawai;
```
Fokus pada: apakah ada kolom `kenaikan_berikutnya` di tabel `pegawai`?

### Step 2: Perbaiki Bug 1 — Dead Code `kenaikan_berikutnya`
- Berdasarkan hasil `DESCRIBE pegawai` di Step 1:
  - **Jika kolom ada:** Audit `_generate_query_sk_capeg()` di `core/kepegawaian/kepeg_pegawai.py` dan tambahkan `kenaikan_berikutnya` ke query UPDATE untuk jenis SK yang relevan. Pastikan tuple di `update_sk_pegawai()` juga diupdate.
  - **Jika kolom tidak ada:** Hapus baris `df["kenaikan_berikutnya"] = format_datetime_series(...)` dari `main()` karena merupakan dead code.

### Step 3: Perbaiki Bug 2 — Validasi `tmt_berlaku`
Di `main()`, sebelum memanggil `update_sk_pegawai()`, tambahkan filter untuk setiap DataFrame (selain `SK_CAPEG`) agar baris dengan `tmt_berlaku` bernilai NULL di-drop dan di-log sebagai warning.

### Step 4: Tambahkan Error Handling (Bug 3)
Bungkus seluruh isi `main()` dengan `try-except`. Import `LOGGER` dari `core.config` jika belum ada.

### Step 5: Tambahkan Logging Record Count (Bug 4)
- Setelah `fetch_latest_sk_by_pegawai()`, log jumlah total record.
- Di dalam loop per `jenis_sk`, log jumlah record yang akan diupdate dan durasi waktu proses (gunakan `log_duration` yang sudah diimport).

### Step 6: Perbaiki Variable Shadowing (Bug 5)
Rename variabel `df` di dalam loop menjadi nama yang tidak konflik dengan variabel outer scope.

### Step 7: Verifikasi
Jalankan script dengan perintah:
```bash
./.venv/bin/python -m v2.v2_12_upd_emp_sk
```
Pastikan:
- ✅ Tidak ada error atau traceback.
- ✅ Log menampilkan jumlah record yang diproses per jenis SK.
- ✅ Durasi per jenis SK ter-log dengan benar.
- ✅ Kolom `ref_sk_*` dan `tmt_*` pada tabel `pegawai` ter-update dengan benar (spot-check 3–5 record).

---

## Checklist Standar (dari `memory/project_bug_patterns.md`)
- [ ] Cek empty DataFrame guard → `if df.empty: return`
- [ ] Cek NaN/NaT sanitasi sebelum query (jika ada cleanup step)
- [ ] Cek error handling di `main()` (try-except + LOGGER)
- [ ] Cek record count logging
- [ ] Cek nilai NULL pada kolom FK/tmt sebelum UPDATE
- [ ] Cek tidak ada variable shadowing di loop
