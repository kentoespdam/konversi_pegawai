import time
import pandas as pd
from icecream import ic
from core.kepegawaian.kepeg_pengalaman_kerja import save_pengalaman_kerja_from_emp_work_experience
from core.smartoffice.emp_work_experience import fetch_emp_work_experience_for_pengalaman_kerja
import swifter


def main():
    start_time = time.time()
    work_df = pd.DataFrame(fetch_emp_work_experience_for_pengalaman_kerja())
    work_df = cleanup(work_df)
    ic(f"generating data finish in {time.time()-start_time}s")

    start_time = time.time()
    save_pengalaman_kerja_from_emp_work_experience(work_df)
    ic(f"posting data finish in {time.time()-start_time}s")


def cleanup(df: pd.DataFrame):
    df["tanggal_pengajuan"] = df["tanggal_pengajuan"].swifter.apply(
        lambda x: x.strftime("%Y-%m-%d %X") if x is not pd.NaT else None)
    df["tanggal_disetujui"] = df["tanggal_disetujui"].swifter.apply(
        lambda x: x.strftime("%Y-%m-%d %X") if x is not pd.NaT else None
    )
    df["is_deleted"] = df["is_deleted"].swifter.apply(
        lambda x: True if x == 1 else False)
    df["tahun_masuk"] = df["tahun_masuk"].astype(int)
    df["tahun_keluar"] = df["tahun_keluar"].astype(int)
    return df


if __name__ == "__main__":
    main()
