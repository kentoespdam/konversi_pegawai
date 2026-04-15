import time
import traceback
import numpy as np
import pandas as pd

from core.config import LOGGER
from core.kepegawaian.kepeg_cuti_pegawai import save_cuti_pegawai
from core.smartoffice.eo_cuti_pegawai import fetch_cuti_pegawai
from v2.v2_helper import format_datetime_series, format_date_series, log_duration

# Constants to avoid magic numbers
CUTI_PENGAJUAN_CLAIM = 1
APPROVAL_APPROVED = 1


def main() -> None:
    try:
        start = time.time()
        df = fetch_cuti_pegawai()
        if df.empty:
            LOGGER.info("No cuti_pegawai data found. Skipping.")
            return

        LOGGER.info(f"Fetched {len(df)} cuti_pegawai records.")
        df = transform_cuti_dataframe(df)

        log_duration("transforming cuti_pegawai finished", start)

        start = time.time()
        save_cuti_pegawai(df)
        LOGGER.info(f"Successfully processed {len(df)} cuti_pegawai records.")
        log_duration("Posting cuti_pegawai finished", start)
    except Exception as e:
        LOGGER.error(f"Error in cuti_pegawai migration: {e}")
        traceback.print_exc()


# ... existing code ...
def transform_cuti_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """
    Normalize date fields and compute 'is_claimed' efficiently.

    Rules for is_claimed:
    - If jenis_pengajuan_cuti == CUTI_PENGAJUAN_CLAIM: False
    - Else: True if the row's id appears as ref_cuti_id in approved claim rows
    """
    # Format timestamps/dates
    df = df.copy()
    df["created_at"] = format_datetime_series(df["created_at"])
    df["tanggal_mulai"] = format_date_series(df["tanggal_mulai"], True)
    df["tanggal_selesai"] = format_date_series(df["tanggal_selesai"], True)

    df = _cleanup_claim(df)
    return df


def _cleanup_claim(df: pd.DataFrame):
    df = df.copy()
    # Build the set of claimed IDs from approved claim submissions
    claim_df = df[df["jenis_pengajuan_cuti"] == CUTI_PENGAJUAN_CLAIM].reset_index(drop=True)
    approved_claim_ref_ids = set(
        claim_df.loc[claim_df["approval_cuti_status"] == APPROVAL_APPROVED, "ref_cuti_id"].dropna().astype(int)
    )

    # Vectorized computation of is_claimed (avoid per-row apply/swifter)
    df["is_claimed"] = (df["jenis_pengajuan_cuti"] != CUTI_PENGAJUAN_CLAIM) & (df["id"].isin(approved_claim_ref_ids))

    # Sanitize NaN/NaT values for MySQL
    df = df.replace({np.nan: None, pd.NaT: None, pd.NA: None})
    return df


if __name__ == "__main__":
    main()
