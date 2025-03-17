from config import get_smartoffice_connection_pool
from core.enums import EmpWorkStatus


def fetch_data_for_pendidikan():
    query = """
        SELECT
            ep.emp_identity_number AS biodataId,
            ref_edu.text AS jenjangPendidikan,
            ref_gelar.nama_gelar AS gelarBelakang,
            ed.edu_major AS jurusan,
            ed.edu_institution AS institusi,
            ed.edu_sdate AS tahunMasuk,
            ed.edu_edate AS tahunLulus,
            ed.edu_gpa AS gpa,
            ed.edu_last_edu_flag AS isLatest 
        FROM
            emp_education AS ed
            INNER JOIN emp_profile AS ep ON ed.emp_profile_id = ep.emp_profile_id
            INNER JOIN employee AS em ON ep.emp_profile_id = em.emp_profile_id
            INNER JOIN sys_reference AS ref_edu ON ed.edu_level = ref_edu.`value` 
            AND ref_edu.`code` = 'pendidikan'
            INNER JOIN gelar_akademik AS ref_gelar ON ed.edu_gelar = ref_gelar.id 
        WHERE
            em.emp_work_status = %s 
        """
    params = (EmpWorkStatus.KaryawanAktif.value,)
    with get_smartoffice_connection_pool() as conn:
        with conn.cursor() as cursor:
            cursor.execute(query, params)
            return cursor.fetchall()
