import pandas as pd

from core.config import save_update_kepegawaian


def save_cuti_approval(df: pd.DataFrame):
    data_list = [(
        row.id,
        row.cuti_pegawai_id,
        row.approver_id,
        row.jabatan_id,
        row.approval_level,
        row.approval_status,
        row.notes,
        'SYSTEM',
        False,
        0,
        row.created_at
    ) for row in df.itertuples(index=False)]
    query = """
            INSERT INTO cuti_approval(id, cuti_pegawai_id, approver_id, jabatan_id, approval_level,
                                      approval_status, notes, created_by, is_deleted, version,
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
                                    created_at      = VALUES(created_at)
            """

    save_update_kepegawaian(query, data_list)
