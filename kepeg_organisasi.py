import pymysql
from config import DEFAULT_KEPEGAWAIAN_DB_CONFIG


def fetch_organisasi_id(nama_organisasi: str) -> int:
    koneksi = pymysql.connect(**DEFAULT_KEPEGAWAIAN_DB_CONFIG)
    query = """
            SELECT id FROM organisasi WHERE nama = %s
            """
    with koneksi.cursor() as cur:
        cur.execute(query, (nama_organisasi,))
        result = cur.fetchone()
        return result["id"] if cur.rowcount > 0 else None
