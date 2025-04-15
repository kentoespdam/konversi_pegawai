from config import get_smartoffice_connection_pool
from core.enums import EmpWorkStatus

def fetch_emp_family_for_profil_keluarga():
    query = """
        SELECT
            ef.fam_id,
            ep.emp_identity_number AS biodata_id,
            ef.fam_name AS nama,
            IF( ef.fam_gender = 'Pria', 0, 1 ) AS jenis_kelamin,
            rh.`value` - 1 AS hubungan_keluarga,
            ef.fam_birth_place AS tempat_lahir,
            ef.fam_birth_date AS tanggal_lahir,
            ef.fam_tanggungan AS tanggungan,
            ef.fam_pendidikan-1 AS status_pendidikan,
            ef.fam_sts_nikah AS status_kawin,
            ef.fam_description AS notes,
            IF( ef.fam_status = 3, TRUE, FALSE ) AS is_deleted 
        FROM
            emp_family AS ef
            INNER JOIN emp_profile AS ep ON ef.emp_profile_id = ep.emp_profile_id
            LEFT JOIN sys_reference AS rh ON ef.fam_relation = rh.`value` 
            AND rh.`code` = 'hub_keluarga'
    """
    with get_smartoffice_connection_pool() as conn:
        with conn.cursor() as cursor:
            cursor.execute(query)
            return cursor.fetchall()

def fetch_data_for_profil_keluarga(emp_profil_id: int = None):
    query = """
        SELECT
            ep.emp_identity_number AS biodataId, 
            '' AS nik,
            ef.fam_name AS nama, 
            IF(ef.fam_gender='Pria', 'LAKI_LAKI', 'PEREMPUAN') AS jenisKelamin,
            'TIDAK_TAHU' AS agama, 
            CASE 
                WHEN ef.fam_relation = 1 THEN 'SUAMI'
                WHEN ef.fam_relation = 2 THEN 'ISTRI'
                WHEN ef.fam_relation = 3 THEN 'AYAH'		
                WHEN ef.fam_relation = 4 THEN 'IBU'		
                WHEN ef.fam_relation = 5 THEN 'ANAK'		
                WHEN ef.fam_relation = 7 THEN 'SAUDARA'		
            END AS hubunganKeluarga, 
            ef.fam_birth_place AS tempatLahir, 
            ef.fam_birth_date AS tanggalLahir, 
            IF(ef.fam_tanggungan=0, FALSE, TRUE) AS tanggungan,
            0 AS pendidikanId, 
            CASE
                WHEN ef.fam_pendidikan=1 THEN 'BELUM_SEKOLAH'
                WHEN ef.fam_pendidikan=2 THEN 'SEKOLAH'
                WHEN ef.fam_pendidikan=3 THEN 'SELESAI_SEKOLAH'
            END AS statusPendidikan,
            ef.fam_sts_nikah, 
            ef.fam_description AS notes
        FROM
            emp_family AS ef
            INNER JOIN emp_profile AS ep
            ON ef.emp_profile_id = ep.emp_profile_id
            INNER JOIN employee AS em
            ON ep.emp_profile_id = em.emp_profile_id
        WHERE
            em.emp_work_status = %s 
            AND ef.fam_status = %s
        """
    params = (EmpWorkStatus.KaryawanAktif.value, 1)
    if emp_profil_id is not None:
        query += " AND ef.emp_profile_id = %s"
        params += (emp_profil_id,)
    with get_smartoffice_connection_pool() as conn:
        with conn.cursor() as cursor:
            cursor.execute(query, params)
            return cursor.fetchall()
