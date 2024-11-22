import pandas as pd
from core.koneksi import koneksi, engine
from icecream import ic

sql_last_edu="""
    SELECT
        emp_profile_id,
        edu_level,
        edu_edate 
    FROM
        emp_education 
    WHERE
    ( emp_profile_id, edu_edate ) IN ( SELECT emp_profile_id, MAX( edu_edate ) FROM emp_education GROUP BY emp_profile_id )
"""

def ambil_biodata_dari_smartoffice():
    try:
        sql = f"""
            SELECT 
                ep.emp_profile_id AS id,
                ep.emp_identity_number AS nik, 
                ep.emp_name AS nama, 
                ep.emp_gender AS jenisKelamin, 
                ep.emp_birth_place AS tempatLahir, 
                ep.emp_birth_date AS tanggalLahir, 
                ep.emp_address AS alamat, 
                ep.emp_mobile AS telp, 
                ep.emp_religion AS agama, 
                ep.emp_mother_name AS ibuKandung, 
                ep.emp_blood_type AS golonganDarah, 
                ep.id_marital_status AS statusKawin,
                edu.edu_level AS pendidikanTerakhirId,
                '' AS notes,
                FALSE AS isPegawai
            FROM emp_profile AS ep
                INNER JOIN employee AS e ON ep.emp_profile_id = e.emp_profile_id
                JOIN ({sql_last_edu}) AS edu ON ep.emp_profile_id = edu.emp_profile_id
            WHERE 
                ep.emp_identity_number <> "" AND
                e.emp_work_status = %s
            LIMIT 1
        """
        result = pd.read_sql_query(sql, engine.connect(), params=(6,))
        # print(result)
        return result
    except Exception as e:
        ic(e)
