import time
from typing import Dict, List

import pandas as pd

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


# ... existing code ...

def main() -> None:
    """Fetch latest SK per pegawai, normalize, split by jenis, and update per jenis."""
    riwayat_sk = fetch_latest_sk_by_pegawai()
    if riwayat_sk.empty:
        return

    riwayat_sk = normalize_sk_dates(riwayat_sk)
    sk_by_jenis = split_by_jenis(riwayat_sk, TARGET_JENIS_SK)

    for jenis_sk, df in sk_by_jenis.items():
        if not df.empty:
            start = time.time()
            update_sk_pegawai(df, jenis_sk)
            log_duration(f"update {jenis_sk.name} in", start)


# ... existing code ...

def normalize_sk_dates(df: pd.DataFrame) -> pd.DataFrame:
    """
    Normalize datetime columns to standardized string format expected downstream.
    """
    df["kenaikan_berikutnya"] = format_datetime_series(df["kenaikan_berikutnya"])
    df["tmt_berlaku"] = format_datetime_series(df["tmt_berlaku"])
    return df


# ... existing code ...

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


# ... existing code ...

if __name__ == "__main__":
    main()
