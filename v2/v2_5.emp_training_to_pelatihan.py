import time

import pandas as pd

from core.kepegawaian.kepeg_pelatihan import save_pelatihan_from_emp_training
from core.smartoffice.emp_training import fetch_emp_training_for_pelatihan
from v2.v2_helper import format_date_series, format_datetime_series, log_duration


def main():
    start_time = time.time()
    training_df = fetch_emp_training_for_pelatihan()
    training_df = cleanup(training_df)
    log_duration("generating data", start_time)

    start_time = time.time()
    save_pelatihan_from_emp_training(training_df)
    log_duration("posting data", start_time)


def cleanup(df: pd.DataFrame):
    df["tanggal_mulai"] = format_date_series(df["tanggal_mulai"])
    df["tanggal_selesai"] = format_date_series(df["tanggal_selesai"])
    df["ikatan_dinas"] = df["ikatan_dinas"].eq(1)
    df["tanggal_akhir_ikatan"] = format_date_series(df["tanggal_akhir_ikatan"])
    df["tanggal_pengajuan"] = format_datetime_series(df["tanggal_pengajuan"])
    df["tanggal_disetujui"] = format_datetime_series(df["tanggal_disetujui"])
    df["is_deleted"] = df["is_deleted"].eq(1)
    return df


if __name__ == "__main__":
    main()
