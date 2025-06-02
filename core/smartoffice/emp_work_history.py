from config import get_smartoffice_connection_pool


def fetch_emp_work_history_for_emp_sk():
    query = """
        SELECT
            emp_id,
            jenis_sk,
            no_sk,
            esk_no_sk,
            tgl_sk,
            tmt_sk,
            keterangan 
        FROM
            (
            SELECT
                em.emp_id,
                5 AS jenis_sk,
                ewh.ewh_sk_no AS no_sk,
                esk.no_sk AS esk_no_sk,
                ewh.ewh_sdate AS tgl_sk,
                ewh.ewh_sdate AS tmt_sk,
                ewh.ewh_note AS keterangan 
            FROM
                emp_work_history AS ewh
                LEFT JOIN emp_sk AS esk ON ewh.ewh_sk_no = esk.no_sk
                INNER JOIN employee AS em ON ewh.emp_code = em.emp_code	
        ) AS ewh1 
        WHERE
            ISNULL(esk_no_sk)
    """
    with get_smartoffice_connection_pool() as conn:
        with conn.cursor() as cursor:
            cursor.execute(query)
            return cursor.fetchall()


def fetch_emp_work_history_for_riwayat_mutasi():
    query = """
        SELECT
            em.emp_id AS pegawai_id,
            ewh.ewh_sk_no AS nomor_sk,
            ewh.emp_code AS nipam,
            ep.emp_name AS nama,
            ewh.ewh_sdate AS tmt_berlaku,
            ewh.ewh_edate AS tanggal_berakhir,
            ewh.ewh_type AS jenis_mutasi,
            IFNULL( ewh.ewh_org_id, 0 ) AS organisasi_id,
            ewh.ewh_org_name AS nama_organisasi,
            IFNULL( ewh.ewh_pos_id, 0 ) AS jabatan_id,
            ewh.ewh_pos_name AS nama_jabatan,
            IFNULL( ewh.ewh_old_org_id, 0 ) AS organisasi_lama_id,
            ewh.ewh_old_org_name AS nama_organisasi_lama,
            IFNULL( ewh.ewh_old_pos_id, 0 ) AS jabatan_lama_id,
            ewh.ewh_old_pos_name AS nama_jabatan_lama,
            ewh.ewh_note AS notes,
            IF(ewh.ewh_status=3,TRUE,FALSE) AS is_deleted 
        FROM
            emp_work_history AS ewh
            INNER JOIN employee AS em ON ewh.emp_code = em.emp_code
            INNER JOIN emp_profile AS ep ON em.emp_profile_id = ep.emp_profile_id 
    """
    with get_smartoffice_connection_pool() as conn:
        with conn.cursor() as cursor:
            cursor.execute(query)
            return cursor.fetchall()


def fetch_data_for_riwayat_mutasi():
    query = """
        SELECT
            ewh.ewh_id AS id,
            ep.emp_identity_number AS nik,
            ewh.emp_code AS nipam,
            ewh.ewh_sdate AS tmt_berlaku,
            ewh.ewh_edate AS tanggal_berakhir,
            ewh.ewh_pos_name AS nama_jabatan,
            ewh.ewh_org_name AS nama_organisasi,
            ewh.ewh_old_pos_name AS nama_jabatan_lama,
            ewh.ewh_old_org_name AS nama_organisasi_lama,
            ewh.ewh_note AS notes,
            esk.no_sk,
            esk.tmt_sk,
            esk.jenis_sk - 1 AS jenis_sk,
            esk.keterangan,
            golongan.golongan AS golongan 
        FROM
            emp_work_history AS ewh
            JOIN employee AS em ON ewh.emp_code = em.emp_code
            LEFT JOIN emp_sk AS esk ON em.emp_id = esk.emp_id 
            AND ewh.ewh_sdate = esk.tmt_sk
            JOIN emp_profile ep ON em.emp_profile_id = ep.emp_profile_id
            LEFT JOIN golongan ON esk.golongan_id = golongan.id 
        WHERE
            em.emp_flag IN ( 1, 2 ) 
            AND ( ep.emp_identity_number != NULL OR ep.emp_identity_number != "" ) 
        ORDER BY
            ewh.ewh_id ASC
        """
    with get_smartoffice_connection_pool() as conn:
        with conn.cursor() as cursor:
            cursor.execute(query)
            return cursor.fetchall()
