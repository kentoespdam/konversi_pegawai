import time
import traceback

import pandas as pd

from core.config import LOGGER
from core.enums import EHubunganKeluarga
from core.kepegawaian.kepeg_profil_keluarga import save_profil_keluarga_from_emp_profile
from core.smartoffice.emp_family import fetch_emp_family_for_profil_keluarga
from v2.v2_helper import format_date_series, log_duration

CORE_RELATION_IDS = {
    EHubunganKeluarga.SUAMI.value,
    EHubunganKeluarga.ISTRI.value,
    EHubunganKeluarga.AYAH.value,
    EHubunganKeluarga.IBU.value
}  # domain: inti keluarga


def main() -> None:
    try:
        start = time.perf_counter()
        family_df = fetch_emp_family_for_profil_keluarga()

        if family_df.empty:
            LOGGER.info("No family data found. Skipping migration.")
            return

        LOGGER.info(f"Fetched {len(family_df)} records")

        family_df = transform_family_df(family_df)
        log_duration("generating data finish", start)

        start = time.perf_counter()
        save_profil_keluarga_from_emp_profile(family_df)
        log_duration("posting data finish", start)
        LOGGER.info(f"Successfully migrated {len(family_df)} family records")

    except Exception as e:
        LOGGER.error(f"Migration failed: {str(e)}")
        LOGGER.error(traceback.format_exc())


def transform_family_df(df: pd.DataFrame) -> pd.DataFrame:
    """
    Normalize and enrich family dataframe to match profil_keluarga schema expectations.
    - tanggal_lahir formatted as YYYY-MM-DD (None preserved)
    - tanggungan coerced to bool
    - status_pendidikan and status_kawin normalized via rules
    - agama defaulted to 1
    """
    result_df = df.copy()
    result_df["tanggal_lahir"] = format_date_series(result_df["tanggal_lahir"])

    # tanggungan: 1 -> True, others -> False
    result_df["tanggungan"] = result_df["tanggungan"].eq(1)

    # default constant
    result_df["agama"] = 1

    # Vectorized status_pendidikan cleanup
    result_df["status_pendidikan"] = _cleanup_status_pendidikan_vectorized(
        result_df["status_pendidikan"],
        result_df["hubungan_keluarga"],
        result_df["umur"]
    )

    # Vectorized status_kawin cleanup
    result_df["status_kawin"] = _cleanup_status_kawin_vectorized(
        result_df["status_kawin"],
        result_df["hubungan_keluarga"]
    )

    # Sanitize NaN/NaT to None for MySQL compatibility
    result_df = result_df.where(pd.notna(result_df), None)

    return result_df


def _cleanup_status_pendidikan_vectorized(
        status_pendidikan: pd.Series,
        hubungan_keluarga: pd.Series,
        umur: pd.Series
) -> pd.Series:
    """
    Vectorized version of status_pendidikan normalization.
    """
    # Create result series with original values
    result = status_pendidikan.copy()
    mask_core = hubungan_keluarga.isin({
        EHubunganKeluarga.SUAMI.value,
        EHubunganKeluarga.ISTRI.value,
        EHubunganKeluarga.AYAH.value,
        EHubunganKeluarga.IBU.value
    })
    result.loc[mask_core] = 2
    mask_invalid = status_pendidikan.eq(-1)
    mask_umur = umur.le(7)
    result.loc[mask_invalid & mask_umur & ~mask_core] = 0
    result.loc[mask_invalid & ~mask_umur & ~mask_core] = 1
    result.loc[umur.gt(25) & hubungan_keluarga.eq(EHubunganKeluarga.ANAK.value)] = 2

    return result


def _cleanup_status_kawin_vectorized(
        status_kawin: pd.Series,
        hubungan_keluarga: pd.Series,
) -> pd.Series:
    """
    Vectorized version of status_kawin normalization.
    """
    # Create result series with original values
    result = status_kawin.copy()
    mask = hubungan_keluarga.isin(CORE_RELATION_IDS)
    result.loc[mask] = 1
    mask_anak = hubungan_keluarga.eq(EHubunganKeluarga.ANAK.value)
    result.loc[~mask & mask_anak & status_kawin.eq(-1)] = 0
    result.loc[~mask_anak & status_kawin.eq(-1)] = 1

    return result


if __name__ == "__main__":
    main()
