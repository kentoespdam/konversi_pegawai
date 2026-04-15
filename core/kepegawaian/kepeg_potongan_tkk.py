from typing import Final

import pandas as pd

from core.config import LOGGER, get_kepegawaian_connection_pool
from core.enums import EStatusPegawai

DEFAULT_UNKNOWN_INT: Final[int] = -1


def save_potongan_tkk(data: pd.DataFrame):
    if data.empty:
        return

    data_list = [(
        row.id,
        row.status_pegawai,
        row.golongan_id if row.golongan_id > 0 else None,
        row.level_id if row.level_id > 0 else None,
        row.nominal,
        "SYSTEM"
    ) for row in data.itertuples(index=False)]

    query = """
            INSERT INTO gaji_potongan_tkk(id, status_pegawai, golongan_id, level_id, nominal, created_by)
            VALUES (%s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE status_pegawai=VALUES(status_pegawai),
                                    golongan_id=VALUES(golongan_id),
                                    level_id=VALUES(level_id),
                                    nominal=VALUES(nominal),
                                    updated_at=CURRENT_TIMESTAMP
            """

    with get_kepegawaian_connection_pool() as conn:
        with conn.cursor() as cursor:
            try:
                cursor.executemany(query, data_list)
                LOGGER.info(f"gaji_potongan_tkk: {cursor.rowcount} rows affected")
                conn.commit()
            except Exception as e:
                LOGGER.error(f"Error saving potongan_tkk: {e}")
                conn.rollback()


def cleanup_potongan_tkk(df: pd.DataFrame) -> pd.DataFrame:
    """
    Return a cleaned copy of the input DataFrame with normalized columns:
    - status_pegawai normalized to EStatusPegawai values (int)
    - level_id normalized according to mapping
    - golongan_id filled with DEFAULT_UNKNOWN_INT when missing and cast to int
    """
    import numpy as np
    df = df.copy()
    df["status_pegawai"] = df["status_pegawai"].apply(_cleanup_status_pegawai).astype(int)
    df["level_id"] = df["level_id"].fillna(DEFAULT_UNKNOWN_INT).astype(int)
    df["level_id"] = df["level_id"].apply(lambda x: _cleanup_level_id(x)).astype(int)
    df["golongan_id"] = df["golongan_id"].fillna(DEFAULT_UNKNOWN_INT).astype(int)

    # Sanitization
    df = df.replace({np.nan: None, pd.NaT: None, pd.NA: None})
    return df


def _cleanup_status_pegawai(status_pegawai: int) -> int:
    """
    Normalize raw status_pegawai code to EStatusPegawai enum value.
    Returns DEFAULT_UNKNOWN_INT when the input is not recognized.
    """
    status_mapping = {
        1: EStatusPegawai.PEGAWAI.value,  # Pegawai Tetap
        2: EStatusPegawai.KONTRAK.value,  # Pegawai Kontrak
        3: EStatusPegawai.NON_PEGAWAI.value,  # Non Pegawai
        4: EStatusPegawai.CAPEG.value,  # Calon Pegawai
        5: EStatusPegawai.HONORER.value,  # Honorer Tetap
        6: EStatusPegawai.CALON_HONORER.value,  # Calon Honorer Tetap
    }
    return status_mapping.get(int(status_pegawai), DEFAULT_UNKNOWN_INT)


def _cleanup_level_id(level_id: int) -> int:
    """
    Map incoming level_id to normalized level id.
    Returns DEFAULT_UNKNOWN_INT when the input is not recognized.
    """
    level_mapping = {
        2: 2,
        3: 3,
        4: 5,
        5: 6,
    }
    return level_mapping.get(int(level_id), DEFAULT_UNKNOWN_INT)
