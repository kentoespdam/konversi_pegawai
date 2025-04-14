import time
import pandas as pd
from icecream import ic
from core.kepegawaian.kepeg_jenjang_pendidikan import fetch_jenjang_pendidikan
from core.kepegawaian.kepeg_pendidikan import save_pendidikan_from_emp_education
from core.smartoffice.emp_education import fetch_emp_education_for_pendidikan
import swifter


def main():
    start_time = time.time()
    edu_df = pd.DataFrame(fetch_emp_education_for_pendidikan())
    edu_df = cleanup(edu_df)
    # ic(edu_df.dtypes)
    ic(f"generating data finish in {time.time()-start_time}s")

    start_time = time.time()
    save_pendidikan_from_emp_education(edu_df)
    ic(f"posting data finish in {time.time()-start_time}s")


def cleanup(df: pd.DataFrame):
    jenjang_pendidikan_df = pd.DataFrame(fetch_jenjang_pendidikan())
    df["jenjang_id"] = df["jenjang_pendidikan"].swifter.apply(
        lambda x: _get_jenjang_pendidikan_id(jenjang_pendidikan_df, x)
    )
    # df["tahun_masuk"] = df["tahun_masuk"].swifter.apply(
    #     lambda x: x if x is not None else 0
    # ).astype(int)
    df["is_lulus"] = df["is_lulus"].swifter.apply(
        lambda x: True if x == 1 else False
    )
    # df["tahun_lulus"] = df["tahun_lulus"].swifter.apply(
    #     lambda x: x if x is not None or x != "" else 0
    # ).astype(int)
    df["is_latest"] = df["is_latest"].swifter.apply(
        lambda x: True if x == 1 else False
    )
    df["tanggal_pengajuan"] = df["tanggal_pengajuan"].swifter.apply(
        lambda x: x.strftime("%Y-%m-%d %X") if x is not None else None
    )
    df["tanggal_disetujui"] = df["tanggal_disetujui"].swifter.apply(
        lambda x: x.strftime("%Y-%m-%d %X") if x is not pd.NaT else None
    )
    df["is_deleted"] = df["is_deleted"].swifter.apply(
        lambda x: True if x == 1 else False
    )
    df["gpa"] = df["gpa"].swifter.apply(
        lambda x: _str_to_float(x)).astype(float)

    return df


def _get_jenjang_pendidikan_id(df: pd.DataFrame, nama: str):
    if nama is None or nama == "":
        return 0
    result = df.query("nama==@nama").reset_index(drop=True)
    return result.iloc[0]["id"] if not result.empty else 0


def _str_to_float(x: str) -> float:
    if x == "" or x is None:
        return 0
    x = x.replace(",", ".")
    try:
        return float(x)
    except:
        return 0


if __name__ == "__main__":
    main()
