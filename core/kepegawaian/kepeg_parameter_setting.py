import pandas as pd

from core.config import LOGGER, get_kepegawaian_connection_pool


def save_parameter_setting(df: pd.DataFrame):
    if df.empty:
        return

    data_list = [(
        row.kode,
        row.nominal,
        "SYSTEM"
    ) for row in df.itertuples(index=False)]
    query = """
            INSERT INTO gaji_parameter_setting (kode, nominal, created_by)
            VALUES (%s, %s, %s)
            ON DUPLICATE KEY UPDATE nominal=VALUES(nominal),
                                    updated_at=CURRENT_TIMESTAMP
            """
    with get_kepegawaian_connection_pool() as conn:
        with conn.cursor() as cursor:
            try:
                cursor.executemany(query, data_list)
                LOGGER.info(f"gaji_parameter_setting: {cursor.rowcount} rows affected")
                conn.commit()
            except Exception as e:
                LOGGER.error(f"Error saving parameter_setting: {e}")
                conn.rollback()
