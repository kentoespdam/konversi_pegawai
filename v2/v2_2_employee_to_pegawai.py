import time

import pandas as pd

from core.kepegawaian.kepeg_gaji_pendapatan_non_pajak import (
    fetch_all_gaji_pendapatan_non_pajak,
)
from core.kepegawaian.kepeg_golongan import fetch_all_golongan
from core.kepegawaian.kepeg_jabatan import fetch_jabatan
from core.kepegawaian.kepeg_organisasi import fetch_organisasi
from core.kepegawaian.kepeg_pegawai import save_pegawai_from_employee, update_pegawai_phdp
from core.kepegawaian.kepeg_profesi import fetch_profesi
from core.smartoffice.eo_employee import fetch_employee_for_pegawai, fetch_gaji_employee
from v2.v2_helper import format_date_series, log_duration

DATE_COLUMNS = [
    "tmt_mutasi",
    "tmt_jabatan",
    "tmt_golongan",
    "tmt_kerja",
    "tanggal_pengangkatan",
    "tmt_pensiun",
]


def main():
    start_time = time.time()
    employee = fetch_employee_for_pegawai()
    employee = cleanup(employee)
    log_duration("generating data finish in ", start_time)

    start_time = time.time()
    save_pegawai_from_employee(employee)
    log_duration("posting data finish in ", start_time)

    start_time = time.time()
    salary_rows = fetch_gaji_employee()
    update_pegawai_phdp(salary_rows)
    log_duration("posting data finish in ", start_time)


def cleanup(df: pd.DataFrame):
    # Build mapping DataFrames once (avoid redundant fetches and DataFrame creation in helpers)
    organisasi_df = pd.DataFrame(fetch_organisasi(), columns=["id", "nama"])
    jabatan_df = pd.DataFrame(fetch_jabatan(), columns=["id", "kode", "parent_id", "level_id", "nama", "organisasi_id"])
    golongan_df = pd.DataFrame(fetch_all_golongan(), columns=["id", "golongan", "pangkat"])
    profesi_df = pd.DataFrame(fetch_profesi(), columns=["id", "nama", "level_id", "organisasi_id", "jabatan_id", "grade_id"])
    pnp_df = fetch_all_gaji_pendapatan_non_pajak()  # already returns DataFrame

    # Apply mappings in-place using Series.map (no unnecessary copies)
    df["organisasi_id"] = _map_organisasi(df["namaOrganisasi"], organisasi_df)
    df["jabatan_id"] = _map_jabatan(df["namaJabatan"], jabatan_df)
    df["golongan_id"] = _map_golongan(df["golongan"], golongan_df)
    df["profesi_id"] = _map_profesi(df["jabatan_id"], profesi_df)
    df["grade_id"] = _map_grade(df["profesi_id"], profesi_df)
    df["gaji_pendapatan_non_pajak_id"] = _map_pendapatan_non_pajak(df["emp_tax_code"], pnp_df)
    df["gaji_profil_id"] = df["gaji_profil_id"].fillna(0).astype(int)

    for col in DATE_COLUMNS:
        df[col] = format_date_series(df[col])

    df["is_askes"] = df["is_askes"].eq('1')
    df["is_deleted"] = df["is_deleted"].eq(1)
    return df


def _map_organisasi(nama_series: pd.Series, organisasi_df: pd.DataFrame) -> pd.Series:
    org_map = organisasi_df.set_index("nama")["id"].to_dict()
    return nama_series.map(org_map).fillna(0).astype(int)


def _map_jabatan(nama_series: pd.Series, jabatan_df: pd.DataFrame) -> pd.Series:
    jab_map = jabatan_df.set_index("nama")["id"].to_dict()
    return nama_series.map(jab_map).fillna(0).astype(int)


def _map_golongan(gol_series: pd.Series, golongan_df: pd.DataFrame) -> pd.Series:
    gol_map = golongan_df.set_index("golongan")["id"].to_dict()
    return gol_series.map(gol_map).fillna(0).astype(int)


def _map_profesi(jabatan_id_series: pd.Series, profesi_df: pd.DataFrame) -> pd.Series:
    profesi_by_jabatan_map = profesi_df.set_index("jabatan_id")["id"].to_dict()
    return jabatan_id_series.map(profesi_by_jabatan_map).fillna(0).astype(int)


def _map_grade(profesi_id_series: pd.Series, profesi_df: pd.DataFrame) -> pd.Series:
    grade_by_profesi_map = profesi_df.set_index("id")["grade_id"].to_dict()
    return profesi_id_series.map(grade_by_profesi_map).fillna(0).astype(int)


def _map_pendapatan_non_pajak(kode_series: pd.Series, pnp_df: pd.DataFrame) -> pd.Series:
    pnp_map = pnp_df.set_index("kode")["id"].to_dict()
    return kode_series.map(pnp_map).fillna(0).astype(int)


if __name__ == "__main__":
    main()
