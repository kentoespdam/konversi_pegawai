import pymysql

from config import DEFAULT_KEPEGAWAIAN_DB_CONFIG


def fetch_golongan_id(golongan: str, pangkat: str) -> int:
    koneksi = pymysql.connect(**DEFAULT_KEPEGAWAIAN_DB_CONFIG)
    query = """
            SELECT id FROM golongan WHERE golongan = %s AND pangkat = %s
            """
    params=(golongan, pangkat)
    with koneksi.cursor() as cur:
        cur.execute(query, params)
        return cur.fetchone()["id"] if cur.rowcount > 0 else None
