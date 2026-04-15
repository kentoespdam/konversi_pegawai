import pandas as pd
from core.config import LOGGER, get_kepegawaian_connection_pool


def save_gaji_tunjangan(df: pd.DataFrame):
    if df.empty:
        return

    insert_list = [
        (
            row.id,
            row.jenis_tunjangan,
            row.level_id,
            row.golongan_id if row.golongan_id > 0 else None,
            row.nominal,
            "SYSTEM"
        )
        for row in df.itertuples(index=False)
    ]
    sql = """
          INSERT INTO gaji_tunjangan
          (id, jenis_tunjangan, level_id, golongan_id, nominal, created_by)
          VALUES (%s, %s, %s, %s, %s, %s)
          ON DUPLICATE KEY UPDATE jenis_tunjangan=VALUES(jenis_tunjangan),
                                  level_id=VALUES(level_id),
                                  golongan_id=VALUES(golongan_id),
                                  nominal=VALUES(nominal),
                                  updated_at=CURRENT_TIMESTAMP
          """

    with get_kepegawaian_connection_pool() as conn:
        with conn.cursor() as cursor:
            cursor.executemany(sql, insert_list)
            LOGGER.info(f"gaji_tunjangan: {cursor.rowcount} rows affected")
            conn.commit()
