import time

import pandas as pd

from core.kepegawaian.kepeg_cuti_pegawai import save_cuti_pegawai
from core.smartoffice.eo_cuti_pegawai import fetch_cuti_pegawai
from v2.v2_helper import format_datetime_series, format_date_series, log_duration

# Constants to avoid magic numbers
CUTI_PENGAJUAN_CLAIM = 1
APPROVAL_APPROVED = 1


def main() -> None:
    start = time.time()
    cp_df = fetch_cuti_pegawai()
    cp_df = transform_cuti_dataframe(cp_df)
    save_cuti_pegawai(cp_df)
    log_duration("Posting cuti_pegawai finished", start)


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
    return df


if __name__ == "__main__":
    main()
