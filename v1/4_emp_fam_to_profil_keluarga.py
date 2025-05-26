import concurrent.futures
import concurrent
import time
import pandas as pd
from icecream import ic
from core.post_data import do_post
from core.smartoffice.emp_family import fetch_data_for_profil_keluarga
from dotenv import load_dotenv
import swifter

load_dotenv()


def main():
    start_time = time.time()
    fam_df = pd.DataFrame(fetch_data_for_profil_keluarga())
    fam_df = cleanup(fam_df)
    fam_df["tanggalLahir"] = fam_df["tanggalLahir"].swifter.apply(
        lambda x: x.strftime('%Y-%m-%d'))
    ic(f"generating data finish in {time.time()-start_time}s")

    start_time = time.time()
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        executor.map(post_data, [row for row in fam_df.itertuples()])
    ic(f"posting data finish in {time.time()-start_time}s")


def cleanup(df: pd.DataFrame):
    df.loc[:, "tanggungan"] = df["tanggungan"].swifter.apply(
        lambda x: True if x == 1 else False)
    df.loc[:, "statusPendidikan"] = df.swifter.apply(
        lambda x: cleanup_status_pendidikan(x), axis=1)
    df.loc[:, "statusKawin"] = df.swifter.apply(
        lambda x: cleanup_status_kawin(x), axis=1)
    return df


def cleanup_status_pendidikan(x: dict):
    if x["hubunganKeluarga"] in {'SUAMI', 'ISTRI'}:
        return "SELESAI_SEKOLAH"
    else:
        return x["statusPendidikan"]


def cleanup_status_kawin(x: dict):
    if x["hubunganKeluarga"] in {'SUAMI', 'ISTRI'}:
        return "KAWIN"

    if x["fam_sts_nikah"] == 1:
        return "BELUM_KAWIN"
    else:
        return "KAWIN"


def post_data(df: dict):
    payload = {
        "biodataId": df.biodataId,
        "nik": df.nik,
        "nama": df.nama,
        "jenisKelamin": df.jenisKelamin,
        "agama": "ISLAM",
        "hubunganKeluarga": df.hubunganKeluarga,
        "tempatLahir": df.tempatLahir,
        "tanggalLahir": df.tanggalLahir,
        "tanggungan": df.tanggungan,
        "pendidikanId": df.pendidikanId,
        "statusPendidikan": df.statusPendidikan,
        "statusKawin": df.statusKawin,
        "notes": df.notes,
    }

    do_post("profil/keluarga", payload)


if __name__ == '__main__':
    main()
