import pandas as pd
from icecream import ic

from core.config import get_kepegawaian_connection_pool


def save_cuti_klaim_detail(df: pd.DataFrame):
    data_list = [(
        row.id,
        row.tanggal,
        row.ref_cuti_id
    ) for row in df.itertuples(index=False)]

    query = """
        INSERT INTO cuti_klaim_detail (id, tanggal, ref_cuti_id)
        VALUES (%s, %s, %s)
    """

    with get_kepegawaian_connection_pool() as connection:
        with connection.cursor() as cursor:
            try:
                cursor.executemany(query, data_list)
                ic(cursor.rowcount, "row(s) affected")
                connection.commit()
            except Exception as e:
                ic(e)
                connection.rollback()
