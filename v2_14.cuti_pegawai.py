from datetime import datetime

from core.kepegawaian.kepeg_cuti_pegawai import save_cuti_pegawai
from core.smartoffice.eo_cuti_pegawai import fetch_cuti_pegawai
from icecream import ic
import pandas as pd
# noinspection PyUnresolvedReferences
import swifter


def main():
    cp_df = fetch_cuti_pegawai()
    cp_df = cleanup(cp_df)
    save_cuti_pegawai(cp_df)
    pass


def cleanup(df: pd.DataFrame):
    claim_df = df[df["jenis_pengajuan_cuti"] == 1].reset_index(drop=True)
    # ic(claim_df.head().to_dict(orient="records"))
    df["created_at"] = df["created_at"].swifter.apply(
        lambda x: _datetime_to_str(x)
    )
    df["tanggal_mulai"] = df["tanggal_mulai"].swifter.apply(
        lambda x: _date_to_str(x)
    )
    df["tanggal_selesai"] = df["tanggal_selesai"].swifter.apply(
        lambda x: _date_to_str(x)
    )
    df.loc[:, "is_claimed"] = df.swifter.apply(lambda x: is_claimed(x, claim_df), axis=1)
    return df


def _datetime_to_str(x: datetime):
    return x.strftime("%Y-%m-%d %X")


def _date_to_str(x: str | datetime):
    # check if x type of date
    if x == "0000-00-00" or x is None:
        return "1945-08-17"
    return x.strftime("%Y-%m-%d")


def is_claimed(data_row: pd.Series, claimed_df: pd.DataFrame) -> bool:
    """
    Check if a cuti is claimed or not
    """
    if data_row["jenis_pengajuan_cuti"] == 1:
        return False
    ref_cuti_id = data_row["id"]
    claimed = claimed_df[
        (claimed_df["ref_cuti_id"] == ref_cuti_id)
        & (claimed_df["approval_cuti_status"] == 1)
        ].reset_index(drop=True)
    return not claimed.empty


if __name__ == "__main__":
    main()
