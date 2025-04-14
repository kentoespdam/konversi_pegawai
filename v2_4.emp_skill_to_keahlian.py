import time
import pandas as pd
from icecream import ic
import swifter
from core.kepegawaian.kepeg_keahlian import save_keahlian_from_emp_skill
from core.smartoffice.emp_skill import fetch_emp_skill_for_keahlian


def main():
    start_time = time.time()
    skill_df = pd.DataFrame(fetch_emp_skill_for_keahlian())
    skill_df = cleanup(skill_df)
    ic(f"generating data finish in {time.time()-start_time}s")

    start_time = time.time()
    save_keahlian_from_emp_skill(skill_df)
    ic(f"posting data finish in {time.time()-start_time}s")


def cleanup(df: pd.DataFrame):
    df["sertifikasi"] = df["sertifikat"].swifter.apply(
        lambda x: True if x == 1 else False)
    df["tanggal_pengajuan"] = df["tanggal_pengajuan"].swifter.apply(
        lambda x: x.strftime("%Y-%m-%d %X") if x is not None else None)
    df["tanggal_disetujui"] = df["tanggal_disetujui"].swifter.apply(
        lambda x: x.strftime("%Y-%m-%d %X") if x is not pd.NaT else None)
    df["is_deleted"] = df["is_deleted"].swifter.apply(
        lambda x: True if x == 1 else False
    )
    return df


if __name__ == "__main__":
    main()
