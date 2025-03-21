import concurrent.futures
from multiprocessing import Pool
import time
import concurrent
from icecream import ic
import pandas as pd
import dask.dataframe as dd
from core.kepegawaian.kepeg_golongan import fetch_golongan_id
from core.kepegawaian.kepeg_jabatan import fetch_jabatan_id
from core.kepegawaian.kepeg_jenjang_pendidikan import fetch_jenjang_pendidikan_id
from core.kepegawaian.kepeg_organisasi import fetch_organisasi_id
from core.kepegawaian.kepeg_profesi import fetch_profesi_id_by_jabatan_id
from core.post_data import kirim_pegawai
from core.smartoffice.eo_employee import fetch_data_for_pegawai
import swifter


def validate_pegawai(pegawai_list: pd.DataFrame):
    pegawai_list["pendidikanTerakhirId"] = pegawai_list["pendidikanTerakhir"].swifter.apply(
        lambda x: fetch_jenjang_pendidikan_id(x)
    )
    pegawai_list["organisasiId"] = pegawai_list["namaOrganisasi"].swifter.apply(
        lambda x: fetch_organisasi_id(x)
    )
    pegawai_list["jabatanId"] = pegawai_list["namaJabatan"].swifter.apply(
        lambda x:  fetch_jabatan_id(x)
    )
    pegawai_list["golongan"] = pegawai_list["golongan"].fillna("")
    pegawai_list["golonganId"] = pegawai_list["golongan"].swifter.apply(
        lambda x: fetch_golongan_id(x)
    )
    pegawai_list["profesiId"] = pegawai_list["jabatanId"].swifter.apply(
        lambda x: fetch_profesi_id_by_jabatan_id(x)
    )
    return pegawai_list


if __name__ == "__main__":
    pegawai_list = fetch_data_for_pegawai()
    pegawai_list = pd.DataFrame(pegawai_list)
    pegawai_list["pendidikanTerakhirId"] = 0
    pegawai_list["organisasiId"] = 0
    pegawai_list["jabatanId"] = 0
    pegawai_list["profesiId"] = 0
    pegawai_list["golonganId"] = 0

    start_time = time.time()
    dask_pegawai_list = dd.from_pandas(
        pegawai_list, npartitions=2)
    valid_pegawai_list = dask_pegawai_list.map_partitions(
        validate_pegawai, meta=dask_pegawai_list).compute()
    ic(f"total time finish in {time.time()-start_time}s")

    start_time = time.time()
    # multi threading
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        executor.map(kirim_pegawai, [row for _,
                     row in valid_pegawai_list.iterrows()])

    # multi processing
    # with Pool(processes=10) as pool:
    #     pool.map(kirim_pegawai, [row for _,
    #              row in valid_pegawai_list.iterrows()])

    ic(f"post data finish in {time.time()-start_time}s")
