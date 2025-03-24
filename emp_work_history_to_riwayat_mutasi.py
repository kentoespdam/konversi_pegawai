import time
import pandas as pd
from icecream import ic
from config import get_kepegawaian_connection_pool
from core.kepegawaian.kepeg_golongan import fetch_all_golongan
from core.kepegawaian.kepeg_jabatan import fetch_jabatan
from core.kepegawaian.kepeg_organisasi import fetch_organisasi
from core.kepegawaian.kepeg_profesi import fetch_profesi
from core.smartoffice.emp_mutation import fetch_data_for_riwayat_mutasi
import swifter


def fetch_pegawai_data():
    query = """
        SELECT
            peg.id AS pegawai_id,
            bio.nik 
        FROM
            pegawai AS peg
            INNER JOIN biodata AS bio ON peg.nik = bio.nik 
        ORDER BY
            bio.nik ASC
        """
    with get_kepegawaian_connection_pool() as conn:
        with conn.cursor() as cursor:
            cursor.execute(query)
            return pd.DataFrame(cursor.fetchall())


def fetch_sk_data():
    query = "SELECT id, nipam, nomor_sk, jenis_sk FROM riwayat_sk ORDER BY nipam ASC"

    with get_kepegawaian_connection_pool() as conn:
        with conn.cursor() as cursor:
            cursor.execute(query)
            return pd.DataFrame(cursor.fetchall())


def get_pegawai_id(nik, pegawai_df: pd.DataFrame):
    result = pegawai_df.query("nik==@nik")
    return result.pegawai_id.values[0] if not result.empty else 0


def get_sk_id(nipam, nomor_sk, sk_df: pd.DataFrame):
    result = sk_df.query("nipam==@nipam and nomor_sk==@nomor_sk")
    return result.id.values[0] if not result.empty else 0


def get_jenis_mutasi(jenis_sk: int):
    if jenis_sk == 0:
        return 3  # SK_KENAIKAN_PANGKAT_GOLONGAN
    elif jenis_sk == 1:
        return 3  # SK_CAPEG
    elif jenis_sk == 2:
        return 3  # SK_PEGAWAI_TETAP
    elif jenis_sk == 3:
        return 2  # SK_JABATAN
    elif jenis_sk == 4:
        return 1  # SK_MUTASI
    elif jenis_sk == 5:
        return 5  # SK_PENSIUN
    elif jenis_sk == 6:
        return 1  # SK_LAINNYA
    elif jenis_sk == 7:
        return 4  # SK_PENYESUAIAN_GAJI
    elif jenis_sk == 8:
        return 5  # SK_KENAIKAN_GAJI_BERKALA


def get_organisasi_id(nama_organisasi: str, organisasi_df: pd.DataFrame):
    result = organisasi_df.query("nama==@nama_organisasi")
    return result.id.values[0] if not result.empty else 0


def get_jabatan_id(nama_jabatan: str, jabatan_df: pd.DataFrame):
    result = jabatan_df.query("nama==@nama_jabatan")
    return result.id.values[0] if not result.empty else 0


def get_profesi_id(jabatan_id: int, profesi_df: pd.DataFrame):
    result = profesi_df.query(
        "jabatan_id == @jabatan_id").reset_index(drop=True)
    return result["id"].values[0] if not result.empty else 0


def get_profesi_name(profesi_id: int, profesi_df: pd.DataFrame):
    result = profesi_df.query(
        "id == @profesi_id").reset_index(drop=True)
    return result["nama"].values[0] if not result.empty else 0


def get_golongan_id(golongan_nama: int, golongan_df: pd.DataFrame):
    result = golongan_df.query(
        "golongan == @golongan_nama").reset_index(drop=True)
    return result["id"].values[0] if not result.empty else 0


def main():
    start_time = time.time()
    work_history_df = pd.DataFrame(fetch_data_for_riwayat_mutasi())
    work_history_df = cleanup_data(work_history_df)
    ic(f"generating data finish in {time.time()-start_time}s")

    start_time = time.time()
    datas = df_to_tuple_list(work_history_df)
    save_riwayat_mutasi(datas)
    ic(f"posting data finish in {time.time()-start_time}s")


def cleanup_data(df: pd.DataFrame):
    pegawai_df = fetch_pegawai_data()
    sk_df = fetch_sk_data()
    organisasi_df = pd.DataFrame(fetch_organisasi())
    jabatan_df = pd.DataFrame(fetch_jabatan())
    profesi_df = pd.DataFrame(fetch_profesi())
    golongan_df = pd.DataFrame(fetch_all_golongan())
    df["pegawai_id"] = df["nik"].swifter.apply(
        lambda x: get_pegawai_id(x, pegawai_df))
    df["riwayat_sk_id"] = df.swifter.apply(
        lambda x: get_sk_id(x["nipam"], x["no_sk"], sk_df), axis=1)
    df["jenis_mutasi"] = df["jenis_sk"].swifter.apply(
        lambda x: get_jenis_mutasi(x))
    df["tmt_berlaku"] = df["tmt_berlaku"].swifter.apply(
        lambda x: x.strftime("%Y-%m-%d") if x else "")
    df["tanggal_berakhir"] = df["tanggal_berakhir"].swifter.apply(
        lambda x: x.strftime("%Y-%m-%d") if x else None)
    df["organisasi_id"] = df["nama_organisasi"].swifter.apply(
        lambda x: get_organisasi_id(x, organisasi_df))
    df["organisasi_lama_id"] = df["nama_organisasi_lama"].swifter.apply(
        lambda x: get_organisasi_id(x, organisasi_df))
    df["jabatan_id"] = df["nama_jabatan"].swifter.apply(
        lambda x: get_jabatan_id(x, jabatan_df))
    df["jabatan_lama_id"] = df["nama_jabatan_lama"].swifter.apply(
        lambda x: get_jabatan_id(x, jabatan_df))
    df["profesi_id"] = df["jabatan_id"].swifter.apply(
        lambda x: get_profesi_id(x, profesi_df))
    df["nama_profesi"] = df["profesi_id"].swifter.apply(
        lambda x: get_profesi_name(x, profesi_df))
    df["profesi_lama_id"] = df["jabatan_id"].swifter.apply(
        lambda x: get_profesi_id(x, profesi_df))
    df["nama_profesi_lama"] = df["profesi_id"].swifter.apply(
        lambda x: get_profesi_name(x, profesi_df))
    df["golongan_id"] = df["golongan"].swifter.apply(
        lambda x: get_golongan_id(x, golongan_df))

    df = df[(df["pegawai_id"] > 0) & (
        df["riwayat_sk_id"] > 0)].reset_index(drop=True)
    return df


def df_to_tuple_list(df: pd.DataFrame):
    return [(
        row.pegawai_id,
        row.riwayat_sk_id,
        row.tmt_berlaku,
        row.tanggal_berakhir,
        row.jenis_mutasi,
        row.organisasi_id if row.organisasi_id > 0 else None,
        row.nama_organisasi,
        row.jabatan_id if row.jabatan_id > 0 else None,
        row.nama_jabatan,
        row.profesi_id if row.profesi_id > 0 else None,
        row.nama_profesi,
        row.golongan_id if row.golongan_id > 0 else None,
        row.golongan,
        row.organisasi_lama_id if row.organisasi_lama_id > 0 else None,
        row.nama_organisasi_lama,
        row.jabatan_lama_id if row.jabatan_lama_id > 0 else None,
        row.nama_jabatan_lama,
        row.profesi_lama_id if row.profesi_lama_id > 0 else None,
        row.nama_profesi_lama
    ) for row in df.itertuples()]


def save_riwayat_mutasi(datas):
    query = """
    INSERT INTO riwayat_mutasi (
        pegawai_id, riwayat_sk_id, tmt_berlaku, tanggal_berakhir, jenis_mutasi, 
        organisasi_id, nama_organisasi, jabatan_id, nama_jabatan, profesi_id,
        nama_profesi, golongan_id, nama_golongan, organisasi_lama_id, nama_organisasi_lama,
        jabatan_lama_id, nama_jabatan_lama, profesi_lama_id, nama_profesi_lama
        ) VALUES (
            %s, %s, %s, %s, %s, 
            %s, %s, %s, %s, %s, 
            %s, %s, %s, %s, %s,
            %s, %s, %s, %s
        )
    """
    with get_kepegawaian_connection_pool() as conn:
        with conn.cursor() as cursor:
            cursor.executemany(query, datas)
            conn.commit()
            ic(cursor.rowcount, "record inserted")


if __name__ == "__main__":
    main()
