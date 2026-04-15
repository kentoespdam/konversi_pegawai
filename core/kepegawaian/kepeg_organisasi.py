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


def update_organisasi_from_organization(df: pd.DataFrame):
    if df.empty:
        return

    data = [(
        row.org_id,
        row.org_name,
        row.mail_code,
        row.category,
        row.is_deleted
    ) for row in df.itertuples(index=False)]

    query = """
            INSERT INTO organisasi (id, nama, short_name, category, is_deleted)
            VALUES (%s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE
                nama=VALUES(nama),
                short_name=VALUES(short_name),
                category=VALUES(category),
                is_deleted=VALUES(is_deleted)
            """

    save_update_kepegawaian(query, data)
