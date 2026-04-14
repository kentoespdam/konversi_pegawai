import pandas as pd
import numpy as np

from core.config import save_update_kepegawaian


def save_cuti_approval(df: pd.DataFrame):
    if df.empty:
        return

    # Sanitasi NaN menjadi None agar database tidak error (float NaN)
    df = df.replace({np.nan: None, pd.NA: None})

    data_list = [(
        row.id,
        row.cuti_pegawai_id,
        row.approver_id,
        row.jabatan_id,
        row.approval_level,
        max(0, row.approval_status),  # Pastikan status tidak negatif (-1 jadi 0)
        row.notes,
        'SYSTEM',
        'SYSTEM',
        False,
        row.created_at
    ) for row in df.itertuples(index=False)]
    query = """
            INSERT INTO cuti_approval(id, cuti_pegawai_id, approver_id, jabatan_id, approval_level,
                                      approval_status, notes, created_by, updated_by, is_deleted,
                                      created_at)
            VALUES (%s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s,
                    %s)
            ON DUPLICATE KEY UPDATE cuti_pegawai_id = VALUES(cuti_pegawai_id),
                                    approver_id     = VALUES(approver_id),
                                    jabatan_id      = VALUES(jabatan_id),
                                    approval_level  = VALUES(approval_level),
                                    approval_status = VALUES(approval_status),
                                    notes           = VALUES(notes),
                                    updated_by      = VALUES(updated_by),
                                    created_at      = VALUES(created_at)
            """

    save_update_kepegawaian(query, data_list)
