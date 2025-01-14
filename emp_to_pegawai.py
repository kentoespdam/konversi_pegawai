import concurrent.futures
import time
import concurrent
from icecream import ic


from eo_employee import fetch_data_for_pegawai
from kepeg_golongan import fetch_golongan_id
from kepeg_jabatan import fetch_jabatan_id
from kepeg_jenjang_pendidikan import fetch_janjang_pendidikan_id
import pandas as pd
import dask.dataframe as dd

from kepeg_organisasi import fetch_organisasi_id
from kepeg_profesi import fetch_grade_profesi_id, fetch_profesi_id
from post_data import kirim_pegawai


def validate_pegawai(pegawai_list):
    pegawai_list["pendidikanTerakhirId"] = pegawai_list.apply(
        lambda x: fetch_janjang_pendidikan_id(
            x["pendidikanTerakhir"]) if x["pendidikanTerakhir"] is not None else None,
        axis=1,
    )
    pegawai_list["organisasiId"] = pegawai_list["namaOrganisasi"].apply(
        lambda x: fetch_organisasi_id(x) if x is not None else None
    )
    pegawai_list["jabatanId"] = pegawai_list["namaJabatan"].apply(
        lambda x:  fetch_jabatan_id(x) if x is not None else None
    )
    pegawai_list["golonganId"] = pegawai_list.apply(
        lambda x: fetch_golongan_id(x["golongan"], x["pangkat"]) if x["golongan"] is not None else None, axis=1
    )
    pegawai_list["profesiId"] = pegawai_list["jabatanId"].apply(
        lambda x: fetch_profesi_id(x) if x is not None else None)
    pegawai_list["gradeId"] = pegawai_list["profesiId"].apply(
        lambda x: fetch_grade_profesi_id(x) if x is not None else None
    )
    return pegawai_list


if __name__ == "__main__":
    pegawai_list = fetch_data_for_pegawai()
    pegawai_list = pd.DataFrame(pegawai_list)
    start_time = time.time()
    dask_pegawai_list: pd.DataFrame = dd.from_pandas(pegawai_list, npartitions=2).reset_index(
        drop=True)
    valid_pegawai_list = dask_pegawai_list.map_partitions(
        validate_pegawai).compute()
    ic(f"total time finish in {time.time()-start_time}s")

    start_time = time.time()
    with concurrent.futures.ProcessPoolExecutor() as executor:
        futures = {
            executor.submit(kirim_pegawai, data): data
            for index, data in valid_pegawai_list.iterrows()
        }

        for future in concurrent.futures.as_completed(futures):
            try:
                future.result()
            except Exception as exc:
                ic(exc)
    ic(f"post data finish in {time.time()-start_time}s")
