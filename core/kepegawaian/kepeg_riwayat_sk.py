import pandas as pd
from icecream import ic
from core.config import get_kepegawaian_connection_pool


def save_riwayat_sk_from_emp_sk(df: pd.DataFrame):
    data = [(
        row.pegawai_id,
        row.nipam,
        row.nama,
        row.nomor_sk,
        row.jenis_sk,
        row.tanggal_sk,
        row.tmt_berlaku,
        row.golongan_id if row.golongan_id > 0 else None,
        row.gaji_pokok,
        row.mkg_tahun,
        row.mkg_bulan,
        row.kenaikan_berikutnya,
        row.mkgb_tahun,
        row.mkgb_bulan,
        row.update_master,
        row.notes,
        row.is_deleted,
        0, 
        'SYSTEM'
    )for row in df.itertuples(index=False)]

    query = """
        INSERT INTO riwayat_sk (
            pegawai_id, nipam, nama, nomor_sk, jenis_sk, 
            tanggal_sk, tmt_berlaku, golongan_id, gaji_pokok, mkg_tahun, 
            mkg_bulan, kenaikan_berikutnya, mkgb_tahun, mkgb_bulan, update_master, 
            notes, is_deleted, version, created_by
        ) VALUES (
            %s, %s, %s, %s, %s,
            %s, %s, %s, %s, %s, 
            %s, %s, %s, %s, %s, 
            %s, %s, %s, %s
        )
    """
    try:
        with get_kepegawaian_connection_pool(autocommit=True) as connection:
            with connection.cursor() as cursor:
                cursor.executemany(query, data)
                affected = cursor.rowcount
                ic(affected, "row(s) affected")
                connection.commit()
    except Exception as e:
        ic(e)
        raise e


def fetch_all_riwayat_sk():
    query = "SELECT * FROM riwayat_sk"
    with get_kepegawaian_connection_pool() as conn:
        with conn.cursor() as cursor:
            cursor.execute(query)
            return cursor.fetchall()
