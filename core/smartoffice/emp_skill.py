from config import get_smartoffice_connection_pool
from core.enums import EmpWorkStatus


def fetch_data_for_keahlian(id: int = None):
    query = """
        SELECT
            ep.emp_identity_number AS biodataId,
            es.jenis_id AS keahlianId,
            UPPER(ref_kualifikasi.text) AS kualifikasi,
            es.sertifikat AS sertifikasi,
            es.institusi,
            es.tahun 
        FROM
            emp_skill AS es
            INNER JOIN emp_profile AS ep ON es.emp_profile_id = ep.emp_profile_id
            INNER JOIN employee AS em ON ep.emp_profile_id = em.emp_profile_id
            INNER JOIN sys_reference AS ref_kualifikasi ON es.kualifikasi_id = ref_kualifikasi.`value` 
            AND ref_kualifikasi.`code` = 'kualifikasi_keahlian'
            INNER JOIN sys_reference AS ref_keahlian ON es.jenis_id = ref_keahlian.`value` 
            AND ref_keahlian.`code` = 'keahlian' 
        WHERE
            em.emp_work_status = %s
        """
    params = (EmpWorkStatus.KaryawanAktif.value)
    if id is not None:
        query += " AND es.id = %s"
        params = (EmpWorkStatus.KaryawanAktif.value, id)
    with get_smartoffice_connection_pool() as conn:
        with conn.cursor() as cursor:
            cursor.execute(query, params)
            return cursor.fetchall()
