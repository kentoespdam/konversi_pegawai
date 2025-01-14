import pymysql
from config import DEFAULT_KEPEGAWAIAN_DB_CONFIG


def fetch_jabatan_id(nama_jabatan: str) -> int:
    koneksi = pymysql.connect(**DEFAULT_KEPEGAWAIAN_DB_CONFIG)
    query = """
            SELECT id FROM jabatan WHERE nama = %s
            """
    with koneksi.cursor() as cur:
        cur.execute(query, (nama_jabatan,))
        return cur.fetchone()["id"] if cur.rowcount > 0 else None
