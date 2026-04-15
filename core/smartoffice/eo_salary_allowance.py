from core.config import get_smartoffice_connection_pool, LOGGER
import pandas as pd
import numpy as np

# Constants
SALARY_ALLOWANCE_QUERY = """
    SELECT
        sa.id, 
        sa.`code`                       AS jenis_tunjangan, 
        CAST(sa.ref_type AS UNSIGNED)   AS level_id, 
        sa.ref_id                       AS golongan_id, 
        sa.`value`                      AS nominal
    FROM
        salary_allowance AS sa
"""

JENIS_TUNJANGAN_CODES = {
    "jabatan": 0,
    "tkk": 1,
    "beras": 2,
    "air": 3,
}
UNKNOWN_JENIS_TUNJANGAN_CODE = -1


def fetch_salary_allowance() -> pd.DataFrame:
    with get_smartoffice_connection_pool() as conn:
        with conn.cursor() as cursor:
            cursor.execute(SALARY_ALLOWANCE_QUERY)
            rows = cursor.fetchall()
            columns = [col[0] for col in cursor.description] if cursor.description else None
            return pd.DataFrame(rows, columns=columns)


# ... existing code ...

def cleanup_salary_allowance(df: pd.DataFrame) -> pd.DataFrame:
    """
    Cleanup and transform salary allowance data.
    """
    if df.empty:
        LOGGER.info("No salary allowance data to cleanup.")
        return df

    try:
        count_before = len(df)
        df = _transform_salary_allowance(df)

        # Sanitization
        df = df.replace({np.nan: None, pd.NaT: None, pd.NA: None})

        count_after = len(df)
        LOGGER.info(f"Successfully cleaned up {count_after} salary allowances (from {count_before} records).")
        return df
    except Exception as e:
        LOGGER.error(f"Error during salary allowance cleanup: {str(e)}")
        raise


# ... existing code ...

def _transform_salary_allowance(df: pd.DataFrame) -> pd.DataFrame:
    """
    Transform partition:
    - Map jenis_tunjangan string codes to enum ints.
    - Compute level_id based on original level_id and golongan_id.
    - Normalize golongan_id based on computed level_id.
    """
    df = df.copy()

    # Map jenis_tunjangan in a vectorized way
    df["jenis_tunjangan"] = (
        df["jenis_tunjangan"]
        .astype(str)
        .str.lower()
        .map(JENIS_TUNJANGAN_CODES)
        .fillna(UNKNOWN_JENIS_TUNJANGAN_CODE)
        .astype(int)
    )

    # Ensure integer types for calculations
    level = df["level_id"].astype(int)
    golongan = df["golongan_id"].astype(int)

    # Vectorized computation for level_id
    level_is_1 = level == 1
    new_level = np.where(level_is_1 & (golongan == 4), 5, np.where(level_is_1 & (golongan == 5), 6, 7))
    df["level_id"] = new_level.astype(int)

    # golongan_id becomes -1 when level_id in {5,6}, otherwise keep original
    df["golongan_id"] = np.where(np.isin(df["level_id"], [5, 6]), -1, golongan).astype(int)

    return df
