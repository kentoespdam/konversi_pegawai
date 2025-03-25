from config import get_smartoffice_connection_pool
from core.enums import EmpWorkStatus


def fetch_data_for_pegawai() -> list:
    """Fetch employee data from the database."""
    query = """
            SELECT
                emp.emp_id,
                emp.emp_profile_id,
                ep.emp_identity_number AS nik,
                ep.emp_name AS nama,
                IF( ep.emp_gender = "Pria", "LAKI_LAKI", "PEREMPUAN" ) AS jenisKelamin,
                ep.emp_birth_place AS tempatLahir,
                ep.emp_birth_date AS tanggalLahir,
                ep.emp_address AS alamat,
                ep.emp_mobile AS telp,
                CASE    
                    WHEN ep.emp_religion = 1 THEN "ISLAM" 
                    WHEN ep.emp_religion = 2 THEN "KRISTEN" 
                    WHEN ep.emp_religion = 3 THEN "KATOLIK" 
                    WHEN ep.emp_religion = 4 THEN "HINDU" 
                    WHEN ep.emp_religion = 5 THEN "BUDHA" 
                    WHEN ep.emp_religion = 6 THEN "KONGHUCU" 
                    WHEN ep.emp_religion = 7 THEN "ALIRAN_KEPERCAYAAN" 
                    WHEN ep.emp_religion = 99 THEN "TIDAK_TAHU" 
                END AS agama,
                IF( ep.emp_mother_name = "", "-", ep.emp_mother_name ) AS ibuKandung,
                ref_edu.text AS pendidikanTerakhir,
                IFNULL( ep.emp_blood_type, "" ) AS golonganDarah,
                CASE    
                    WHEN ep.id_marital_status = 1 THEN "BELUM_KAWIN" 
                    WHEN ep.id_marital_status = 2 THEN "KAWIN" 
                    WHEN ep.id_marital_status = 3 THEN "JANDA_DUDA" 
                    WHEN ep.id_marital_status = 4 THEN "MENIKAH_SEKANTOR" 
                    ELSE "TIDAK_TAHU" 
                END AS statusKawin,
                ep.emp_note AS notes,
                emp.emp_code AS nipam,
                CASE    
                    WHEN emp.emp_flag = 1 THEN "PEGAWAI" 
                    WHEN emp.emp_flag = 2 THEN "KONTRAK" 
                    WHEN emp.emp_flag = 3 THEN "NON_PEGAWAI" 
                    WHEN emp.emp_flag = 4 THEN "CAPEG" 
                    WHEN emp.emp_flag = 5 THEN "HONORER" 
                    WHEN emp.emp_flag = 6 THEN "CALON_HONORER" 
                END AS statusPegawai,
                CASE    
                    WHEN emp.emp_work_status = 1 THEN "LAMARAN_BARU" 
                    WHEN emp.emp_work_status = 2 THEN "TAHAP_SELEKSI" 
                    WHEN emp.emp_work_status = 3 THEN "DITERIMA" 
                    WHEN emp.emp_work_status = 4 THEN "DIREKOMENDASIKAN" 
                    WHEN emp.emp_work_status = 5 THEN "DITOLAK" 
                    WHEN emp.emp_work_status = 6 THEN "KARYAWAN_AKTIF" 
                    WHEN emp.emp_work_status = 7 THEN "DIRUMAHKAN" 
                    WHEN emp.emp_work_status = 8 THEN "BERHENT" 
                END AS statusKerja,
                pos.pos_name AS namaJabatan,
                org.org_name AS namaOrganisasi,
                "" AS profesi,
                gol.golongan AS golongan,
                gol.pangkat AS pangkat,
                IF( emp.emp_flag = 2, empc.contract_no, emp_sk.no_sk ) AS nomorSk,
                IF( emp.emp_flag = 2, skk.tgl_sk, emp_sk.tgl_sk ) AS tanggalSk,
                IF( emp.emp_flag = 2, empc.contract_start_date, emp_sk.tmt_sk ) AS tmtBerlakuSk,
                IF( emp.emp_flag = 2, empc.contract_exp_date, NULL ) AS tmtKontrakSelesai,
                sni.id AS kodePajakId,
                emp.emp_gp AS gajiPokok 
            FROM
                employee AS emp
                INNER JOIN emp_profile AS ep ON emp.emp_profile_id = ep.emp_profile_id
                LEFT JOIN emp_education AS eed ON ep.emp_profile_id = eed.emp_profile_id 
                    AND eed.edu_last_edu_flag = 1
                LEFT JOIN sys_reference AS ref_edu ON eed.edu_level = ref_edu.`value` 
                    AND ref_edu.`code` = 'pendidikan'
                INNER JOIN position AS pos ON emp.emp_pos_id = pos.pos_id
                INNER JOIN organization AS org ON pos.pos_org_id = org.org_id
                LEFT JOIN golongan AS gol ON emp.emp_gol_id = gol.id
                LEFT JOIN emp_sk ON emp.emp_id = emp_sk.emp_id 
                    AND emp.sk_pengangkatan = emp_sk.no_sk
                INNER JOIN salary_non_taxable_income AS sni ON ep.emp_tax_code = sni.`code`
                LEFT JOIN emp_sk skk ON emp.emp_flag = 2 
                    AND emp.emp_id = skk.emp_id 
                    AND skk.jenis_sk = 7 
                LEFT JOIN emp_contract empc ON skk.no_sk = empc.contract_no 
            WHERE
                emp.emp_work_status = %s 
                AND emp.emp_code != %s
            GROUP BY
                emp.emp_id
            """
    params = (EmpWorkStatus.KaryawanAktif.value, "Pengaduan")
    with get_smartoffice_connection_pool() as conn:
        with conn.cursor() as cursor:
            cursor.execute(query, params)
            return cursor.fetchall()


def fetch_data_for_profil_gaji():
    query = """
        SELECT
            em.emp_code AS nipam,
            em.tgl_pengangkatan AS tmtKerja,
            em.tmt_pensiun AS tmtPensiun,
        CASE
            WHEN em.emp_flag = 1 THEN "PEGAWAI" 
            WHEN em.emp_flag = 2 THEN "KONTRAK" 
            WHEN em.emp_flag = 3 THEN "NON_PEGAWAI" 
            WHEN em.emp_flag = 4 THEN "CAPEG" 
            WHEN em.emp_flag = 5 THEN "HONORER" 
            WHEN em.emp_flag = 6 THEN "CALON_HONORER" 
        END AS statusPegawai,
            em.emp_gp AS gajiPokok,
            em.emp_phdp AS phdp,
            ep.askes_flag AS isAskes,
            ep.emp_tax_code AS kodePajak,
            em.emp_sg_id AS gajiProfilId,
            ep.id_rumdin AS rumahDinasId
        FROM
            employee AS em
            INNER JOIN emp_profile AS ep ON em.emp_profile_id = ep.emp_profile_id 
        WHERE
            em.emp_work_status = %s
        """
    params=(EmpWorkStatus.KaryawanAktif.value,)
    with get_smartoffice_connection_pool() as conn:
        with conn.cursor() as cursor:
            cursor.execute(query, params)
            return cursor.fetchall()


def fetch_gaji_employee():
    query = """
            SELECT
                emp.emp_sg_id AS gajiProfilId,
                emp.emp_phdp AS phdp,
                ep.id_rumdin AS rumahDinasId,
                emp.emp_code AS nipam
            FROM 
                employee AS emp
                JOIN emp_profile AS ep ON emp.emp_profile_id = ep.emp_profile_id
            WHERE
                emp.emp_work_status = %s 
                AND emp.emp_code != %s
            """
    params = (EmpWorkStatus.KaryawanAktif.value, "Pengaduan")
    with get_smartoffice_connection_pool() as conn:
        with conn.cursor() as cursor:
            cursor.execute(query, params)
            return cursor.fetchall()
