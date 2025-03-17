import time
from core.kepegawaian.kepeg_jenjang_pendidikan import fetch_jenjang_pendidikan
from core.kepegawaian.pendidikan import fetch_pendidikan_pegawai
from core.post_data import do_post, do_put
from core.smartoffice.emp_education import fetch_data_for_pendidikan
import pandas as pd
from icecream import ic
import concurrent.futures
import swifter


def main():
    start_time = time.time()
    edu_df = pd.DataFrame(fetch_data_for_pendidikan())
    edu_df = cleanup_data(edu_df)
    ic(f"generating data finish in {time.time()-start_time}s")

    start_time = time.time()
    result = pd.DataFrame()
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        futures = {executor.submit(post_data, row)                   : row for row in edu_df.itertuples()}
        for future in concurrent.futures.as_completed(futures):
            try:
                result = pd.concat([result, pd.DataFrame([future.result()])])
            except Exception as e:
                print(e)
    ic(f"posting data finish in {time.time()-start_time}s")

    start_time = time.time()
    edu_df = update_data(edu_df)
    ic(f"updating data finish in {time.time()-start_time}s")

    start_time = time.time()
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        executor.map(accept_data, [row for row in edu_df.itertuples()])
    ic(f"putting data finish in {time.time()-start_time}s")


def cleanup_data(df: pd.DataFrame):
    jenjang_pendidikan_df = pd.DataFrame(fetch_jenjang_pendidikan())
    df["jenjangPendidikanId"] = df["jenjangPendidikan"].swifter.apply(
        lambda x: jenjang_pendidikan_df.loc[jenjang_pendidikan_df["nama"] == x, "id"].values[0])
    df.drop(columns=["jenjangPendidikan"], inplace=True)
    df["gelarBelakang"] = df["gelarBelakang"].swifter.apply(
        lambda x: "" if x == None or x == "Tidak ada" else x)
    df["isLatest"] = df["isLatest"].swifter.apply(
        lambda x: True if x == 1 else False)
    return df


def update_data(df: pd.DataFrame):
    pendidikan_df = pd.DataFrame(fetch_pendidikan_pegawai())
    df["id"] = df.swifter.apply(lambda x: filter_pendidikan(
        pendidikan_df, x.biodataId, x.jenjangPendidikanId, "id"), axis=1)
    return df


def filter_pendidikan(df: pd.DataFrame, biodataId: str, jenjangPendidikanId: int, col: str):
    result = df.query(
        "biodata_id == @biodataId and jenjang_id == @jenjangPendidikanId").reset_index(drop=True)
    return result[col].values[0] if not result.empty else 0


def post_data(df: dict):
    payload = {
        "biodataId": df.biodataId,
        "jenjangPendidikanId": df.jenjangPendidikanId,
        "gelarDepan": "",
        "gelarBelakang": df.gelarBelakang,
        "jurusan": df.jurusan,
        "institusi": df.institusi,
        "kota": "",
        "tahunMasuk": df.tahunMasuk,
        "tahunLulus": df.tahunLulus,
        "gpa": df.gpa,
        "isLatest": df.isLatest
    }

    return do_post("profil/pendidikan", payload)


def accept_data(df: dict):
    payload = {
        "biodataId": df.biodataId,
        "isLatest": df.isLatest
    }

    do_put(f"profil/pendidikan/{id}/accept", payload)

if __name__ == "__main__":
    main()
