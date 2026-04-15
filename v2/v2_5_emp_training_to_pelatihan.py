import logging
import time

import pandas as pd
import numpy as np

from core.kepegawaian.kepeg_pelatihan import save_pelatihan_from_emp_training
from core.smartoffice.emp_training import fetch_emp_training_for_pelatihan
from v2.v2_helper import format_date_series, format_datetime_series, log_duration

LOGGER = logging.getLogger(__name__)


def main():
    try:
        start_time = time.time()
        training_df = fetch_emp_training_for_pelatihan()

        if training_df.empty:
            LOGGER.info("No training data found to migrate. Skipping.")
            return

        training_df = cleanup(training_df)
        log_duration("generating data", start_time)

        start_time = time.time()
        save_pelatihan_from_emp_training(training_df)
        log_duration("posting data", start_time)

    except Exception as e:
        LOGGER.error(f"Migration failed for v2_5_emp_training_to_pelatihan: {e}", exc_info=True)


def cleanup(df: pd.DataFrame):
    # Dynamic 'disetujui' logic: True if tanggal_disetujui is present
    df["disetujui"] = df["tanggal_disetujui"].notnull()

    df["tanggal_mulai"] = format_date_series(df["tanggal_mulai"])
    df["tanggal_selesai"] = format_date_series(df["tanggal_selesai"])
    df["ikatan_dinas"] = df["ikatan_dinas"].eq(1)
    df["tanggal_akhir_ikatan"] = format_date_series(df["tanggal_akhir_ikatan"])
    df["tanggal_pengajuan"] = format_datetime_series(df["tanggal_pengajuan"])
    df["tanggal_disetujui"] = format_datetime_series(df["tanggal_disetujui"])
    df["is_deleted"] = df["is_deleted"].eq(1)

    # Convert NaN/NaT to None for database compatibility
    df = df.replace({pd.NA: None, np.nan: None, pd.NaT: None})

    return df


if __name__ == "__main__":
    main()
