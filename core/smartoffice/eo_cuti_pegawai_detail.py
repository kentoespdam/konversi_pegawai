from core.config import fetch_smartoffice


def fetch_cuti_pegawai_detail():
    query = """
            SELECT cpd.cpd_id     AS id,
                   cpd.cp_id      AS ref_cuti_id,
                   cpd.cpd_date_1 AS tanggal
            FROM cuti_pegawai_detail AS cpd
                     INNER JOIN
                 cuti_pegawai AS cp
                 ON
                     cpd.cp_id = cp.cp_id \
            """
    return fetch_smartoffice(query)
