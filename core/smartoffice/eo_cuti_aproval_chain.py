from core.config import fetch_smartoffice


def fetch_cuti_approval_chain():
    """
    Fetch data chain approval cuti dari SmartOffice database.
    """
    query = """
            SELECT cac.cpc_id                        AS id,
                   cac.cp_id                         AS ref_cuti_id,
                   cac.cpc_pos_id                    AS jabatan_id,
                   cac.cpc_pos_name                  AS jabatan_nama,
                   cac.cpc_approval_level            AS approval_level,
                   IFNULL(task.read_write_status, 1) AS read_write_status
            FROM cuti_pegawai_approval_chain AS cac
                     INNER JOIN cuti_pegawai AS cp ON cac.cp_id = cp.cp_id
                     INNER JOIN employee AS em ON cp.emp_code = em.emp_code
                     LEFT JOIN (SELECT cat.cpt_id,
                                       cat.cp_id,
                                       em.emp_pos_id,
                                       IF(cat.cpt_status = 0, 2, 1) AS read_write_status
                                FROM cuti_pegawai_approval_task AS cat
                                         INNER JOIN employee AS em ON cat.cpt_emp_code = em.emp_code) AS task
                                ON cac.cp_id = task.cp_id AND cac.cpc_pos_id = task.emp_pos_id
                     LEFT JOIN cuti_pegawai_approval AS cpa ON cac.cp_id = cpa.cp_id AND cac.cpc_pos_id = cpa.cpa_pos_id
            """

    return fetch_smartoffice(query)
