from config import get_kepegawaian_connection_pool


def fetch_all_jenis_kartu():
    query = """
        SELECT
            jenis_kitas.id, 
            jenis_kitas.nama
        FROM
            jenis_kitas
        """
    with get_kepegawaian_connection_pool() as conn:
        with conn.cursor() as cursor:
            cursor.execute(query)
            return cursor.fetchall()
