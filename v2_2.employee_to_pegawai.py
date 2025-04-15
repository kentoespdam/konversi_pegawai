import pandas as pd
import time
from icecream import ic
from core.kepegawaian.kepeg_gaji_pendapatan_non_pajak import fetch_all_gaji_pendapatan_non_pajak
from core.kepegawaian.kepeg_golongan import fetch_all_golongan
from core.kepegawaian.kepeg_jabatan import fetch_jabatan
from core.kepegawaian.kepeg_organisasi import fetch_organisasi
from core.kepegawaian.kepeg_pegawai import save_pegawai_from_employee
from core.kepegawaian.kepeg_profesi import fetch_profesi
from core.smartoffice.eo_employee import fetch_employee_for_pegawai
import swifter


def main():
    start_time = time.time()
    employee = pd.DataFrame(fetch_employee_for_pegawai())
    employee = cleanup(employee)
    ic(f"generating data finish in {time.time()-start_time}s")
    
    start_time = time.time()
    save_pegawai_from_employee(employee)
    ic(f"posting data finish in {time.time()-start_time}s")


def cleanup(df: pd.DataFrame):
    organisasi_df = pd.DataFrame(fetch_organisasi())
    df["organisasi_id"] = df["namaOrganisasi"].swifter.apply(
        lambda x: _get_organisasi_id(organisasi_df, x))

    jabatan_df = pd.DataFrame(fetch_jabatan())
    df["jabatan_id"] = df["namaJabatan"].swifter.apply(
        lambda x: _get_jabatan_id(jabatan_df, x))

    golongan_df = pd.DataFrame(fetch_all_golongan())
    df["golongan_id"] = df["golongan"].swifter.apply(
        lambda x: _get_golongan_id(golongan_df, x))

    profesi_df = pd.DataFrame(fetch_profesi())
    df["profesi_id"] = df["jabatan_id"].swifter.apply(
        lambda x: _get_profesi_id(profesi_df, x))
    df["grade_id"] = df["profesi_id"].swifter.apply(
        lambda x: _get_grade_id(profesi_df, x))

    pnp = pd.DataFrame(fetch_all_gaji_pendapatan_non_pajak())
    df["gaji_pendapatan_non_pajak_id"] = df["emp_tax_code"].swifter.apply(
        lambda x: _get_pnp_id(pnp, x))

    df["gaji_profil_id"] = df["gaji_profil_id"].swifter.apply(
        lambda x: x if not pd.isna(x) else 0).astype(int)

    df["tmt_kerja"] = df["tmt_kerja"].swifter.apply(
        lambda x: x.strftime("%Y-%m-%d") if x is not None else None)
    df["tmt_pensiun"] = df["tmt_pensiun"].swifter.apply(
        lambda x: x.strftime("%Y-%m-%d") if x is not None else None)
    
    df["is_askes"]=df["is_askes"].swifter.apply(
        lambda x: True if x==1 else False
    )
    df["is_deleted"] = df["is_deleted"].swifter.apply(
        lambda x: True if x == 1 else False)
    return df


def _get_organisasi_id(df: pd.DataFrame, namaOrganisasi: str):
    if namaOrganisasi is None or namaOrganisasi == "":
        return 0
    result = df.query("nama==@namaOrganisasi").reset_index(drop=True)
    return result.iloc[0]["id"] if not result.empty else 0


def _get_jabatan_id(df: pd.DataFrame, namaJabatan: str):
    if namaJabatan is None or namaJabatan == "":
        return 0
    result = df.query("nama==@namaJabatan").reset_index(drop=True)
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
