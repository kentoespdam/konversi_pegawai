from config import get_smartoffice_connection_pool
import pandas as pd
import dask.dataframe as dd


def fetch_sallary_allowance():
    query = """
            SELECT
                sa.id, 
                sa.`code`                       AS jenis_tunjangan, 
                CAST(sa.ref_type AS UNSIGNED)   AS level_id, 
                sa.ref_id                       AS golongan_id, 
                sa.`value`                      AS nominal
            FROM
                salary_allowance AS sa
            """
    with get_smartoffice_connection_pool() as conn:
        with conn.cursor() as cursor:
            cursor.execute(query)
            return pd.DataFrame(cursor.fetchall())


def cleanup_sallary_allowance(df: pd.DataFrame):
    ddf = dd.from_pandas(df, npartitions=4)
    ddf = ddf.map_partitions(
        _manipulate_df,
        meta={
            "id": int,
            "jenis_tunjangan": str,
            "level_id": int,
            "golongan_id": int,
            "nominal": int,
        },
    )
    df = ddf.compute()
    return df


def _manipulate_df(df: pd.DataFrame):
    df["jenis_tunjangan"] = df["jenis_tunjangan"].apply(_manipulate_jenis_tunjangan)
    df["level_id"] = df.apply(_manipulate_level_id, axis=1)
    df["golongan_id"] = df.apply(_manipulate_golongan_id, axis=1)

    return df


def _manipulate_jenis_tunjangan(jenis_tunjangan_code: str) -> int:
    """
    Manipulate jenis_tunjangan_code to match Kepegawaian's enum.
    """
    jenis_tunjangan_codes = {
        "jabatan": 0,
        "tkk": 1,
        "beras": 2,
        "air": 3,
    }
    return jenis_tunjangan_codes.get(jenis_tunjangan_code.lower(), -1)


def _manipulate_level_id(row: pd.Series) -> int:
    """Manipulate level_id to match Kepegawaian's enum."""
    if row["level_id"] == 1 and row["golongan_id"] == 4:
        return 5
    elif row["level_id"] == 1 and row["golongan_id"] == 5:
        return 6
    else:
        return 7


def _manipulate_golongan_id(row: pd.Series) -> int:
    """Manipulate golongan_id to match Kepegawaian's enum."""
    return row["golongan_id"] if row["level_id"] not in [5, 6] else -1
