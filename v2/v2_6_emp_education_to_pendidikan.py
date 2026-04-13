import time

import pandas as pd

from core.kepegawaian.kepeg_jenjang_pendidikan import fetch_jenjang_pendidikan
from core.kepegawaian.kepeg_pendidikan import save_pendidikan_from_emp_education
from core.smartoffice.emp_education import fetch_emp_education_for_pendidikan
from v2.v2_helper import format_datetime_series, str_to_float, log_duration

DEFAULT_JENJANG_ID = 0


def main():
    start_time = time.time()
    edu_df = fetch_emp_education_for_pendidikan()
    edu_df = cleanup(edu_df)
    log_duration("generating data finished", start_time)

    start_time = time.time()
    save_pendidikan_from_emp_education(edu_df)
    log_duration("posting data finished", start_time)


def cleanup(df: pd.DataFrame):
    jenjang_pendidikan_df = pd.DataFrame(fetch_jenjang_pendidikan())
    # Build a vectorized mapping from jenjang name to id for efficient lookup
    jenjang_map = dict(zip(jenjang_pendidikan_df["nama"], jenjang_pendidikan_df["id"]))
    df["jenjang_id"] = (
        df["jenjang_pendidikan"]
        .map(jenjang_map)
        .fillna(DEFAULT_JENJANG_ID)
        .astype(int)
    )
    df["is_lulus"] = df["is_lulus"].eq(1)
    df["is_latest"] = df["is_latest"].eq(1)
    df["tanggal_pengajuan"] = format_datetime_series(df["tanggal_pengajuan"])
    df["tanggal_disetujui"] = format_datetime_series(df["tanggal_disetujui"])
    df["is_deleted"] = df["is_deleted"].eq(1)
    df["gpa"] = df["gpa"].map(str_to_float).astype(float)
    return df


if __name__ == "__main__":
    main()
