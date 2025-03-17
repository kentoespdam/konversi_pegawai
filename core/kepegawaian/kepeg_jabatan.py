import pymysql
from config import DEFAULT_KEPEGAWAIAN_DB_CONFIG, get_kepegawaian_connection_pool


def fetch_jabatan():
    query = """
        SELECT
            jab.id, 
            jab.kode, 
            jab.parent_id, 
            jab.level_id, 
            jab.nama, 
            jab.organisasi_id
        FROM
            jabatan AS jab
        """
    with get_kepegawaian_connection_pool() as conn:
        with conn.cursor() as cursor:
            cursor.execute(query)
            return cursor.fetchall()


def fetch_jabatan_id(jabatan_name: str) -> int:
    """
    Fetch jabatan ID from the database.

    Args:
        jabatan_name (str): The name of the jabatan.

    Returns:
        int: The ID of the jabatan.
    """
    if jabatan_name is None:
        return 0

    connection = pymysql.connect(**DEFAULT_KEPEGAWAIAN_DB_CONFIG)
    query = """
            SELECT id FROM jabatan WHERE nama = %s
            """
    with connection.cursor() as cursor:
        cursor.execute(query, (jabatan_name,))
        result = cursor.fetchone()

    return result["id"] if result else 0
