import pymysql
from config import DEFAULT_KEPEGAWAIAN_DB_CONFIG


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
