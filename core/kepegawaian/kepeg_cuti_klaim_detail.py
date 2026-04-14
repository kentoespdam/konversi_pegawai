import pandas as pd
import numpy as np

from core.config import save_update_kepegawaian, LOGGER


def save_cuti_klaim_detail(df: pd.DataFrame):
    if df.empty:
        return

    # Sanitize NaN/NaT to None for SQL
    df = df.replace({np.nan: None, pd.NA: None})

    data_list = [(
        row.id,
        row.tanggal,
        row.ref_cuti_id
    ) for row in df.itertuples(index=False)]

    query = """
            INSERT INTO cuti_klaim_detail (id, tanggal, ref_cuti_id)
            VALUES (%s, %s, %s)
            ON DUPLICATE KEY UPDATE
                tanggal = VALUES(tanggal),
                ref_cuti_id = VALUES(ref_cuti_id)
            """

    try:
        save_update_kepegawaian(query, data_list)
    except Exception as e:
        LOGGER.error(f"Error saving cuti_klaim_detail: {e}")
        raise
