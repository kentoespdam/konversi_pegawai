import pymysql
from config import DEFAULT_KEPEGAWAIAN_DB_CONFIG


def fetch_profesi_id_by_jabatan_id(jabatan_id: int) -> int:
    """
    Fetch the ID of a profesi from the database based on the given jabatan ID.

    Args:
        jabatan_id (int): The ID of the jabatan.

    Returns:
        int: The ID of the profesi.
    """
    if jabatan_id == 0:
        return 0

    with pymysql.connect(**DEFAULT_KEPEGAWAIAN_DB_CONFIG) as connection:
        with connection.cursor() as cursor:
            query = """
                    SELECT id FROM profesi WHERE jabatan_id = %s
                    """
            params = (jabatan_id,)
            cursor.execute(query, params)
            result = cursor.fetchone()

    return result["id"] if result else 0


def fetch_grade_profesi_id(profesi_id: int) -> int:
    koneksi = pymysql.connect(**DEFAULT_KEPEGAWAIAN_DB_CONFIG)
    query = """
            SELECT grade_id FROM profesi WHERE id = %s
            """
    params = (profesi_id,)
    with koneksi.cursor() as cur:
        cur.execute(query, params)
        return cur.fetchone()["grade_id"] if cur.rowcount > 0 else None
