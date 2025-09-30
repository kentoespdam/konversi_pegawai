import time

import pandas as pd

from core.enums import EHubunganKeluarga
from core.kepegawaian.kepeg_profil_keluarga import save_profil_keluarga_from_emp_profile
from core.smartoffice.emp_family import fetch_emp_family_for_profil_keluarga
from v2.v2_helper import format_date_series, log_duration

CORE_RELATION_IDS = {EHubunganKeluarga.SUAMI.value, EHubunganKeluarga.ISTRI.value, EHubunganKeluarga.AYAH.value,
                     EHubunganKeluarga.IBU.value, EHubunganKeluarga.ANAK.value,
                     EHubunganKeluarga.SAUDARA.value}  # domain: inti keluarga


def main() -> None:
    start = time.perf_counter()
    family_df = fetch_emp_family_for_profil_keluarga()
    family_df = transform_family_df(family_df)
    log_duration("generating data finish", start)

    start = time.perf_counter()
    save_profil_keluarga_from_emp_profile(family_df)
    log_duration("posting data finish", start)


def transform_family_df(df: pd.DataFrame) -> pd.DataFrame:
    """
    Normalize and enrich family dataframe to match profil_keluarga schema expectations.
    - tanggal_lahir formatted as YYYY-MM-DD (None preserved)
    - tanggungan coerced to bool
    - status_pendidikan and status_kawin normalized via rules
    - agama defaulted to 1
    """
    df["tanggal_lahir"] = format_date_series(df["tanggal_lahir"])

    # tanggungan: 1 -> True, others -> False
    df["tanggungan"] = df["tanggungan"].eq(1)

    # row-wise normalizations depending on multiple columns
    df["status_pendidikan"] = df.apply(
        lambda x: _cleanup_status_pendidikan(
            x["status_pendidikan"], x["hubungan_keluarga"], x["tanggungan"]
        ),
        axis=1,
    )
    df["status_kawin"] = df.apply(
        lambda x: _cleanup_status_kawin(
            x["hubungan_keluarga"], x["tanggungan"], x["status_kawin"]
        ),
        axis=1,
    )

    # default constant
    df["agama"] = 1
    return df


def _cleanup_status_pendidikan(status_pendidikan: int, hubungan_keluarga: int, tanggungan: bool) -> int:
    """
    Normalize pendidikan status when it's invalid (< 0).
    - For hubungan_keluarga in {0, 1} => 2
    - Else => 1 if tanggungan else 2
    """
    if status_pendidikan < 0:
        if hubungan_keluarga in (0, 1):
            return 2
        return 1 if tanggungan else 2
    return status_pendidikan


def _cleanup_status_kawin(hubungan_keluarga: int, tanggungan: bool, status_kawin: int) -> int:
    """
    Normalize kawin status.
    - Core relations {0,1,2,3} => 1
    - If tanggungan => 0
    - If hubungan_keluarga == 4 and status_kawin == 2 => 0
    - Otherwise keep original status_kawin
    """
    if hubungan_keluarga in CORE_RELATION_IDS:
        return 1
    if tanggungan:
        return 0
    if hubungan_keluarga == 4 and status_kawin == 2:
        return 0
    return status_kawin


if __name__ == "__main__":
    main()
