import time
import traceback
import numpy as np
import pandas as pd

from core.config import LOGGER
from core.kepegawaian.kepeg_golongan import fetch_all_golongan
from core.kepegawaian.kepeg_profesi import fetch_profesi
from core.kepegawaian.kepeg_riwayat_mutasi import save_riwayat_mutasi_from_emp_work_history
from core.kepegawaian.kepeg_riwayat_sk import fetch_all_riwayat_sk
from core.smartoffice.emp_work_history import fetch_emp_work_history_for_riwayat_mutasi
from v2.v2_helper import format_date_series, log_duration

# Constants

JENIS_MUTASI_MAP: dict[int, int] = {
    # Smartoffice -> Kepegawaian
    1: 0,
    2: 1,
    3: 4,
    4: 6,
}


def main():
    try:
        start_time = time.time()

        work_history_df = fetch_emp_work_history_for_riwayat_mutasi()
        if work_history_df.empty:
            LOGGER.info("No data found in emp_work_history. Skipping.")
            return

        LOGGER.info(f"Fetched {len(work_history_df)} records.")

        work_history_df = cleanup(work_history_df)

        # Log how many records will be skipped
        records_before_filter = len(work_history_df)
        work_history_df = work_history_df[work_history_df["riwayat_sk_id"] > 0].reset_index(drop=True)
        records_after_filter = len(work_history_df)
        skipped_records = records_before_filter - records_after_filter

        if skipped_records > 0:
            LOGGER.warning(f"Skipping {skipped_records} records without riwayat_sk_id mapping.")

        if work_history_df.empty:
            LOGGER.info("All records filtered out (no valid riwayat_sk_id). Skipping.")
            return

        log_duration("generating data finish in ", start_time)

        start_time = time.time()
        save_riwayat_mutasi_from_emp_work_history(work_history_df)
        LOGGER.info(f"Successfully processed {len(work_history_df)} records.")
        log_duration("posting data finish in ", start_time)

    except Exception as e:
        LOGGER.error(f"Migration failed: {e}")
        LOGGER.error(traceback.format_exc())


def cleanup(df: pd.DataFrame) -> pd.DataFrame:
    """
    Transform and enrich raw emp_work_history data to the format expected by riwayat_mutasi.
    """
    # Prepare SK data
    sk_df = pd.DataFrame(fetch_all_riwayat_sk())
    if not sk_df.empty:
        # Bug Fix: Deduplicate SK to prevent record explosion in merge
        # Sort by id descending to pick the latest SK entry if duplicates exist
        sk_df = sk_df.sort_values("id", ascending=False).drop_duplicates(["pegawai_id", "nomor_sk"]).reset_index(drop=True)
        sk_df["golongan_id"] = sk_df["golongan_id"].apply(lambda x: 0 if pd.isna(x) else x).astype(int)

    # Merge to get riwayat_sk_id based on (pegawai_id, nomor_sk)
    df = df.merge(
        sk_df[["id", "pegawai_id", "nomor_sk"]],
        how="left",
        left_on=["pegawai_id", "nomor_sk"],
        right_on=["pegawai_id", "nomor_sk"],
    ).rename(columns={"id": "riwayat_sk_id"})
    df["riwayat_sk_id"] = df["riwayat_sk_id"].fillna(0).astype(int)

    # Map golongan_id from SK using riwayat_sk_id
    if not sk_df.empty:
        df = df.merge(
            sk_df[["id", "golongan_id"]].rename(columns={"id": "riwayat_sk_id"}),
            how="left",
            on="riwayat_sk_id",
        )
        df["golongan_id"] = df["golongan_id"].fillna(0).astype(int)
    else:
        df["golongan_id"] = 0

    # Map nama_golongan from master golongan
    golongan_df = pd.DataFrame(fetch_all_golongan())
    if not golongan_df.empty:
        df = df.merge(
            golongan_df[["id", "golongan"]].rename(columns={"id": "golongan_id", "golongan": "nama_golongan"}),
            how="left",
            on="golongan_id",
        )
    else:
        df["nama_golongan"] = None

    # Bug Fix: Initialize golongan_lama columns (not currently available in source query/mapping)
    df["golongan_lama_id"] = 0
    df["nama_golongan_lama"] = None

    # Map profesi (current) from jabatan_id
    profesi_df = pd.DataFrame(fetch_profesi())
    if not profesi_df.empty:
        # Bug Fix: Deduplicate profesi by jabatan_id to prevent record explosion
        profesi_df = profesi_df.sort_values("id", ascending=False).drop_duplicates("jabatan_id").reset_index(drop=True)
        
        current_prof = profesi_df[["jabatan_id", "id", "nama"]].rename(
            columns={"id": "profesi_id", "nama": "nama_profesi"}
        )
        df = df.merge(current_prof, how="left", on="jabatan_id")

        # Map profesi (old) from jabatan_lama_id
        old_prof = profesi_df[["jabatan_id", "id", "nama"]].rename(
            columns={"jabatan_id": "jabatan_lama_id", "id": "profesi_lama_id", "nama": "nama_profesi_lama"}
        )
        df = df.merge(old_prof, how="left", on="jabatan_lama_id")

        df["profesi_id"] = df["profesi_id"].fillna(0).astype(int)
        df["profesi_lama_id"] = df["profesi_lama_id"].fillna(0).astype(int)
    else:
        df["profesi_id"] = 0
        df["profesi_lama_id"] = 0
        df["nama_profesi"] = None
        df["nama_profesi_lama"] = None

    # Format dates
    df["tmt_berlaku"] = format_date_series(df["tmt_berlaku"])
    df["tanggal_berakhir"] = format_date_series(df["tanggal_berakhir"])

    # Normalize jenis_mutasi
    init_mask = df["nomor_sk"] == "Init Smartoffice"
    mapped = df["jenis_mutasi"].map(JENIS_MUTASI_MAP).fillna(0).astype(int)
    df["jenis_mutasi"] = mapped.where(~init_mask, 0)

    # Normalize is_deleted from {0,1} to {False,True}
    df["is_deleted"] = df["is_deleted"].eq(1)

    # Ensure integer types for these columns
    df = df.astype({
        "organisasi_id": int,
        "jabatan_id": int,
        "organisasi_lama_id": int,
        "jabatan_lama_id": int,
    })

    # Final Sanitization: Replace NaN/NaT/pd.NA with None for SQL compatibility
    df = df.replace({np.nan: None, pd.NaT: None, pd.NA: None})

    return df


if __name__ == '__main__':
    main()
