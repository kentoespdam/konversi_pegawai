import pymysql
from config import DEFAULT_KEPEGAWAIAN_DB_CONFIG
from icecream import ic


def fetch_golongan_id(golongan_name: str) -> int:
    """
    Fetch golongan ID from the database.

    Args:
        golongan_name (str): The name of the golongan.
        pangkat_name (str): The name of the pangkat.

    Returns:
        int: The ID of the golongan.
    """
    if not golongan_name:
        return 0

    connection = pymysql.connect(**DEFAULT_KEPEGAWAIAN_DB_CONFIG)

    with connection.cursor() as cursor:
        query = "SELECT id FROM golongan WHERE golongan = %s"
        cursor.execute(query, (golongan_name))
        result = cursor.fetchone()

    return result["id"] if result else 0
