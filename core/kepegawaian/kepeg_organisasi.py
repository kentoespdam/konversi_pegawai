import pymysql
from config import DEFAULT_KEPEGAWAIAN_DB_CONFIG, get_kepegawaian_connection_pool
from icecream import ic


def fetch_organisasi():
    query = """
        SELECT
            org.id, 
            org.kode, 
            org.parent_id, 
            org.level_org, 
            org.nama, 
            org.short_name
        FROM
            organisasi AS org
        """
    with get_kepegawaian_connection_pool() as conn:
        with conn.cursor() as cursor:
            cursor.execute(query)
            return cursor.fetchall()


def fetch_organisasi_id(organisasi_name: str) -> int:
    """
    Fetch the ID of an organisasi from the database.

    Args:
        organisasi_name (str): The name of the organisasi.

    Returns:
        int: The ID of the organisasi.
    """

    if organisasi_name is None:
        return 0

    if organisasi_name == "BAG. PERENCANAAN & PENGEMBANGAN":
        return 31

    connection = pymysql.connect(**DEFAULT_KEPEGAWAIAN_DB_CONFIG)
    with connection.cursor() as cursor:
        query = "SELECT id FROM organisasi WHERE nama = %(organisasi_name)s"
        params = {"organisasi_name": organisasi_name}
        cursor.execute(query, params)
        result = cursor.fetchone()
        if result is None:
            ic(cursor.mogrify(query, params))

    return result["id"] if result else 0
