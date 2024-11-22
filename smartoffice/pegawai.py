import pandas as pd
from pandas import DataFrame
from core.kamus import replace_status_kerja, replace_status_pegawai
from core.koneksi import engine
import swifter  # noqa: F401

from kepegawaian.master import find_golongan_id, find_jabatan_id, find_organisasi_id

sql_edu = """
    SELECT
		eed.emp_profile_id,
		eed.edu_level,
		eed.edu_edate 
	FROM
		emp_education AS eed 
	WHERE
	( emp_profile_id, edu_edate ) IN ( SELECT emp_profile_id, MAX( edu_edate ) FROM emp_education GROUP BY emp_profile_id )
"""
sql_sk = """
    SELECT
		emp_id,
		tgl_sk,
		no_sk 
	FROM
		emp_sk 
	WHERE
		jenis_sk = 3 
		AND ( emp_id, tgl_sk ) IN ( 
            SELECT emp_id, MAX( tgl_sk ) 
            FROM emp_sk
            WHERE jenis_sk = 3 
            GROUP BY emp_id 
        )
"""
sql = f"""
    SELECT
        ep.emp_identity_number AS nik,
        ep.emp_name AS nama,
        ep.emp_gender AS jenisKelamin,
        ep.emp_birth_place AS tempatLahir,
        ep.emp_birth_date AS tanggalLahir,
        ep.emp_address AS alamat,
        ep.emp_mobile AS telp,
        ep.emp_religion AS agama,
        ep.emp_mother_name AS ibuKandung,
        edu.edu_level AS pendidikanTerakhirId,
        ep.emp_blood_type AS golonganDarah,
        ep.id_marital_status AS statusKawin,
        '' AS notes,
        TRUE AS isPegawai,
        e.emp_code AS nipam,
        e.emp_flag AS statusPegawai,
        e.emp_work_status AS statusKerja,
        p.pos_name AS jabatanId,
        o.org_name AS organisasiId,
        45 AS profesiId,
        CONCAT( g.golongan,'-' ,g.pangkat ) AS golonganId,
        8 AS gradeId,
        sk.no_sk AS nomorSk,
        sk.tgl_sk AS tanggalSk,
        e.emp_gp AS gajiPokok 
    FROM
        emp_profile AS ep
        INNER JOIN employee AS e ON ep.emp_profile_id = e.emp_profile_id
        JOIN ({sql_edu}) AS edu ON ep.emp_profile_id = edu.emp_profile_id
        JOIN position p ON e.emp_pos_id = p.pos_id
        JOIN organization o ON p.pos_org_id = o.org_id
        LEFT JOIN golongan g ON e.emp_gol_id = g.id
        LEFT JOIN ({sql_sk}) AS sk ON e.emp_id = sk.emp_id 
    WHERE
        ep.emp_identity_number <> "" 
        AND e.emp_work_status = %s
    ORDER BY
        e.emp_profile_id
    
"""

# def manipulate_jenis_kelamin()


def manipulate_pegawai(frame: DataFrame) -> DataFrame:
    frame["jenisKelamin"].swifter.apply(
        lambda x: "LAKI_LAKI" if x == "Pria" else "PEREMPUAN"
    )

    return frame


def ambil_pegawai_dari_smartoffice():
    try:
        result = pd.read_sql_query(sql, engine.connect(), params=(6,))
        result["jenisKelamin"] = result["jenisKelamin"].swifter.apply(
            lambda x: "LAKI_LAKI" if x == "Pria" else "PEREMPUAN"
        )
        result["statusPegawai"] = result["statusPegawai"].swifter.apply(
            lambda x: replace_status_pegawai(x)
        )
        result["statusKerja"] = result["statusKerja"].swifter.apply(
            lambda x: replace_status_kerja(x)
        )
        result["ibuKandung"] = result["ibuKandung"].swifter.apply(
            lambda x: x if x else "Ibu"
        )
        result["golonganId"] = result["golonganId"].swifter.apply(
            lambda x: find_golongan_id(x) if x else 0
        )
        result["jabatanId"] = result["jabatanId"].swifter.apply(
            lambda x: find_jabatan_id(x) if x else 0
        )
        result["organisasiId"] = result["organisasiId"].swifter.apply(
            lambda x: find_organisasi_id(x)
        )
        return result
    except Exception as e:
        print(f"Error: {e}")
