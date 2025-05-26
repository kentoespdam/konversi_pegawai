import time
import concurrent.futures
import pandas as pd
from icecream import ic
from core.post_data import do_post
from core.smartoffice.emp_training import fetch_data_for_pelatihan


def main():
    start_time = time.time()
    training_df = pd.DataFrame(fetch_data_for_pelatihan())
    ic(f"generating data finish in {time.time()-start_time}s")

    start_time = time.time()
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        executor.map(post_data, [row for row in training_df.itertuples()])
    ic(f"posting data finish in {time.time()-start_time}s")


def post_data(row: dict):
    payload = {
        "biodataId": row.biodataId,
        "jenisPelatihanId": row.jenisPelatihanId,
        "nama": row.nama,
        "lembaga": row.lembaga,
        "tanggalMulai": row.tanggalMulai.strftime('%Y-%m-%d') if row.tanggalMulai is not None else "",
        "tanggalSelesai": row.tanggalSelesai.strftime('%Y-%m-%d') if row.tanggalSelesai is not None else "",
        "lulus": row.lulus,
        "nilai": row.nilai,
        "ikatanDinas": row.ikatanDinas,
        "tanggalAkhirIkatan": row.tanggalAkhirIkatan.strftime('%Y-%m-%d') if row.tanggalAkhirIkatan is not None else "",
        "notes": row.notes
    }

    do_post("profil/pelatihan", payload)


if __name__ == '__main__':
    main()
