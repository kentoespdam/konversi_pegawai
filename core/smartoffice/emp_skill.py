from core.config import get_smartoffice_connection_pool
from core.enums import EmpWorkStatus


def fetch_emp_skill_for_keahlian():
    query = """
        SELECT
            ep.emp_identity_number AS biodata_id,
            es.jenis_id AS jenis_keahlian_id,
            IF( es.kualifikasi_id = 3, 0, es.kualifikasi_id ) AS kualifikasi,
            es.sertifikat,
            es.institusi,
            es.tahun,
            es.entry_date AS tanggal_pengajuan,
            es.approve_date AS tanggal_disetujui,
        IF
            ( es.`status` = 3, TRUE, FALSE ) AS is_deleted 
        FROM
            emp_skill AS es
            INNER JOIN emp_profile AS ep ON es.emp_profile_id = ep.emp_profile_id
    """
    with get_smartoffice_connection_pool() as conn:
        with conn.cursor() as cursor:
            cursor.execute(query)
            return cursor.fetchall()


def fetch_data_for_keahlian(_id: int = None):
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
    params = EmpWorkStatus.KaryawanAktif.value
    if _id is not None:
        query += " AND es.id = %s"
        params = (EmpWorkStatus.KaryawanAktif.value, _id)
    with get_smartoffice_connection_pool() as conn:
        with conn.cursor() as cursor:
            cursor.execute(query, params)
            return cursor.fetchall()
