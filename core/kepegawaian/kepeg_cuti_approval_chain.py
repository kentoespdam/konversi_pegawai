import pandas as pd
import numpy as np

from core.config import save_update_kepegawaian


def save_approval_chain(df: pd.DataFrame):
    """
    Simpan atau update data chain approval cuti ke database Kepegawaian.
    """
    if df.empty:
        return

    data_list = [
        (
            row.id,
            row.ref_cuti_id,
            row.jabatan_id,
            row.jabatan_nama,
            row.approval_level,
            0,  # approval_status default 0
            row.read_write_status
        )
        for row in df.itertuples(index=False)
    ]

    query = """
            INSERT INTO cuti_approval_chain (
                id, ref_cuti_id, jabatan_id, jabatan_nama, approval_level,
                approval_status, read_write_status
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE
                ref_cuti_id       = VALUES(ref_cuti_id),
                jabatan_id        = VALUES(jabatan_id),
                jabatan_nama      = VALUES(jabatan_nama),
                approval_level    = VALUES(approval_level),
                approval_status   = VALUES(approval_status),
                read_write_status = VALUES(read_write_status)
            """
    save_update_kepegawaian(query, data_list)


def update_approval_chain(df: pd.DataFrame):
    if df.empty:
        return

    # Sanitasi NaN menjadi None
    df = df.replace({np.nan: None, pd.NA: None})

    data_list = [(
        max(0, row.approval_status),
        row.cuti_pegawai_id,
        row.jabatan_id,
        row.approval_level
    ) for row in df.itertuples(index=False)]

    query = """
            UPDATE cuti_approval_chain
            SET approval_status=%s
            WHERE ref_cuti_id = %s
              AND jabatan_id = %s
              AND approval_level = %s
            """
    save_update_kepegawaian(query, data_list)
