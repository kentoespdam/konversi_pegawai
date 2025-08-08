import pandas as pd

from config import LOGGER, get_kepegawaian_connection_pool


def save_gaji_tunjangan(df: pd.DataFrame):
    insert_list = [
        (
            row.id,
            row.jenis_tunjangan,
            row.level_id,
            row.golongan_id if row.golongan_id > 0 else None,
            row.nominal,
            "DEV",
            0,
        )
        for row in df.itertuples(index=False)
    ]
    sql = """
        INSERT INTO gaji_tunjangan 
            (id, jenis_tunjangan, level_id, golongan_id, nominal, created_at, version) 
        VALUES 
            (%s, %s, %s, %s, %s, %s, %s) 
        ON DUPLICATE KEY UPDATE 
            jenis_tunjangan=VALUES(jenis_tunjangan), level_id=VALUES(level_id), golongan_id=VALUES(golongan_id), nominal=VALUES(nominal)
        """

    with get_kepegawaian_connection_pool() as conn:
        with conn.cursor() as cursor:
            cursor.executemany(sql, insert_list)
            LOGGER.debug(f"{cursor.rowcount} rows affected")
            conn.commit()
