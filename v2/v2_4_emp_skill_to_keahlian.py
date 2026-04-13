import time

import pandas as pd

from core.kepegawaian.kepeg_keahlian import save_keahlian_from_emp_skill
from core.smartoffice.emp_skill import fetch_emp_skill_for_keahlian
from v2.v2_helper import format_date_series, log_duration


def main():
    start_time = time.time()
    skill_df = fetch_emp_skill_for_keahlian()
    skill_df = cleanup(skill_df)
    log_duration("generating data", start_time)

    start_time = time.time()
    save_keahlian_from_emp_skill(skill_df)
    log_duration("posting data", start_time)


def cleanup(df: pd.DataFrame):
    df["sertifikasi"] = df["sertifikat"].eq(1)
    df["tanggal_pengajuan"] = format_date_series(df["tanggal_pengajuan"])
    df["tanggal_disetujui"] = format_date_series(df["tanggal_disetujui"])
    df["is_deleted"] = df["is_deleted"].eq(1)
    return df


if __name__ == "__main__":
    main()
