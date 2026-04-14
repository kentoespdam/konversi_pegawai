import time
import traceback

import numpy as np
import pandas as pd

from core.config import LOGGER, fetch_smartoffice
from core.smartoffice.emp_sk import save_emp_sk_from_emp_work_history
from core.smartoffice.emp_work_history import fetch_emp_work_history_for_emp_sk
from v2.v2_helper import log_duration, format_date_series


def main():
    start_all = time.time()
    try:
        LOGGER.info("Starting v2_9_1_init_emp_sk_from_riwayat_sk_optional...")
        
        start_time = time.time()
        sk_df = fetch_emp_work_history_for_emp_sk()
        if sk_df.empty:
            LOGGER.info("No records found to process.")
            return

        LOGGER.info(f"Fetched {len(sk_df)} records from emp_work_history.")
        sk_df = cleanup_init(sk_df)
        log_duration("generating data", start_time)

        if sk_df.empty:
            LOGGER.info("No new records after cleaning and filtering.")
            return

        start_time = time.time()
        save_emp_sk_from_emp_work_history(sk_df)
        LOGGER.info(f"Successfully processed {len(sk_df)} records.")
        log_duration("posting data", start_time)
        
        log_duration("Total execution", start_all)

    except Exception as e:
        LOGGER.error(f"Migration failed: {e}")
        LOGGER.error(traceback.format_exc())


def filter_sk(df: pd.DataFrame, no_sk: str):
    """Filter records that match an existing SK no (Bug Fix: use | instead of or)"""
    mask = df["esk_no_sk"].isnull() | df["no_sk"].eq(no_sk)
    return df[mask].reset_index(drop=True)


def cleanup_init(df: pd.DataFrame):
    df = df.copy()
    
    # Bug Fix: Map invalid no_sk to "Init SmartOffice"
    df["no_sk"] = df["no_sk"].fillna("").astype(str)
    df["no_sk"] = np.where(
        df["no_sk"].isin(["", "-", "None"]),
        "Init SmartOffice",
        df["no_sk"]
    )

    # Bug Fix: Format dates
    df["tgl_sk"] = format_date_series(df["tgl_sk"])
    df["tmt_sk"] = format_date_series(df["tmt_sk"])
    
    # Constant columns
    df["ref_id"] = 0
    df["status"] = 1
    
    # Bug Fix: Note sanitization
    df["notes"] = np.where(
        df["notes"].isna() | df["notes"].eq(""),
        "Init Smartoffice",
        df["notes"].astype(str)
    )

    # Idempotency Filter: Remove records that already exist in emp_sk
    # (Since there is no Unique Key on emp_sk table)
    existing_sk = fetch_smartoffice("SELECT emp_id, no_sk FROM emp_sk")
    if not existing_sk.empty:
        # Create a combined key for matching
        df["match_key"] = df["emp_id"].astype(str) + "_" + df["no_sk"].astype(str)
        existing_sk["match_key"] = existing_sk["emp_id"].astype(str) + "_" + existing_sk["no_sk"].astype(str)
        
        mask = ~df["match_key"].isin(existing_sk["match_key"])
        df = df[mask].drop(columns=["match_key"])
    
    # Final NaN sanitization
    df = df.replace({np.nan: None, pd.NaT: None, pd.NA: None})
    
    return df


if __name__ == "__main__":
    main()
