import time
import numpy as np
import pandas as pd

from core.kepegawaian.kepeg_cuti_kuota import save_cuti_kuota
from core.smartoffice.eo_cuti_kuota import fetch_cuti_kuota
from core.config import LOGGER
from v2.v2_helper import format_date_series, log_duration


def main():
    try:
        start = time.time()
        ck_df = fetch_cuti_kuota()

        if ck_df.empty:
            LOGGER.info("No cuti_kuota data found. Skipping.")
            return

        LOGGER.info(f"Fetched {len(ck_df)} records from smartoffice.")

        ck_df = cleanup(ck_df)
        log_duration("generating data finished", start)

        start_post = time.time()
        save_cuti_kuota(ck_df)
        LOGGER.info(f"Successfully processed {len(ck_df)} records.")
        log_duration("posting cuti_kuota finished", start_post)

    except Exception as e:
        LOGGER.error(f"Migration failed: {e}", exc_info=True)


def cleanup(df):
    # Bug 1 Fix: Filter out records where pegawai_id is NULL (from LEFT JOIN)
    initial_count = len(df)
    df = df[df["pegawai_id"].notnull()].copy()
    dropped_count = initial_count - len(df)
    if dropped_count > 0:
        LOGGER.warning(f"Dropped {dropped_count} records due to missing employee mapping (pegawai_id IS NULL).")

    df["expired"] = format_date_series(df["expired"])

    # Bug 5 Fix: NaN/NaT sanitization
    df = df.replace({np.nan: None, pd.NaT: None, pd.NA: None})
    return df


if __name__ == "__main__":
    main()
