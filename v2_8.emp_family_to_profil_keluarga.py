import pandas as pd
import time
import swifter
from icecream import ic

from core.kepegawaian.kepeg_profil_keluarga import save_profil_keluarga_from_emp_profile
from core.smartoffice.emp_family import fetch_emp_family_for_profil_keluarga


def main():
    start_time = time.time()
    fam_df = pd.DataFrame(fetch_emp_family_for_profil_keluarga())
    fam_df = cleanup(fam_df)
    ic(f"generating data finish in {time.time()-start_time}s")

    start_time = time.time()
    save_profil_keluarga_from_emp_profile(fam_df)
    ic(f"posting data finish in {time.time()-start_time}s")


def cleanup(df: pd.DataFrame):
    df["tanggal_lahir"] = df["tanggal_lahir"].swifter.apply(
        lambda x: x.strftime('%Y-%m-%d') if x is not None else None)
    df["tanggungan"] = df["tanggungan"].swifter.apply(
        lambda x: True if x == 1 else False)
    df["status_pendidikan"] = df.swifter.apply(
        lambda x: cleanup_status_pendidikan(x), axis=1)
    df["status_kawin"] = df.swifter.apply(
        lambda x: cleanup_status_kawin(x), axis=1)
    df["agama"] = 1
    return df


def cleanup_status_pendidikan(row: pd.Series) -> int:
    """
    Clean up pendidikan status
    """
    if row["status_pendidikan"] < 0:
        if row["hubungan_keluarga"] in [0, 1]:
            return 2
        elif row["tanggungan"]:
            return 1
        elif not row["tanggungan"]:
            return 2
        else:
            return 0

    return row["status_pendidikan"]


def cleanup_status_kawin(row: pd.Series) -> int:
    """Clean up kawin status."""

    if row["hubungan_keluarga"] in [0, 1, 2, 3]:
        return 1
    elif row["tanggungan"]:
        return 0
    elif row["hubungan_keluarga"] == 4 and row["status_kawin"] == 2:
        return 0

    return row["status_kawin"]


if __name__ == "__main__":
    main()
