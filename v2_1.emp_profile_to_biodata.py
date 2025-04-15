import time
import pandas as pd
from core.kepegawaian.kepeg_biodata import save_biodata_from_emp_profile
from core.kepegawaian.kepeg_kartu_identitas import save_kartu_identitas_from_emp_profile
from core.kepegawaian.kepeg_jenjang_pendidikan import fetch_jenjang_pendidikan
from core.smartoffice.emp_profile import fetch_data_for_biodata
from icecream import ic
import swifter


def main():
    start_time = time.time()
    biodata_df = pd.DataFrame(fetch_data_for_biodata())
    biodata_df = cleanup(biodata_df)
    ic(f"generating data finish in {time.time()-start_time}s")

    start_time = time.time()
    save_biodata_from_emp_profile(biodata_df)
    save_kartu_identitas_from_emp_profile(biodata_df)
    ic(f"posting data finish in {time.time()-start_time}s")


def cleanup(df: pd.DataFrame):
    jejang_pendidikan_df = pd.DataFrame(fetch_jenjang_pendidikan())
    df["tanggal_lahir"] = df["tanggal_lahir"].swifter.apply(
        lambda x: x.strftime('%Y-%m-%d') if x is not None else None)
    df["pendidikan_id"] = df["pendidikanTerakhir"].swifter.apply(
        lambda x: get_pendidikan_terakhir_id(x, jejang_pendidikan_df))
    df["is_deleted"] = df["is_deleted"].swifter.apply(
        lambda x: True if x == 1 else False)
    df["is_pegawai"]=df["emp_flag"].swifter.apply(
        lambda x: False if x == 0 else True)
    return df


def get_pendidikan_terakhir_id(pendidikan_terakhir: str, jenjang_pendidikan_df: pd.DataFrame):
    result = jenjang_pendidikan_df.query(
        "nama == @pendidikan_terakhir").reset_index(drop=True)
    return result["id"].values[0] if not result.empty else 0

if __name__ == "__main__":
    main()
