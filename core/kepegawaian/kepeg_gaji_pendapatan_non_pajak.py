from config import get_kepegawaian_connection_pool


def fetch_all_gaji_pendapatan_non_pajak():
    query="""
        SELECT
            id,
            kode,
            nominal,
            notes
        FROM
            gaji_pendapatan_non_pajak
        WHERE
            is_deleted = FALSE
    """
    with get_kepegawaian_connection_pool() as conn:
        with conn.cursor() as cursor:
            cursor.execute(query)
            return cursor.fetchall()