import pandas as pd

from core.config import get_smartoffice_connection_pool


def fetch_cuti_approval():
    query = """
            SELECT cpa.cpa_id                    AS id,
                   cpa.cp_id                     AS cuti_pegawai_id,
                   em.emp_id                     AS approver_id,
                   em.emp_pos_id                 AS jabatan_id,
                   cpa.cpa_approval_level        AS approval_level,
                   (cpa.cpa_approval_status - 1) AS approval_status,
                   cpa.cpa_note                  AS notes,
                   cpa.cpa_date                  AS created_at
            FROM cuti_pegawai_approval AS cpa
                     INNER JOIN employee AS em ON cpa.cpa_emp_code = em.emp_code
                     INNER JOIN cuti_pegawai AS cp ON cpa.cp_id = cp.cp_id
            """
    with get_smartoffice_connection_pool() as conn:
        with conn.cursor() as cursor:
            cursor.execute(query)
            return pd.DataFrame(cursor.fetchall())
