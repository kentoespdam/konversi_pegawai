from unittest import result
import pymysql
from config import DEFAULT_KEPEGAWAIAN_DB_CONFIG


def fetch_jenjang_pendidikan_id(jenjang_pendidikan: str) -> int:
    """
    Fetch the ID of a jenjang pendidikan from the database.

    Args:
        jenjang_pendidikan (str): The name of the jenjang pendidikan.

    Returns:
        int: The ID of the jenjang pendidikan.
    """

    if jenjang_pendidikan is None:
        return 0

    with pymysql.connect(**DEFAULT_KEPEGAWAIAN_DB_CONFIG) as connection:
        with connection.cursor() as cursor:
            query = """
                SELECT id FROM jenjang_pendidikan
                WHERE nama = %s
            """
            cursor.execute(query, (jenjang_pendidikan,))
            result = cursor.fetchone()

        return result["id"] if result else 0