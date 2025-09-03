import time

import pandas as pd
import swifter  # noqa

from core.config import LOGGER
from core.kepegawaian.kepeg_gaji_pendapatan_non_pajak import (
    fetch_all_gaji_pendapatan_non_pajak,
)
from core.kepegawaian.kepeg_golongan import fetch_all_golongan
from core.kepegawaian.kepeg_jabatan import fetch_jabatan
from core.kepegawaian.kepeg_organisasi import fetch_organisasi
from core.kepegawaian.kepeg_pegawai import save_pegawai_from_employee, update_pegawai_phdp
from core.kepegawaian.kepeg_profesi import fetch_profesi
from core.smartoffice.eo_employee import fetch_employee_for_pegawai, fetch_gaji_employee
from v2.v2_helper import format_date_series


def main():
    start_time = time.time()
    employee = pd.DataFrame(fetch_employee_for_pegawai())
    employee = cleanup(employee)
    LOGGER.info(f"generating data finish in {time.time() - start_time}s")

    start_time = time.time()
    save_pegawai_from_employee(employee)
    LOGGER.info(f"posting data finish in {time.time() - start_time}s")

    start_time = time.time()
    salary_rows = fetch_gaji_employee()
    update_pegawai_phdp(salary_rows)
    LOGGER.info(f"updating data finish in {time.time() - start_time}s")


def cleanup(df: pd.DataFrame):
    organisasi_df = pd.DataFrame(fetch_organisasi())
    df["organisasi_id"] = df["namaOrganisasi"].apply(
        lambda x: _get_organisasi_id(organisasi_df, x)
    )

    jabatan_df = pd.DataFrame(fetch_jabatan())
    df["jabatan_id"] = df["namaJabatan"].apply(
        lambda x: _get_jabatan_id(jabatan_df, x)
    )

    golongan_df = pd.DataFrame(fetch_all_golongan())
    df["golongan_id"] = df["golongan"].apply(
        lambda x: _get_golongan_id(golongan_df, x)
    )

    profesi_df = pd.DataFrame(fetch_profesi())
    df["profesi_id"] = df["jabatan_id"].apply(
        lambda x: _get_profesi_id(profesi_df, x)
    )
    df["grade_id"] = df["profesi_id"].apply(
        lambda x: _get_grade_id(profesi_df, x)
    )

    pnp = pd.DataFrame(fetch_all_gaji_pendapatan_non_pajak())
    df["gaji_pendapatan_non_pajak_id"] = df["emp_tax_code"].apply(
        lambda x: _get_pnp_id(pnp, x)
    )

    df["gaji_profil_id"] = (
        df["gaji_profil_id"]
        .apply(lambda x: x if not pd.isna(x) else 0)
        .astype(int)
    )

    df["tmt_mutasi"] = format_date_series(df["tmt_mutasi"])
    df["tmt_jabatan"] = format_date_series(df["tmt_jabatan"])
    df["tmt_golongan"] = format_date_series(df["tmt_golongan"])
    df["tmt_kerja"] = format_date_series(df["tmt_kerja"])
    df["tanggal_pengangkatan"] = format_date_series(df["tanggal_pengangkatan"])
    df["tmt_pensiun"] = format_date_series(df["tmt_pensiun"])

    df["is_askes"] = df["is_askes"].eq(1)
    df["is_deleted"] = df["is_deleted"].eq(1)
    return df


def _get_organisasi_id(df: pd.DataFrame, nama_organisasi: str):
    if nama_organisasi is None or nama_organisasi == "":
        return 0
    result = df.query("nama==@nama_organisasi").reset_index(drop=True)
    return result.iloc[0]["id"] if not result.empty else 0


def _get_jabatan_id(df: pd.DataFrame, nama_jabatan: str):
    if nama_jabatan is None or nama_jabatan == "":
        return 0
    result = df.query("nama==@nama_jabatan").reset_index(drop=True)
    return result.iloc[0]["id"] if not result.empty else 0


def _get_golongan_id(df: pd.DataFrame, golongan: str):
    if golongan is None or golongan == "":
        return 0
    result = df.query("golongan==@golongan").reset_index(drop=True)
    return result.iloc[0]["id"] if not result.empty else 0


def _get_profesi_id(df: pd.DataFrame, jabatan_id: int):
    if jabatan_id is None or jabatan_id == "":
        return 0
    result = df.query("jabatan_id==@jabatan_id").reset_index(drop=True)
    return result.iloc[0]["id"] if not result.empty else 0


def _get_grade_id(df: pd.DataFrame, profesi_id: int):
    if profesi_id is None or profesi_id == "":
        return 0
    result = df.query("id==@profesi_id").reset_index(drop=True)
    return result.iloc[0]["grade_id"] if not result.empty else 0


def _get_pnp_id(df: pd.DataFrame, emp_tax_code: str):
    if emp_tax_code is None or emp_tax_code == "":
        return 0
    result = df.query("kode==@emp_tax_code").reset_index(drop=True)
    return result.iloc[0]["id"] if not result.empty else 0


if __name__ == "__main__":
    main()
