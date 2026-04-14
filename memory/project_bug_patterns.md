---
name: Common Bug & Optimization Patterns
description: Pola bug berulang di v2 scripts dan pola optimasi standar yang sudah diterapkan di v2_1-v2_6
type: project
---

## Bug Berulang (ditemukan di hampir setiap v2 script sebelum optimasi)

### 1. DataFrame Kosong Tanpa Guard
**Masalah**: Tidak ada `if df.empty: return` setelah fetch → error saat cleanup/save
**Fix**: Tambahkan early exit + LOGGER.info setelah fetch

### 2. Pandas NULL Tidak Disanitasi
**Masalah**: `NaN`, `NaT`, `pd.NA` dari pandas dikirim ke pymysql → SQL error atau data corrupt
**Fix**: `df.replace({np.nan: None, pd.NaT: None, pd.NA: None})` sebelum return dari cleanup

### 3. Flag `disetujui` Hardcoded
**Masalah**: Boolean `disetujui` diset statis `True` di SQL atau save function
**Fix**: Dynamic di cleanup: `df["disetujui"] = df["tanggal_disetujui"].notnull()`

### 4. ON DUPLICATE KEY UPDATE Tidak Lengkap
**Masalah**: Hanya update `biodata_id=VALUES(biodata_id)` (redundan, PK/UK) — kolom lain tidak terupdate
**Fix**: Update SEMUA kolom atribut + tambah `updated_at=CURRENT_TIMESTAMP`

### 5. Tidak Ada Error Handling
**Masalah**: Tanpa try-except di main() → crash tanpa log terstruktur
**Fix**: Global try-except + `LOGGER.error(f"...: {e}", exc_info=True)`

### 6. Tidak Ada Record Count Logging
**Masalah**: Tidak tahu berapa record di-fetch/di-save
**Fix**: `LOGGER.info(f"Fetched {len(df)} records")` setelah fetch, dan setelah save

### 7. Kolom Target Tidak Terisi Lengkap
**Masalah**: Kolom seperti `tanggal_pengajuan`, `tanggal_disetujui`, `disetujui_oleh` di-fetch tapi tidak di-INSERT
**Fix**: Tambahkan ke INSERT + tuple data + ON DUPLICATE KEY UPDATE

### 8. INNER JOIN Menghilangkan Data
**Masalah**: INNER JOIN dengan tabel referensi → record tanpa mapping hilang
**Fix**: Ganti ke LEFT JOIN, terima NULL untuk kolom referensi

### 9. Kolom `approve_by` / `disetujui_oleh` Tidak Di-fetch
**Masalah**: Tabel source punya `approve_by` tapi query tidak SELECT
**Fix**: Tambahkan `ew.approve_by AS disetujui_oleh` di SELECT

### 10. Kolom `version` Mismatch
**Masalah**: INSERT menyertakan `version=0` padahal tabel target mungkin tidak punya kolom version
**Fix**: Verifikasi schema target (DESCRIBE table) sebelum INSERT. Hapus jika tidak ada.

### 11. Tabel Tanpa Unique Key → Duplikasi
**Masalah**: ON DUPLICATE KEY UPDATE tidak berfungsi karena tabel hanya punya PK auto-increment
**Fix**: TRUNCATE sebelum INSERT, atau koordinasi DBA untuk tambah unique constraint

### 12. Nilai Integer 0 Tidak Disanitasi
**Masalah**: Tahun=0, ID=0 dari source dikirim apa adanya (semantik invalid)
**Fix**: `.replace(0, None)` untuk kolom tahun; untuk FK, `row.field if row.field > 0 else None`

## Pola Optimasi Standar (sudah diterapkan v2_5/v2_6)

### Struktur main() Teroptimasi
```
import traceback, numpy as np
from core.config import LOGGER

def main():
    try:
        start_time = time.time()
        df = fetch_xxx()
        if df.empty:
            LOGGER.info("No data found. Skipping.")
            return
        LOGGER.info(f"Fetched {len(df)} records.")
        df = cleanup(df)
        log_duration("generating data finished", start_time)

        start_time = time.time()
        save_xxx(df)
        LOGGER.info(f"Successfully processed {len(df)} records.")
        log_duration("posting data finished", start_time)
    except Exception as e:
        LOGGER.error(f"Migration failed: {e}", exc_info=True)
```

### Struktur cleanup() Teroptimasi
```
def cleanup(df):
    # 1. Dynamic boolean flags
    df["disetujui"] = df["tanggal_disetujui"].notnull()
    # 2. Date formatting (centralized via v2_helper)
    df["tanggal_pengajuan"] = format_datetime_series(df["tanggal_pengajuan"])
    df["tanggal_disetujui"] = format_datetime_series(df["tanggal_disetujui"])
    # 3. Boolean/int conversion (vectorized)
    df["is_deleted"] = df["is_deleted"].eq(1)
    # 4. Dict mapping untuk FK (jika perlu)
    # mapping = dict(zip(master_df["nama"], master_df["id"]))
    # df["fk_id"] = df["nama_col"].map(mapping).fillna(0).astype(int)
    # 5. NaN/NaT sanitization (TERAKHIR, sebelum return)
    df = df.replace({np.nan: None, pd.NaT: None, pd.NA: None})
    return df
```

### Struktur save() Teroptimasi
```
INSERT INTO target (col1, col2, ..., created_by)
VALUES (%s, %s, ..., %s)
ON DUPLICATE KEY UPDATE
    col1=VALUES(col1),
    col2=VALUES(col2),
    ...,
    updated_at=CURRENT_TIMESTAMP
```
- Tuple dari `df.itertuples(index=False)`
- FK handling: `row.fk_id if row.fk_id > 0 else None`
- Selalu `created_by='SYSTEM'`

## Checklist Audit Script Baru
Gunakan checklist ini saat mengaudit v2_8+:
1. [ ] Cek schema target: `DESCRIBE <table>` — kolom apa saja, ada unique key?
2. [ ] Cek JOIN type di fetch: INNER vs LEFT — apakah ada data loss?
3. [ ] Cek kolom fetch vs kolom INSERT: match?
4. [ ] Cek ada kolom `approve_by`/`disetujui_oleh` di source?
5. [ ] Cek ada kolom `version` di target? Jika tidak, hapus dari INSERT
6. [ ] Cek empty DataFrame guard
7. [ ] Cek NaN/NaT sanitization
8. [ ] Cek dynamic `disetujui` logic
9. [ ] Cek ON DUPLICATE KEY UPDATE lengkap + `updated_at=CURRENT_TIMESTAMP`
10. [ ] Cek error handling (try-except + LOGGER)
11. [ ] Cek record count logging
12. [ ] Cek nilai 0 pada kolom tahun/FK
