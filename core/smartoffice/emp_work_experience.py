from config import get_smartoffice_connection_pool
from core.enums import EmpWorkStatus


def fetch_data_for_pengalaman_kerja():
    query = """
        SELECT
            ep.emp_identity_number AS biodataId,
            ewe.ewe_company_name AS namaPerusahaan,
            ewe.ewe_company_type AS typePerusahaan,
            ewe.ewe_job_title AS jabatan,
            ewe.ewe_location AS lokasi,
            ewe.ewe_start AS tanggalMasuk,
            ewe.ewe_end AS tanggalKeluar,
            ewe.ewe_job_description AS notes 
        FROM
            emp_work_experience AS ewe
            INNER JOIN emp_profile AS ep ON ewe.emp_profile_id = ep.emp_profile_id
            INNER JOIN employee AS emp ON ep.emp_profile_id = emp.emp_profile_id 
        WHERE
            emp.emp_work_status = %s
        """
    params = (EmpWorkStatus.KaryawanAktif.value,)
    with get_smartoffice_connection_pool() as conn:
        with conn.cursor() as cursor:
            cursor.execute(query, params)
            return cursor.fetchall()
