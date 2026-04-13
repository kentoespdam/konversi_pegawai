import logging
import time
import sys

import pandas as pd

from core.kepegawaian.kepeg_keahlian import save_keahlian_from_emp_skill
from core.smartoffice.emp_skill import fetch_emp_skill_for_keahlian
from v2.v2_helper import format_date_series, log_duration

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def main():
    try:
        start_time = time.time()
        skill_df = fetch_emp_skill_for_keahlian()
        
        if skill_df is None or skill_df.empty:
            logging.info("No data found to migrate.")
            return

        skill_df = cleanup(skill_df)
        log_duration("generating data", start_time)

        start_time = time.time()
        save_keahlian_from_emp_skill(skill_df)
        log_duration("posting data", start_time)
        
        logging.info("Migration v2_4 completed successfully.")
    except Exception as e:
        logging.error(f"Migration v2_4 failed: {str(e)}")
        sys.exit(1)


def cleanup(df: pd.DataFrame):
    # Vectorized operations
    df["sertifikasi"] = df["sertifikat"].eq(1)
    df["tanggal_pengajuan"] = format_date_series(df["tanggal_pengajuan"])
    df["tanggal_disetujui"] = format_date_series(df["tanggal_disetujui"])
    
    # Dynamic disetujui logic: True if tanggal_disetujui is not null/empty
    df["disetujui"] = df["tanggal_disetujui"].notna() & (df["tanggal_disetujui"] != "")
    
    # is_deleted logic: status_raw == 3 (based on original query logic)
    df["is_deleted"] = df["status_raw"].eq(3)
    
    return df


if __name__ == "__main__":
    main()
