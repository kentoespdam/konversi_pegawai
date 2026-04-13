# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

ETL/data migration tool that converts employee data from a legacy **smartoffice** MySQL database to a modern **kepegawaian** (HR) system. Written in Python using Pandas DataFrames and raw SQL via PyMySQL with connection pooling.

## Commands

```bash
# Activate virtual environment
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run main entry point (NIK cleanup)
python main_v2.py

# Run a specific migration step
python -m v2.v2_1.emp_profile_to_biodata
python -m v2.v2_2.employee_to_pegawai
# ... through v2_17

# Run employee-to-pegawai conversion with Dask parallel processing
python emp_to_pegawai.py

# Run tests
python -m pytest tests/

# Run a single test
python -m pytest tests/test_main_v2.py
```

## Architecture

### Three-Layer ETL Pattern

1. **Fetch (source)** - `core/smartoffice/` - SELECT queries against the smartoffice database returning DataFrames
2. **Transform** - `v2/` - Numbered migration scripts (v2_1 through v2_17) that map, clean, and join data
3. **Save (target)** - `core/kepegawaian/` - INSERT/UPDATE operations against the kepegawaian_migrasi database

### Core Modules

- `core/config.py` - Database connection pools and shared fetch/save functions (`fetch_smartoffice`, `fetch_kepegawaian`, `save_update_kepegawaian`). All DB access flows through here.
- `core/enums.py` - Enum-based mappings between source and target system codes (status_pegawai, status_kerja, jenis_sk, etc.)
- `core/post_data.py` - HTTP POST utility for pushing data to an external API (uses `API_URL` env var)
- `v2/v2_helper.py` - Shared transformation utilities used across migration steps

### Migration Script Ordering

Scripts in `v2/` are numbered sequentially (v2_1, v2_2, ..., v2_17) and should run in order. Each script handles one entity migration:
- v2_1: emp_profile -> biodata
- v2_2: employee -> pegawai
- v2_3: emp_card -> kartu_identitas
- v2_4-v2_8: skills, training, education, work experience, family
- v2_9-v2_12: SK (surat keputusan), work history, contracts
- v2_13-v2_17: leave/cuti management

### External Integrations

- `app_write/` - AppWrite SDK integration for user account management (create/delete users from pegawai data)

## Key Conventions

- **No ORM** - All database access uses raw SQL with `pymysql` and `pymysqlpool.ConnectionPool`
- **DataFrame-centric** - Data flows as `pd.DataFrame` between fetch, transform, and save layers
- **Enum mappings** - Source system codes are translated to target system values via enums in `core/enums.py`
- **Foreign key checks disabled** during batch inserts (`SET FOREIGN_KEY_CHECKS=0`) with rollback on error
- **Default ID 0** used for unmapped/missing reference data in foreign key columns
- **icecream (`ic`)** used for debug output instead of print statements

## Environment

Requires a `.env` file with: `DB_HOST`, `DB_PORT`, `DB_USER`, `DB_PASS`, `DB_NAME` (smartoffice), `DB_NAME_KEPEGAWAIAN` (target DB). Optional: `API_URL` for HTTP posting.
