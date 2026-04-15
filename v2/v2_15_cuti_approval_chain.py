import time
import numpy as np
import pandas as pd
from core.config import LOGGER
from core.kepegawaian.kepeg_cuti_approval_chain import save_approval_chain
from core.smartoffice.eo_cuti_aproval_chain import fetch_cuti_approval_chain
from v2.v2_helper import log_duration


def cleanup(df: pd.DataFrame) -> pd.DataFrame:
    """
    Sanitasi data Pandas DataFrame sebelum dikirim ke database.
    """
    # 1. Type casting for consistency and to avoid floating point IDs
    df['id'] = df['id'].astype('Int64')
    df['ref_cuti_id'] = df['ref_cuti_id'].astype('Int64')
    df['jabatan_id'] = df['jabatan_id'].astype('Int64')
    df['approval_level'] = df['approval_level'].astype('Int64')
    df['read_write_status'] = df['read_write_status'].astype('Int64')

    # 2. Handle missing strings
    df['jabatan_nama'] = df['jabatan_nama'].fillna('')

    # 3. Final NaN/None sanitization
    df = df.replace({np.nan: None, pd.NA: None})

    return df


def main():
    try:
        start_time = time.time()
        LOGGER.info("Starting cuti_approval_chain migration...")

        # 1. Fetch
        df = fetch_cuti_approval_chain()
        if df.empty:
            LOGGER.info("No cuti_approval_chain data found. Skipping.")
            return

        LOGGER.info(f"Fetched {len(df)} records from SmartOffice.")

        # 2. Cleanup
        df = cleanup(df)
        log_duration("Data cleanup and preparation finished", start_time)

        # 3. Save
        post_start = time.time()
        save_approval_chain(df)
        LOGGER.info(f"Successfully processed and saved {len(df)} records.")
        log_duration("Posting cuti_approval_chain to Kepegawaian finished", post_start)

        log_duration("Total Cutii Approval Chain migration duration", start_time)

    except Exception as e:
        LOGGER.error(f"Migration v2_15 failed: {e}", exc_info=True)


if __name__ == "__main__":
    main()
