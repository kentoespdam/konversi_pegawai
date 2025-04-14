from config import get_smartoffice_connection_pool


def fetch_data_for_biodata():
    query = """
        SELECT
            ep.emp_identity_number AS nik,
            ep.emp_name AS nama,
        IF
            ( ep.emp_gender = "Pria", 0, 1 ) AS jenis_kelamin,
            ep.emp_birth_place AS tempat_lahir,
            ep.emp_birth_date AS tanggal_lahir,
            ep.emp_address AS alamat,
            ep.emp_mobile AS telp,
        IF
            ( ep.emp_religion = 99, 0, ep.emp_religion ) AS agama,
        IF
            ( ep.emp_mother_name = "", "-", ep.emp_mother_name ) AS ibu_kandung,
            IFNULL( ref_edu.text, "SMA - Sederajat" ) AS pendidikanTerakhir,
            ep.emp_blood_type AS golongan_darah,
        IF
            ( ep.id_marital_status = 99, 4, ep.id_marital_status - 1 ) AS status_kawin,
            ep.emp_note AS notes 
        FROM
            emp_profile AS ep
            LEFT JOIN emp_education AS eed ON ep.emp_profile_id = eed.emp_profile_id 
            AND eed.edu_last_edu_flag = 1
            LEFT JOIN sys_reference AS ref_edu ON eed.edu_level = ref_edu.`value` 
            AND ref_edu.`code` = 'pendidikan'
            LEFT JOIN employee em ON ep.emp_profile_id = em.emp_profile_id
        GROUP BY
            ep.emp_profile_id
    """
    with get_smartoffice_connection_pool() as conn:
        with conn.cursor() as cursor:
            cursor.execute(query)
            return cursor.fetchall()
