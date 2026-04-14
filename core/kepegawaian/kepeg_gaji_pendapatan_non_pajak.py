import pandas as pd

from core.config import get_kepegawaian_connection_pool, LOGGER, fetch_kepegawaian


def fetch_all_gaji_pendapatan_non_pajak():
    query = """
            SELECT id,
                   kode,
                   nominal,
                   notes
            FROM gaji_pendapatan_non_pajak
            WHERE is_deleted = %s
            """
    where = (False,)
    return fetch_kepegawaian(query, where)


def save_gaji_pendapatan_non_pajak(df: pd.DataFrame):
    if df.empty:
        return

    data_list = [(
        row.id,
        row.kode,
        row.nominal,
        row.notes if hasattr(row, 'notes') and row.notes else '',
        row.is_deleted,
        'SYSTEM'
    ) for row in df.itertuples(index=False)]

    query = """
            INSERT INTO gaji_pendapatan_non_pajak (id, kode, nominal, notes, is_deleted, created_by)
            VALUES (%s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE kode=VALUES(kode),
                                     nominal=VALUES(nominal),
                                     notes=VALUES(notes),
                                     is_deleted=VALUES(is_deleted),
                                     updated_at=CURRENT_TIMESTAMP
            """
    with get_kepegawaian_connection_pool() as conn:
        with conn.cursor() as cursor:
            try:
                cursor.executemany(query, data_list)
                LOGGER.info(f"gaji_pendapatan_non_pajak: {cursor.rowcount} rows affected")
                conn.commit()
            except Exception as e:
                LOGGER.error(f"Error saving gaji_pendapatan_non_pajak: {e}")
                conn.rollback()
