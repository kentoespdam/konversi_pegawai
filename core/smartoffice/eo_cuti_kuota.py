from core.config import fetch_smartoffice


def fetch_cuti_kuota():
    query = """
            SELECT ck.ck_id      AS id,
                   em.emp_id     AS pegawai_id,
                   ck.ck_pyear   AS tahun,
                   ck.ck_kuota   AS kuota,
                   ck.ck_diambil AS kuota_terpakai,
                   ck.ck_sisa    AS sisa_kuota,
                   ck.ck_expired AS expired
            FROM cuti_kuota AS ck
                     LEFT JOIN employee AS em ON ck.emp_code = em.emp_code \
            """

    return fetch_smartoffice(query)