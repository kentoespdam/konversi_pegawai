---
name: Project Architecture & ETL Pattern
description: Arsitektur 3-layer ETL, modul inti, konvensi kode, helper functions, enums, dan alur eksekusi migration pipeline
type: project
---

## Arsitektur ETL 3-Layer

```
[1. Fetch/Source]          [2. Transform/v2]           [3. Save/Target]
core/smartoffice/*.py  →  v2/v2_N_*.py (cleanup)  →  core/kepegawaian/*.py
SELECT dari MySQL          Pandas DataFrame ops        INSERT/UPSERT ke MySQL
DB: smartoffice            mapping, casting, filter    DB: kepegawaian_migrasi
```

## Core Modules

### `core/config.py`
- **Connection pools**: Singleton pattern via `pymysqlpool.ConnectionPool`
  - smartoffice: size=5, maxsize=10
  - kepegawaian: size=5, maxsize=50, autocommit=False
- **Fetch**: `fetch_smartoffice(query, where)` / `fetch_kepegawaian(query, where)` → pd.DataFrame
- **Save**: `save_update_kepegawaian(query, data_list)` → executemany + commit/rollback
  - Disables `FOREIGN_KEY_CHECKS=0` sebelum operasi, restore di finally
- **Retry**: `@db_retry(max_retries=3, delay=1)` decorator pada semua fetch/save
- **LOGGER**: `logging.getLogger(__name__)`, level dari env `LOG_LEVEL`

### `v2/v2_helper.py`
| Fungsi | Signature | Kegunaan |
|--------|-----------|----------|
| `format_date_series` | `(s, default_date=False)` | → "YYYY-MM-DD", None jika NaT, opsional default "1945-08-17" |
| `format_datetime_series` | `(s)` | → "YYYY-MM-DD HH:MM:SS", None jika NaT |
| `log_duration` | `(prefix, start_time)` | Log elapsed time via LOGGER.info |
| `str_to_float` | `(x)` | String→float, handle empty/None/"-"/koma, default 0 |

### `core/enums.py` — Enum Mappings
| Enum | Values (key→value) |
|------|-----|
| EHubunganKeluarga | SUAMI=0, ISTRI=1, AYAH=2, IBU=3, ANAK=4, SAUDARA=5 |
| EJenisMutasi | PENGANGKATAN_PERTAMA=0, MUTASI_LOKER=1, MUTASI_JABATAN=2, MUTASI_GOLONGAN=3, MUTASI_GAJI=4, MUTASI_GAJI_BERKALA=5, TERMINASI=6 |
| EmpFlag | PegawaiTetap=1, PegawaiKontrak=2, NonPegawai=3, CalonPegawai=4, HonorerTetap=5, CalonHonorerTetap=6 |
| EStatusPegawai | KONTRAK=0, CAPEG=1, PEGAWAI=2, CALON_HONORER=3, HONORER=4, NON_PEGAWAI=5 |
| EmpWorkStatus | LamaranBaru=1 .. KaryawanAktif=6 .. BerhentiOrKeluar=8 |
| EStatusKerja | BERHENTI_OR_KELUAR=0 .. KARYAWAN_AKTIF=2 .. DITOLAK=7 |
| EJenisSk | SK_KENAIKAN_PANGKAT_GOLONGAN=0 .. SK_KENAIKAN_GAJI_BERKALA=8 |
| EJenisKontrak | PERPANJANGAN=0, PENGANGKATAN=1 |

### `core/post_data.py`
- `kirim_pegawai(data)`, `do_post(path, payload)`, `do_put(path, payload, id)`, `do_patch(path, payload)`
- HTTP client ke `API_URL` env var, gunakan icecream untuk debug

## Konvensi Kode

- **No ORM** — semua raw SQL via pymysql
- **DataFrame-centric** — data mengalir sebagai pd.DataFrame antar layer
- **Foreign key checks disabled** selama batch insert, restore di finally block
- **Default ID 0** untuk unmapped foreign key
- **`'SYSTEM'` atau `'DEV'`** sebagai created_by
- **`version=0`** di beberapa INSERT (tapi TIDAK semua tabel punya kolom version)
- **icecream (`ic`)** untuk debug, **LOGGER** untuk production logging
- **ON DUPLICATE KEY UPDATE** untuk upsert, beberapa tabel pakai REPLACE INTO (pegawai)

## Alur Eksekusi

```
main_v2.py → CleanupNikEmpProfile().run()  (NIK cleanup only)

Manual per-step:
python -m v2.v2_1_emp_profile_to_biodata
python -m v2.v2_2_employee_to_pegawai
... sampai v2_17
```

Script harus dijalankan berurutan (v2_1 → v2_17) karena ada dependensi FK.

## Environment
- `.env`: DB_HOST, DB_PORT, DB_USER, DB_PASS, DB_NAME (smartoffice), DB_NAME_KEPEGAWAIAN, LOG_LEVEL
- Dependencies: pymysql, pymysql-pool, pandas, numpy, python-dotenv, icecream
