import time
import pandas as pd
from core.kepegawaian.jenis_kartu import fetch_all_jenis_kartu
from core.kepegawaian.kepeg_kartu_identitas import save_kartu_identitas_from_emp_card
from core.smartoffice.emp_card import fetch_emp_card_for_kartu_identitas
from icecream import ic
import swifter


def main():
    start_time = time.time()
    kartu_identitas_df = pd.DataFrame(fetch_emp_card_for_kartu_identitas())
    kartu_identitas_df = cleanup(kartu_identitas_df)
    ic(f"generating data finish in {time.time()-start_time}s")

    start_time = time.time()
    save_kartu_identitas_from_emp_card(kartu_identitas_df)
    ic(f"posting data finish in {time.time()-start_time}s")


def cleanup(df: pd.DataFrame):
    jenis_kartu_df = pd.DataFrame(fetch_all_jenis_kartu())
    df["jenis_kitas_id"] = df["jenis_kitas"].swifter.apply(
        lambda x: _get_kartu_identitas_id(jenis_kartu_df, x)
    )

    df["tanggal_expired"] = df["tanggal_expired"].swifter.apply(
        lambda x: x.strftime("%Y-%m-%d") if x is not None else None
    )
    df["tanggal_terima"] = df["tanggal_terima"].swifter.apply(
        lambda x: x.strftime("%Y-%m-%d") if x is not None else None
    )
    df["is_deleted"] = df["is_deleted"].swifter.apply(
        lambda x: True if x == 1 else False
    )
    return df


def _get_kartu_identitas_id(df: pd.DataFrame, jenis_kitas: str):
    if jenis_kitas is None or jenis_kitas == "":
        return 0
    result = df.query("nama==@jenis_kitas").reset_index(drop=True)
    return result.iloc[0]["id"] if not result.empty else 0


if __name__ == "__main__":
    main()
