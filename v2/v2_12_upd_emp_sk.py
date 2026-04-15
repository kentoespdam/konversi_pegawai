import time
import traceback
from typing import Dict, List

import pandas as pd

from core.config import LOGGER
from core.enums import EJenisSk
from core.kepegawaian.kepeg_pegawai import update_sk_pegawai
from core.kepegawaian.kepeg_sk import fetch_latest_sk_by_pegawai
from v2.v2_helper import format_datetime_series, log_duration

# Processed SK types are centralized here for easier maintenance
TARGET_JENIS_SK: List[EJenisSk] = [
    EJenisSk.SK_CAPEG,
    EJenisSk.SK_JABATAN,
    EJenisSk.SK_KENAIKAN_PANGKAT_GOLONGAN,
    EJenisSk.SK_MUTASI,
    EJenisSk.SK_PEGAWAI_TETAP,
]


def main() -> None:
    """Fetch latest SK per pegawai, normalize, split by jenis, and update per jenis."""
    try:
        start_time = time.time()
        df = fetch_latest_sk_by_pegawai()
        if df.empty:
            LOGGER.info("No data found to process. Skipping.")
            return

        LOGGER.info(f"Fetched {len(df)} latest SK records from riwayat_sk.")

        df = df.copy()
        df["tmt_berlaku"] = format_datetime_series(df["tmt_berlaku"])

        sk_by_jenis = split_by_jenis(df, TARGET_JENIS_SK)

        for jenis_sk, df_jenis in sk_by_jenis.items():
            if df_jenis.empty:
                continue

            # Validation: tmt_berlaku is required for everything except SK_CAPEG
            if jenis_sk != EJenisSk.SK_CAPEG:
                valid_mask = df_jenis["tmt_berlaku"].notnull()
                invalid_count = len(df_jenis) - valid_mask.sum()
                if invalid_count > 0:
                    LOGGER.warning(f"Skipping {invalid_count} records for {jenis_sk.name} due to missing tmt_berlaku.")
                    df_jenis = df_jenis[valid_mask].copy()

            if not df_jenis.empty:
                start_op = time.time()
                LOGGER.info(f"Updating {len(df_jenis)} records for {jenis_sk.name}...")
                update_sk_pegawai(df_jenis, jenis_sk)
                log_duration(f"update {jenis_sk.name} in", start_op)

        log_duration("Total v2_12 processing time:", start_time)

    except Exception as e:
        LOGGER.error(f"Migration v2_12 failed: {e}")
        LOGGER.error(traceback.format_exc())


def split_by_jenis(df: pd.DataFrame, jenis_list: List[EJenisSk]) -> Dict[EJenisSk, pd.DataFrame]:
    """
    Split the given DataFrame into a mapping of EJenisSk -> filtered DataFrame,
    containing only the latest row per (pegawai_id, jenis_sk) that matches the provided jenis list.
    """
    result: Dict[EJenisSk, pd.DataFrame] = {}
    for jenis in jenis_list:
        mask = df["jenis_sk"] == jenis.value
        result[jenis] = df[mask].reset_index(drop=True)
    return result


if __name__ == "__main__":
    main()
