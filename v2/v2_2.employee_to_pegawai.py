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
    df = df.copy()
    df["organisasi_id"] = _cleanup_organisasi_id(df)
    df["jabatan_id"] = _cleanup_jabatan_id(df)
    df["golongan_id"] = _cleanup_golongan_id(df)
    profesi_df = pd.DataFrame(fetch_profesi())
    df["profesi_id"] = _cleanup_profesi_id(df, profesi_df)
    df["grade_id"] = _cleanup_grade_id(df, profesi_df)
    df["gaji_pendapatan_non_pajak_id"] = cleanup_pendapatan_non_pajak(df)
    df["gaji_profil_id"] = df["gaji_profil_id"].fillna(0).astype(int)

    for col in DATE_COLUMNS:
        df[col] = format_date_series(df[col])

    df["is_askes"] = df["is_askes"].eq(1)
    df["is_deleted"] = df["is_deleted"].eq(1)
    return df


def _cleanup_organisasi_id(df: pd.DataFrame):
    df = df.copy()
    organisasi_df = pd.DataFrame(fetch_organisasi())
    org_map = organisasi_df.set_index("nama")["id"].to_dict()
    return df["namaOrganisasi"].map(org_map).fillna(0).astype(int)


def _cleanup_jabatan_id(df: pd.DataFrame):
    df = df.copy()
    jabatan_df = pd.DataFrame(fetch_jabatan())
    jab_map = jabatan_df.set_index("nama")["id"].to_dict()
    return df["namaJabatan"].map(jab_map).fillna(0).astype(int)


def _cleanup_golongan_id(df: pd.DataFrame):
    df = df.copy()
    golongan_df = pd.DataFrame(fetch_all_golongan())
    gol_map = golongan_df.set_index("golongan")["id"].to_dict()
    return df["golongan"].map(gol_map).fillna(0).astype(int)


def _cleanup_profesi_id(df: pd.DataFrame, profesi_df: pd.DataFrame):
    df = df.copy()
    profesi_by_jabatan_map = profesi_df.set_index("jabatan_id")["id"].to_dict()
    return df["jabatan_id"].map(profesi_by_jabatan_map).fillna(0).astype(int)


def _cleanup_grade_id(df: pd.DataFrame, profesi_df: pd.DataFrame):
    df = df.copy()
    grade_by_profesi_map = profesi_df.set_index("id")["grade_id"].to_dict()
    return df["profesi_id"].map(grade_by_profesi_map).fillna(0).astype(int)


def cleanup_pendapatan_non_pajak(df: pd.DataFrame):
    df = df.copy()
    pnp = pd.DataFrame(fetch_all_gaji_pendapatan_non_pajak())
    pnp_map = pnp.set_index("kode")["id"].to_dict()
    return df["emp_tax_code"].map(pnp_map).fillna(0).astype(int)


if __name__ == "__main__":
    main()
