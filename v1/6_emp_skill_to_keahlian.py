import time
import pandas as pd
from icecream import ic
import concurrent.futures
import swifter
from core.post_data import do_post
from core.smartoffice.emp_skill import fetch_data_for_keahlian


def main():
    start_time = time.time()
    skill_df = pd.DataFrame(fetch_data_for_keahlian())
    skill_df["sertifikasi"] = skill_df["sertifikasi"].swifter.apply(
        lambda x: True if x == 1 else False)
    ic(f"generating data finish in {time.time()-start_time}s")

    start_time = time.time()
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        executor.map(post_data, [row for row in skill_df.itertuples()])
    ic(f"posting data finish in {time.time()-start_time}s")


def post_data(row: dict):
    payload = {
        "biodataId": row.biodataId,
        "keahlianId": row.keahlianId,
        "kualifikasi": row.kualifikasi,
        "sertifikasi": row.sertifikasi,
        "institusi": row.institusi,
        "tahun": row.tahun,
        "masaBerlaku": ""
    }
    do_post("profil/keahlian", payload)


if __name__ == "__main__":
    main()
