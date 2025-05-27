from config import get_kepegawaian_connection_pool
import pandas as pd


def save_data_riwayat_sk(datas: list):
    query = """
        INSERT INTO riwayat_sk (
            pegawai_id, nipam, nama, nomor_sk, jenis_sk, 
            tanggal_sk, tmt_berlaku, golongan_id, gaji_pokok, mkg_tahun, 
            mkg_bulan, kenaikan_berikutnya, mkgb_tahun, mkgb_bulan, update_master, 
            notes, created_by, version
        ) VALUES (
            %s, %s, %s, %s, %s, 
            %s, %s, %s, %s, %s, 
            %s, %s, %s, %s, %s, 
            %s, 'SYSTEM', 1
        ) ON DUPLICATE KEY UPDATE
            pegawai_id=VALUES(pegawai_id),
            nipam=VALUES(nipam),
            nama=VALUES(nama),
            nomor_sk=VALUES(nomor_sk),
            jenis_sk=VALUES(jenis_sk),
            tanggal_sk=VALUES(tanggal_sk),
            tmt_berlaku=VALUES(tmt_berlaku),
            golongan_id=VALUES(golongan_id),
            gaji_pokok=VALUES(gaji_pokok),
            mkg_tahun=VALUES(mkg_tahun),
            mkg_bulan=VALUES(mkg_bulan),
            kenaikan_berikutnya=VALUES(kenaikan_berikutnya),
            mkgb_tahun=VALUES(mkgb_tahun),
            mkgb_bulan=VALUES(mkgb_bulan),
            update_master=VALUES(update_master),
            notes=VALUES(notes)
    """
    with get_kepegawaian_connection_pool() as conn:
        with conn.cursor() as cursor:
            cursor.executemany(query, datas)
            conn.commit()


def fetch_latest_sk_by_pegawai() -> pd.DataFrame:
    query = """
        SELECT
            id,
            pegawai_id,
            jenis_sk,
            nomor_sk,
            tmt_berlaku,
            kenaikan_berikutnya 
        FROM
            (
            SELECT
                id,
                pegawai_id,
                jenis_sk,
                nomor_sk,
                tmt_berlaku,
                kenaikan_berikutnya,
                ROW_NUMBER() OVER ( PARTITION BY pegawai_id, jenis_sk ORDER BY tmt_berlaku DESC ) AS row_num 
            FROM
                riwayat_sk 
            ) AS riwayats 
        WHERE
            row_num = 1
    """
    with get_kepegawaian_connection_pool() as conn:
        with conn.cursor() as cursor:
            cursor.execute(query)
            return pd.DataFrame(cursor.fetchall())

def fetch_sk_golongan() -> pd.DataFrame:
    query = """
        SELECT
            id,
            pegawai_id,
            jenis_sk,
            nomor_sk,
            tanggal_sk,
            kenaikan_berikutnya 
        FROM
            (
            SELECT
                id,
                pegawai_id,
                jenis_sk,
                nomor_sk,
                tanggal_sk,
                kenaikan_berikutnya,
                ROW_NUMBER() OVER ( PARTITION BY pegawai_id, jenis_sk ORDER BY tanggal_sk DESC ) AS row_num 
            FROM
                riwayat_sk 
            ) AS riwayats 
        WHERE
            row_num = 1
    """
    with get_kepegawaian_connection_pool() as conn:
        with conn.cursor() as cursor:
            cursor.execute(query)
            return pd.DataFrame(cursor.fetchall())