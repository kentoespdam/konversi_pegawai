# Konversi Pegawai

Tool ETL/migrasi data untuk mengkonversi data pegawai dari database legacy **SmartOffice** (MySQL) ke sistem kepegawaian modern **Kepegawaian**.

## Tech Stack

- **Python 3** + **Pandas** - Manipulasi & transformasi data berbasis DataFrame
- **PyMySQL** + **pymysqlpool** - Koneksi MySQL dengan connection pooling
- **Dask** - Parallel processing untuk konversi data skala besar
- **AppWrite SDK** - Manajemen akun user
- **icecream** - Debug output

## Prerequisites

- Python 3.10+
- MySQL Server dengan akses ke database `smartoffice` (source) dan `kepegawaian_migrasi` (target)
- File `.env` untuk konfigurasi koneksi database

## Instalasi

```bash
# Clone repository
git clone <repo-url>
cd konversi_pegawai

# Buat virtual environment
python -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

## Konfigurasi

Buat file `.env` di root project:

```env
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASS=password
DB_NAME=smartoffice
DB_NAME_KEPEGAWAIAN=kepegawaian_migrasi

# Optional: URL API eksternal untuk push data pegawai
API_URL=http://localhost:8000/api
```

## Arsitektur

Project mengikuti pola **Three-Layer ETL**:

```
SmartOffice DB          Transform (v2/)          Kepegawaian DB
┌─────────────┐     ┌───────────────────┐     ┌──────────────────┐
│ core/       │     │ v2_1 ~ v2_17      │     │ core/            │
│ smartoffice/│ ──> │ Map, clean, join   │ ──> │ kepegawaian/     │
│ (fetch)     │     │ DataFrame ops      │     │ (save/update)    │
└─────────────┘     └───────────────────┘     └──────────────────┘
```

### Core Modules

| Module              | Fungsi                                                                                       |
|---------------------|----------------------------------------------------------------------------------------------|
| `core/config.py`    | Connection pool & fungsi `fetch_smartoffice`, `fetch_kepegawaian`, `save_update_kepegawaian` |
| `core/enums.py`     | Mapping enum antara kode source & target (status pegawai, jenis SK, dll)                     |
| `core/post_data.py` | HTTP POST utility untuk push data ke API eksternal                                           |
| `core/smartoffice/` | Query SELECT dari database SmartOffice (source)                                              |
| `core/kepegawaian/` | Query INSERT/UPDATE ke database Kepegawaian (target)                                         |
| `v2/v2_helper.py`   | Utility transformasi: format tanggal, durasi log, konversi tipe                              |

## Script Migrasi

Script dijalankan secara berurutan dari `v2_1` sampai `v2_17`:

| Script | Source                   | Target                        | Keterangan                              |
|--------|--------------------------|-------------------------------|-----------------------------------------|
| v2_1   | `emp_profile`            | `biodata` + `kartu_identitas` | Profil pegawai & kartu identitas        |
| v2_2   | `employee`               | `pegawai`                     | Data utama pegawai                      |
| v2_3   | `emp_card`               | `kartu_identitas`             | Kartu identitas (KTP, SIM, dll)         |
| v2_4   | `emp_skill`              | `keahlian`                    | Keahlian pegawai                        |
| v2_5   | `emp_training`           | `pelatihan`                   | Riwayat pelatihan                       |
| v2_6   | `emp_education`          | `pendidikan`                  | Riwayat pendidikan                      |
| v2_7   | `emp_work_experience`    | `pengalaman_kerja`            | Pengalaman kerja sebelumnya             |
| v2_8   | `emp_family`             | `profil_keluarga`             | Data keluarga                           |
| v2_9_1 | `riwayat_sk`             | `emp_sk`                      | Inisialisasi SK dari riwayat (opsional) |
| v2_9_2 | `emp_sk`                 | `riwayat_sk`                  | Riwayat Surat Keputusan                 |
| v2_10  | `emp_work_history`       | `riwayat_mutasi`              | Riwayat mutasi                          |
| v2_11  | `emp_contract`           | `riwayat_kontrak`             | Riwayat kontrak                         |
| v2_12  | -                        | `emp_sk` (update)             | Update referensi SK per jenis           |
| v2_13  | `eo_cuti_kuota`          | `cuti_kuota`                  | Kuota cuti                              |
| v2_14  | `eo_cuti_pegawai`        | `cuti_pegawai`                | Pengajuan cuti                          |
| v2_15  | `eo_cuti_approval_chain` | `cuti_approval_chain`         | Rantai approval cuti                    |
| v2_16  | `eo_cuti_approval`       | `cuti_approval`               | Approval cuti                           |
| v2_17  | `eo_cuti_pegawai_detail` | `cuti_klaim_detail`           | Detail klaim cuti                       |

### Script Pendukung

| Script                    | Keterangan                                                          |
|---------------------------|---------------------------------------------------------------------|
| `v2_master_gaji.py`       | Migrasi master data gaji (tunjangan, PTKP, parameter, potongan TKK) |
| `v2_master_organisasi.py` | Sinkronisasi data organisasi                                        |
| `set_nik_pegawai.py`      | Pembersihan NIK pegawai yang belum terisi                           |
| `update_phdp_pegawai.py`  | Update PHDP dan ID perumahan pada data pegawai                      |

## Penggunaan

### Menjalankan Semua Migrasi (Berurutan)

```bash
source .venv/bin/activate

# 1. Cleanup NIK
python main_v2.py

# 2. Jalankan migrasi satu per satu
python -m v2.v2_1_emp_profile_to_biodata
python -m v2.v2_2_employee_to_pegawai
python -m v2.v2_3_emp_card_to_kartu_identitas
python -m v2.v2_4_emp_skill_to_keahlian
python -m v2.v2_5_emp_training_to_pelatihan
python -m v2.v2_6_emp_education_to_pendidikan
python -m v2.v2_7_emp_work_experience_to_pengalaman_kerja
python -m v2.v2_8_emp_family_to_profil_keluarga
python -m v2.v2_9_1_init_emp_sk_from_riwayat_sk_optional
python -m v2.v2_9_2_emp_sk_to_riwayat_sk
python -m v2.v2_10_emp_work_history_to_riwayat_mutasi
python -m v2.v2_11_emp_contract_to_riwayat_kontrak
python -m v2.v2_12_upd_emp_sk
python -m v2.v2_13_cuti_kuota
python -m v2.v2_14_cuti_pegawai
python -m v2.v2_15_cuti_approval_chain
python -m v2.v2_16_cuti_approval
python -m v2.v2_17_cuti_klaim_detail

# 3. Master data
python -m v2.v2_master_gaji
python -m v2.v2_master_organisasi
```

### Konversi Paralel dengan Dask

```bash
python emp_to_pegawai.py
```

### Manajemen User AppWrite

```bash
# Buat akun user dari data pegawai
python -m app_write.create_users

# Hapus akun user
python -m app_write.delete_users
```

## Testing

```bash
# Jalankan semua test
python -m pytest tests/

# Jalankan test spesifik
python -m pytest tests/test_v2_1_emp_profile_to_biodata.py
```

## Struktur Project

```
konversi_pegawai/
├── core/
│   ├── config.py                  # Koneksi DB & fungsi shared
│   ├── enums.py                   # Mapping enum source-target
│   ├── post_data.py               # HTTP POST utility
│   ├── kepegawaian/               # Data access layer (target)
│   └── smartoffice/               # Data access layer (source)
├── v2/
│   ├── v2_helper.py               # Utility transformasi
│   ├── v2_1 ~ v2_17               # Script migrasi berurutan
│   ├── v2_master_gaji.py          # Master data gaji
│   ├── v2_master_organisasi.py    # Master data organisasi
│   ├── set_nik_pegawai.py         # Cleanup NIK
│   └── update_phdp_pegawai.py     # Update PHDP
├── app_write/                     # Integrasi AppWrite
├── tests/                         # Unit & integration tests
├── main_v2.py                     # Entry point (cleanup NIK)
├── emp_to_pegawai.py              # Konversi paralel dengan Dask
├── requirements.txt               # Dependencies
└── .env                           # Konfigurasi database (tidak di-commit)
```

## Konvensi

- **Tanpa ORM** - Semua akses database menggunakan raw SQL dengan PyMySQL
- **DataFrame-centric** - Data mengalir sebagai `pd.DataFrame` antar layer
- **Enum mapping** - Kode source ditranslasi ke target via enum di `core/enums.py`
- **Foreign key check dinonaktifkan** saat batch insert (`SET FOREIGN_KEY_CHECKS=0`)
- **Default ID 0** untuk data referensi yang tidak ter-mapping
- **icecream (`ic`)** untuk debug output
