from config import get_smartoffice_connection_pool
import pandas as pd


def fetch_cuti_kuota():
    query = """
            SELECT ck.ck_id      AS id,
                   em.emp_id     AS pegawai_id,
                   ck.ck_pyear   AS tahun,
                   ck.ck_kuota   AS kuota,
                   ck.ck_diambil AS kuota_terpakai,
                   ck.ck_sisa    AS sisa_kuota,
                   ck.ck_expired AS expired
            FROM cuti_kuota AS ck
                     INNER JOIN employee AS em ON ck.emp_code = em.emp_code \
            """
    with get_smartoffice_connection_pool() as conn:
        with conn.cursor() as cursor:
            cursor.execute(query)
            return pd.DataFrame(cursor.fetchall())
