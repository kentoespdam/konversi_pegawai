import pandas as pd
from icecream import ic

from core.config import get_kepegawaian_connection_pool


def save_parameter_setting(df: pd.DataFrame):
    data_list = [(
        row.kode,
        row.nominal,
        "DEV",
        0
    ) for row in df.itertuples(index=False)]
    query = """
        INSERT INTO gaji_parameter_setting (kode, nominal, created_by, version) 
        VALUES (%s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE nominal=VALUES(nominal)
    """
    with get_kepegawaian_connection_pool() as conn:
        with conn.cursor() as cursor:
            try:
                cursor.executemany(query, data_list)
                ic(f"{cursor.rowcount} rows affected")
                conn.commit()
            except Exception as e:
                ic(e)
                conn.rollback()
