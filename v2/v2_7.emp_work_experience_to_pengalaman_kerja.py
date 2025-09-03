import time

import pandas as pd

from core.kepegawaian.kepeg_pengalaman_kerja import save_pengalaman_kerja_from_emp_work_experience
from core.smartoffice.emp_work_experience import fetch_emp_work_experience_for_pengalaman_kerja
from v2.v2_helper import log_duration, format_datetime_series


def main():
    start_time = time.time()
    work_df = pd.DataFrame(fetch_emp_work_experience_for_pengalaman_kerja())
    work_df = cleanup(work_df)
    log_duration("generating data finished", start_time)

    start_time = time.time()
    save_pengalaman_kerja_from_emp_work_experience(work_df)
    log_duration("posting data finished", start_time)


def cleanup(df: pd.DataFrame):
    df["tanggal_pengajuan"] = format_datetime_series(df["tanggal_pengajuan"])
    df["tanggal_disetujui"] = format_datetime_series(df["tanggal_disetujui"])
    df["is_deleted"] = df["is_deleted"].eq(1)
    df["tahun_masuk"] = df["tahun_masuk"].astype(int)
    df["tahun_keluar"] = df["tahun_keluar"].astype(int)
    return df


if __name__ == "__main__":
    main()
