import time
from core.kepegawaian.jenis_kartu import fetch_all_jenis_kartu
from core.post_data import do_post
from core.smartoffice.emp_card import fetch_data_for_kartu_identitas
from icecream import ic
import concurrent.futures
import pandas as pd
import swifter


def main():
    start_time = time.time()
    card_df = pd.DataFrame(fetch_data_for_kartu_identitas())
    jenis_kartu_df = pd.DataFrame(fetch_all_jenis_kartu())
    card_df.loc[:, "jenisKartuId"] = card_df["jenisKartu"].swifter.apply(
        lambda x: get_kartu_identitas_id(x, jenis_kartu_df)
    )
    card_df.loc[:, "tanggalExpired"] = card_df["tanggalExpired"].swifter.apply(
        lambda x: x.strftime('%Y-%m-%d')if x is not None else "")
    card_df.loc[:, "tanggalTerima"] = card_df["tanggalTerima"].swifter.apply(
        lambda x: x.strftime('%Y-%m-%d')if x is not None else "")
    card_df.drop(columns=["jenisKartu"], inplace=True)
    ic(f"generating data finish in {time.time()-start_time}s")

    start_time = time.time()
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        executor.map(post_data, [row for row in card_df.itertuples()])
    ic(f"posting data finish in {time.time()-start_time}s")


def get_kartu_identitas_id(nama: str, df: pd.DataFrame):
    filtered = df.query("nama==@nama")["id"].reset_index(drop=True)
    return filtered.values[0] if not filtered.empty else 0


def post_data(row):
    payload = {
        "nik": row.nik,
        "jenisKartuId": row.jenisKartuId,
        "nomorKartu": row.nomorKartu,
        "tanggalExpired": row.tanggalExpired,
        "tanggalTerima": row.tanggalTerima,
        "notes": row.notes
    }
    do_post("profil/kartu-identitas", payload)


if __name__ == "__main__":
    main()
