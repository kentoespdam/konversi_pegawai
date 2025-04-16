from datetime import date
import time
import pandas as pd
from icecream import ic
from core.kepegawaian.kepeg_biodata import fetch_biodata_for_riwayat_kontrak
from core.kepegawaian.kepeg_riwayat_kontrak import save_riwayat_kontrak_from_emp_contract
from core.smartoffice.emp_contract import fetch_emp_contract_for_riwayat_kontrak
import swifter


def main():
    start_time = time.time()
    contract_df = pd.DataFrame(fetch_emp_contract_for_riwayat_kontrak())
    contract_df = cleanup(contract_df)
    # ic(contract_df)
    ic(f"generating data finish in {time.time()-start_time}s")

    start_time = time.time()
    save_riwayat_kontrak_from_emp_contract(contract_df)
    ic(f"posting data finish in {time.time()-start_time}s")


def cleanup(df: pd.DataFrame):
    pegawai_df = pd.DataFrame(fetch_biodata_for_riwayat_kontrak())
    df["pegawai_id"] = df["nik"].swifter.apply(
        lambda x: _get_pegawai_id(pegawai_df, x))
    df["nama"] = df["nik"].swifter.apply(
        lambda x: _get_pegawai_id(pegawai_df, x, "nama"))

    df["tanggal_sk"] = df["tanggal_sk"].swifter.apply(
        lambda x: _cleanup_tanggal_sk(x))
    df["is_deleted"] = df["is_deleted"].swifter.apply(
        lambda x: True if x == 1 else False)

    # df_grouped=df.sort_values(["tanggal_sk"],ascending=False).groupby("nik")
    df["is_latest"] = df["tanggal_sk"].transform(lambda x: x == x.max())
    return df


def _cleanup_tanggal_sk(x):
    if x == "0000-00-00":
        return pd.to_datetime("1945-08-17")
    return pd.to_datetime(x)


def _get_pegawai_id(df: pd.DataFrame, nik: str, col: str = "id"):
    result = df.query("nik==@nik").reset_index(drop=True)
    result_size = result["nik"].size
    if (result_size > 1):
        result = result[result["status_kerja"] == 2].reset_index(drop=True)
    return result.iloc[0][col] if not result.empty else 0 if col == "id" else None


if __name__ == "__main__":
    main()
