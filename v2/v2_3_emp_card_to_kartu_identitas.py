import logging
import time

import pandas as pd

from core.kepegawaian.jenis_kartu import fetch_all_jenis_kartu
from core.kepegawaian.kepeg_kartu_identitas import save_kartu_identitas_from_emp_card
from core.smartoffice.emp_card import fetch_emp_card_for_kartu_identitas
from v2.v2_helper import format_date_series, log_duration

# Setup logging
LOGGER = logging.getLogger(__name__)


def main():
    try:
        start_time = time.time()
        kartu_identitas_df = fetch_emp_card_for_kartu_identitas()

        if kartu_identitas_df.empty:
            LOGGER.info("No data found for kartu identitas.")
            return

        kartu_identitas_df = cleanup(kartu_identitas_df)
        log_duration("generating data", start_time)

        start_time = time.time()
        save_kartu_identitas_from_emp_card(kartu_identitas_df)
        log_duration("saving data", start_time)
    except Exception as e:
        LOGGER.error(f"Migration failed: {e}", exc_info=True)


def cleanup(df: pd.DataFrame):
    # Optimization: Use dictionary mapping for vectorized lookup instead of .apply()
    jenis_kartu_data = fetch_all_jenis_kartu()
    mapping = {item["nama"]: item["id"] for item in jenis_kartu_data}

    # Bug Fix: Ensure jenis_kitas_id is correctly mapped and handles missing values
    df["jenis_kitas_id"] = df["jenis_kitas"].map(mapping).fillna(0).astype(int)

    df["tanggal_expired"] = format_date_series(df["tanggal_expired"])
    df["tanggal_terima"] = format_date_series(df["tanggal_terima"])

    # Bug Fix: Ensure is_deleted is integer for DB compatibility
    df["is_deleted"] = df["is_deleted"].astype(int)

    return df


if __name__ == "__main__":
    main()
