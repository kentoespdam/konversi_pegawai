import pymysql
from config import DEFAULT_KEPEGAWAIAN_DB_CONFIG


def fetch_profesi_id(jabatan_id: int) -> int:
    koneksi = pymysql.connect(**DEFAULT_KEPEGAWAIAN_DB_CONFIG)
    query = """
            SELECT id FROM profesi WHERE jabatan_id = %s
            """
    params = (jabatan_id,)
    with koneksi.cursor() as cur:
        cur.execute(query, params)
        return cur.fetchone()["id"] if cur.rowcount > 0 else None

def fetch_grade_profesi_id(profesi_id: int) -> int:
    koneksi = pymysql.connect(**DEFAULT_KEPEGAWAIAN_DB_CONFIG)
    query = """
            SELECT grade_id FROM profesi WHERE id = %s
            """
    params = (profesi_id,)
    with koneksi.cursor() as cur:
        cur.execute(query, params)
        return cur.fetchone()["grade_id"] if cur.rowcount > 0 else None