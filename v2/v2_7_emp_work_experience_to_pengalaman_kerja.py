import time
import traceback

import numpy as np
import pandas as pd

from core.config import LOGGER
from core.kepegawaian.kepeg_pengalaman_kerja import save_pengalaman_kerja_from_emp_work_experience
from core.smartoffice.emp_work_experience import fetch_emp_work_experience_for_pengalaman_kerja
from v2.v2_helper import log_duration, format_datetime_series


def main():
    try:
        start_time = time.time()
        work_df = fetch_emp_work_experience_for_pengalaman_kerja()

        if work_df is None or work_df.empty:
            LOGGER.info("No work experience records found for migration.")
            return

        LOGGER.info(f"Fetched {len(work_df)} records from source.")

        work_df = cleanup(work_df)
        log_duration("generating data finished", start_time)

        start_time = time.time()
        save_pengalaman_kerja_from_emp_work_experience(work_df)
        LOGGER.info(f"Successfully migrated {len(work_df)} records to target.")
        log_duration("posting data finished", start_time)

    except Exception as e:
        LOGGER.error(f"Fatal error during migration: {e}")
        LOGGER.error(traceback.format_exc())


def cleanup(df: pd.DataFrame):
    # Dynamic 'disetujui' flag: True only if tanggal_disetujui is present
    df["disetujui"] = df["tanggal_disetujui"].notnull()

    df["tanggal_pengajuan"] = format_datetime_series(df["tanggal_pengajuan"])
    df["tanggal_disetujui"] = format_datetime_series(df["tanggal_disetujui"])
    df["is_deleted"] = df["is_deleted"].eq(1)

    # Sanitize years: cast to int and replace 0 with None
    df["tahun_masuk"] = df["tahun_masuk"].astype(int).replace(0, None)
    df["tahun_keluar"] = df["tahun_keluar"].astype(int).replace(0, None)

    # Convert Pandas/Numpy nulls to native Python None for database compatibility
    return df.replace({np.nan: None, pd.NaT: None, pd.NA: None})


if __name__ == "__main__":
    main()
