import time
import traceback

import numpy as np
import pandas as pd

from core.config import LOGGER
from core.kepegawaian.kepeg_biodata import fetch_biodata_for_riwayat_kontrak
from core.kepegawaian.kepeg_riwayat_kontrak import save_riwayat_kontrak_from_emp_contract
from core.smartoffice.emp_contract import fetch_emp_contract_for_riwayat_kontrak, fetch_smartoffice
from v2.v2_helper import log_duration


def main():
    try:
        start_time = time.time()
        contract_df = fetch_emp_contract_for_riwayat_kontrak()
        if contract_df.empty:
            LOGGER.info("No data found. Skipping.")
            return

        # Orphan detection (Optional but recommended in plan)
        total_src = fetch_smartoffice("SELECT COUNT(*) AS total FROM emp_contract", {}).iloc[0]["total"]
        orphans = total_src - len(contract_df)
        LOGGER.info(f"Fetched {len(contract_df)} records. ({orphans} orphans skipped)")

        contract_df = cleanup(contract_df)
        log_duration("Generating data finished in ", start_time)

        start_time = time.time()
        save_riwayat_kontrak_from_emp_contract(contract_df)
        LOGGER.info(f"Successfully processed {len(contract_df)} records.")
        log_duration("Posting data finished in ", start_time)
    except Exception as e:
        LOGGER.error(f"Migration v2_11 failed: {e}")
        traceback.print_exc()


def cleanup(df: pd.DataFrame):
    pegawai_df = fetch_biodata_for_riwayat_kontrak()
    nik_to_id = _build_pegawai_id_lookup(pegawai_df, id_col="id")

    # Map pegawai_id; default to 0 when not found, preserving original behavior
    df = df.copy()
    df["pegawai_id"] = df["nik"].map(nik_to_id).fillna(0).astype(int)

    # Normalize tanggal_sk, replacing the sentinel "0000-00-00" with 1945-08-17
    sentinel_replacement = "1945-08-17"
    tanggal_raw = df["tanggal_sk"].astype(str)
    tanggal_normalized = tanggal_raw.where(tanggal_raw != "0000-00-00", sentinel_replacement)
    df["tanggal_sk"] = pd.to_datetime(tanggal_normalized, errors="coerce")

    # Booleanize is_deleted
    df["is_deleted"] = df["is_deleted"].eq(1)

    # Flag latest per nik based on max tanggal_sk
    latest_per_nik = df.groupby("nik")["tanggal_sk"].transform("max")
    df["is_latest"] = df["tanggal_sk"].eq(latest_per_nik)

    # Derive jenis_kontrak with vectorized conditions:
    # - default 0
    # - 1 when nipam does not start with "KO-"
    # - 2 when is_latest and status_kerja == 8 (TERMINASI)
    df["jenis_kontrak"] = 0
    # nipam may be null; treat null as not starting with "KO-"
    nipam = df.get("nipam")
    not_ko = nipam.fillna("").astype(str).str.startswith("KO-").map(lambda v: not v)
    df.loc[not_ko, "jenis_kontrak"] = 1
    df.loc[df["is_latest"] & (df["status_kerja"] == 8), "jenis_kontrak"] = 2

    # NaN sanitization (LAST STEP)
    df = df.replace({np.nan: None, pd.NaT: None, pd.NA: None})

    return df


def _build_pegawai_id_lookup(pegawai_df: pd.DataFrame, id_col: str = "id") -> pd.Series:
    """
    Build a Series mapping nik -> id, preferring rows with status_kerja == 2
    when duplicates exist for a nik.
    """
    if pegawai_df.empty or "nik" not in pegawai_df.columns:
        return pd.Series(dtype="int64")

    tmp = pegawai_df.copy()
    # Prefer status_kerja == 2 by sorting a preference flag first
    tmp["__pref"] = (tmp["status_kerja"] != 2)
    tmp = tmp.sort_values(by=["nik", "__pref"])
    dedup = tmp.drop_duplicates(subset="nik", keep="first")
    mapping = dedup.set_index("nik")[id_col]
    return mapping


if __name__ == "__main__":
    main()
