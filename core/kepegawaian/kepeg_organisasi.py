import pandas as pd

from core.config import get_kepegawaian_connection_pool, save_update_kepegawaian


def fetch_organisasi():
    query = """
            SELECT id, nama FROM organisasi
            """
    with get_kepegawaian_connection_pool() as conn:
        with conn.cursor() as cursor:
            cursor.execute(query)
            return cursor.fetchall()

    data = [(
        row.org_name,
        row.mail_code,
        row.category,
        row.is_deleted,
        row.org_id
    ) for row in df.itertuples(index=False)]

    query = """
            UPDATE organisasi
            SET nama=%s,
                short_name=%s,
                category=%s,
                is_deleted=%s
            WHERE id = %s \
            """

    save_update_kepegawaian(query, data)
