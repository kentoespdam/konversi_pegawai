import time
import traceback

import numpy as np
import pandas as pd

from core.config import LOGGER, fetch_kepegawaian
from core.kepegawaian.kepeg_riwayat_sk import save_riwayat_sk_from_emp_sk
from core.smartoffice.emp_sk import fetch_emp_sk_for_riwayat_sk, update_init_smartoffice_no_sk
from v2.v2_helper import log_duration


def main():
    start_all = time.time()
    try:
        LOGGER.info("Starting v2_9_2_emp_sk_to_riwayat_sk...")
        
        # 1. Initialization
        start_time = time.time()
        update_init_smartoffice_no_sk()
        log_duration("Initialization finished", start_time)

        # 2. Fetch Data
        start_time = time.time()
        sk_df = fetch_emp_sk_for_riwayat_sk()
        if sk_df.empty:
            LOGGER.info("No records found to process.")
            return

        LOGGER.info(f"Fetched {len(sk_df)} records from SmartOffice.")
        sk_df = cleanup(sk_df)
        log_duration("Generating and filtering data finished", start_time)

        if sk_df.empty:
            LOGGER.info("No new records after cleaning and idempotency filtering.")
            return

        # 3. Post Data
        start_time = time.time()
        save_riwayat_sk_from_emp_sk(sk_df)
        LOGGER.info(f"Successfully processed {len(sk_df)} records.")
        log_duration("Posting data finished", start_time)

        log_duration("Total execution finished", start_all)

    except Exception as e:
        LOGGER.error(f"Migration failed: {e}")
        LOGGER.error(traceback.format_exc())


def cleanup(df: pd.DataFrame):
    df = df.copy()

    # 1. Transform booleans
    df["update_master"] = df["update_master"].eq(1)
    df["is_deleted"] = df["is_deleted"].eq(1)

    # 2. Convert 0 to None for specific numeric columns (BUG-6)
    # Value 0 in these fields usually means no data from source
    num_cols = ["gaji_pokok", "mkg_tahun", "mkg_bulan", "mkgb_tahun", "mkgb_bulan"]
    for col in num_cols:
        if col in df.columns:
            df[col] = df[col].replace(0, None)

    # 3. Idempotency Filter: Remove records that already exist in riwayat_sk (BUG-2)
    # We use (pegawai_id, nomor_sk, jenis_sk) as the composite key for matching
    existing_sk = fetch_kepegawaian("SELECT pegawai_id, nomor_sk, jenis_sk FROM riwayat_sk")
    if not existing_sk.empty:
        # Create a combined key for matching
        df["match_key"] = (
            df["pegawai_id"].astype(str) + "_" + 
            df["nomor_sk"].astype(str) + "_" + 
            df["jenis_sk"].astype(str)
        )
        existing_sk["match_key"] = (
            existing_sk["pegawai_id"].astype(str) + "_" + 
            existing_sk["nomor_sk"].astype(str) + "_" + 
            existing_sk["jenis_sk"].astype(str)
        )
        
        mask = ~df["match_key"].isin(existing_sk["match_key"])
        df = df[mask].drop(columns=["match_key"])

    # 4. Final NaN/NaT sanitization (BUG-5)
    df = df.replace({np.nan: None, pd.NaT: None, pd.NA: None})

    return df


if __name__ == "__main__":
    main()
