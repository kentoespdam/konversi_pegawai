import time
import concurrent
import pandas as pd
import dask.dataframe as dd
from core.kepegawaian.kepeg_golongan import fetch_all_golongan
from core.kepegawaian.kepeg_jabatan import fetch_jabatan
from core.kepegawaian.kepeg_jenjang_pendidikan import fetch_jenjang_pendidikan
from core.kepegawaian.kepeg_organisasi import fetch_organisasi
from core.kepegawaian.kepeg_profesi import fetch_profesi
from core.post_data import kirim_pegawai
from core.smartoffice.eo_employee import fetch_data_for_pegawai
from icecream import ic


def main():
    raw_pegawai_df = pd.DataFrame(fetch_data_for_pegawai())
    jejang_pendidikan_df = pd.DataFrame(fetch_jenjang_pendidikan())
    organisasi_df = pd.DataFrame(fetch_organisasi())
    jabatan_df = pd.DataFrame(fetch_jabatan())
    golongan_df = pd.DataFrame(fetch_all_golongan())
    profesi_df = pd.DataFrame(fetch_profesi())

    raw_pegawai_df["pendidikanTerakhirId"] = 0
    raw_pegawai_df["organisasiId"] = 0
    raw_pegawai_df["jabatanId"] = 0
    raw_pegawai_df["profesiId"] = 0
    raw_pegawai_df["golonganId"] = 0

    start_time = time.time()
    raw_pegawai_dd = dd.from_pandas(raw_pegawai_df, npartitions=2)
    pegawai_dd = raw_pegawai_dd.map_partitions(
        validate_pegawai,
        jenjang_pendidikan_df=jejang_pendidikan_df,
        organisasi_df=organisasi_df,
        jabatan_df=jabatan_df,
        golongan_df=golongan_df,
        profesi_df=profesi_df,
        meta=raw_pegawai_dd
    ).compute()
    ic(f"total time finish in {time.time()-start_time}s")

    start_time = time.time()
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        executor.map(kirim_pegawai, [row for _, row in pegawai_dd.iterrows()])
    ic(f"total time finish in {time.time()-start_time}s")



def validate_pegawai(
        pegawai_list: pd.DataFrame,
        jenjang_pendidikan_df: pd.DataFrame,
        organisasi_df: pd.DataFrame,
        jabatan_df: pd.DataFrame,
        golongan_df: pd.DataFrame,
        profesi_df: pd.DataFrame
):
    pegawai_list.loc[:, "pendidikanTerakhirId"] = pegawai_list["pendidikanTerakhir"].apply(
        lambda x: get_pendidikan_terakhir_id(x, jenjang_pendidikan_df)
    )
    pegawai_list.loc[:, "organisasiId"] = pegawai_list["namaOrganisasi"].apply(
        lambda x: get_organisasi_id(x, organisasi_df)
    )
    pegawai_list.loc[:, "jabatanId"] = pegawai_list["namaJabatan"].apply(
        lambda x: get_jabatan_id(x, jabatan_df)
    )
    pegawai_list.loc[:, "golonganId"] = pegawai_list["golongan"].apply(
        lambda x: get_golongan_id(x, golongan_df)
    )
    pegawai_list.loc[:, "profesiId"] = pegawai_list["jabatanId"].apply(
        lambda x: get_profesi_id(x, profesi_df)
    )

    return pegawai_list


def get_pendidikan_terakhir_id(pendidikan_terakhir: str, jenjang_pendidikan_df: pd.DataFrame):
    result = jenjang_pendidikan_df.query(
        "nama == @pendidikan_terakhir").reset_index(drop=True)
    return result["id"].values[0] if not result.empty else 0


def get_organisasi_id(nama_organisasi: str, organisasi_df: pd.DataFrame):
    result = organisasi_df.query(
        "nama == @nama_organisasi").reset_index(drop=True)
    return result["id"].values[0] if not result.empty else 0


def get_jabatan_id(jabatan_name: str, jabatan_df: pd.DataFrame) -> int:
    result = jabatan_df.query("nama == @jabatan_name").reset_index(drop=True)
    return result["id"].values[0] if not result.empty else 0


def get_profesi_id(jabatan_id: int, profesi_df: pd.DataFrame):
    result = profesi_df.query(
        "jabatan_id == @jabatan_id").reset_index(drop=True)
    return result["id"].values[0] if not result.empty else 0


def get_golongan_id(nama_golongan: str, golongan_df: pd.DataFrame):
    result = golongan_df.query(
        "golongan == @nama_golongan").reset_index(drop=True)
    return result["id"].values[0] if not result.empty else 0


if __name__ == "__main__":
    main()
