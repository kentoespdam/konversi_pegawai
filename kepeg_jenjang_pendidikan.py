import pymysql
from config import DEFAULT_KEPEGAWAIAN_DB_CONFIG


def fetch_janjang_pendidikan_id(jenjang: str):
    koneksi = pymysql.connect(**DEFAULT_KEPEGAWAIAN_DB_CONFIG)
    query = """
            SELECT id FROM jenjang_pendidikan WHERE nama = %s
            """
    with koneksi.cursor() as cur:
        cur.execute(query, (jenjang,))
        return cur.fetchone()["id"] if cur.rowcount > 0 else None
