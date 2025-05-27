from config import get_smartoffice_connection_pool
import pandas as pd
from icecream import ic


def fetch_emp_sk_for_riwayat_sk():
    query = """
        SELECT
            es.emp_id AS pegawai_id,
            em.emp_code AS nipam,
            emp_profile.emp_name AS nama,
            es.no_sk AS nomor_sk,
            es.jenis_sk - 1 AS jenis_sk,
            es.tgl_sk AS tanggal_sk,
            es.tmt_sk AS tmt_berlaku,
            IFNULL( es.golongan_id, 0 ) AS golongan_id,
            IFNULL( es.gaji_pokok, 0 ) AS gaji_pokok,
            IFNULL( es.mkg_tahun, 0 ) AS mkg_tahun,
            IFNULL( es.mkg_bulan, 0 ) AS mkg_bulan,
            es.kenaikan_berikutnya,
            IFNULL( es.mkgb_tahun, 0 ) AS mkgb_tahun,
            IFNULL( es.mkgb_bulan, 0 ) AS mkgb_bulan,
            IFNULL( es.flag_update_master, 0 ) AS update_master,
            es.keterangan AS notes,
        IF
            ( es.`status` = 3, TRUE, FALSE ) AS is_deleted 
        FROM
            emp_sk AS es
            INNER JOIN employee AS em ON es.emp_id = em.emp_id
            INNER JOIN emp_profile ON em.emp_profile_id = emp_profile.emp_profile_id
        """
    with get_smartoffice_connection_pool() as conn:
        with conn.cursor() as cursor:
            cursor.execute(query)
            return cursor.fetchall()


def fetch_data_for_riwayat_sk():
    query = """
        SELECT
            em.emp_code AS nipam,
            ep.emp_name AS nama,
            esk.no_sk AS nomor_sk,
            esk.jenis_sk,
            esk.tgl_sk AS tanggal_sk,
            esk.tmt_sk AS tmt_berlaku,
            gol.golongan,
            esk.gaji_pokok,
            esk.mkg_tahun,
            esk.mkg_bulan,
            esk.kenaikan_berikutnya,
            esk.mkgb_tahun,
            esk.mkgb_bulan,
            esk.flag_update_master AS update_master,
            esk.keterangan AS notes 
        FROM
            emp_sk AS esk
            INNER JOIN employee AS em ON esk.emp_id = em.emp_id
            INNER JOIN emp_profile AS ep ON em.emp_profile_id = ep.emp_profile_id
            LEFT JOIN golongan AS gol ON esk.golongan_id = gol.id
        """
    with get_smartoffice_connection_pool() as conn:
        with conn.cursor() as cursor:
            cursor.execute(query)
            return cursor.fetchall()


def save_emp_sk_from_emp_work_history(df: pd.DataFrame):
    data = [(
        row.emp_id,
        row.jenis_sk,
        row.ref_id,
        row.no_sk,
        row.tgl_sk,
        row.tmt_sk,
        row.status,
        row.notes
    ) for row in df.itertuples(index=False)]

    query = """
        INSERT INTO emp_sk (
            emp_id, jenis_sk, ref_id, no_sk, tgl_sk, 
            tmt_sk, status, keterangan
        ) VALUES (
            %s, %s, %s, %s, %s, 
            %s, %s, %s
        )
    """
    with get_smartoffice_connection_pool() as conn:
        with conn.cursor() as cursor:
            cursor.executemany(query, data)
            affected = cursor.rowcount
            ic(affected, "row(s) affected")
            conn.commit()
