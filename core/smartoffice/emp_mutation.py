from config import get_smartoffice_connection_pool


def fetch_data_for_riwayat_mutasi():
    query="""
        SELECT
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
            esk.jenis_sk -1 AS jenis_sk,
            esk.keterangan,
            emp_profile.emp_identity_number AS nik, 
            golongan.golongan AS golongan 
        FROM
            emp_work_history AS ewh
            INNER JOIN employee AS em ON ewh.emp_code = em.emp_code
            INNER JOIN emp_sk AS esk ON em.emp_id = esk.emp_id 
            AND ewh.ewh_sdate = esk.tmt_sk
            INNER JOIN emp_profile ON em.emp_profile_id = emp_profile.emp_profile_id 
            INNER JOIN golongan ON esk.golongan_id = golongan.id 
        WHERE
            emp_profile.emp_identity_number != NULL 
            OR emp_profile.emp_identity_number != ""
        """
    with get_smartoffice_connection_pool() as conn:
        with conn.cursor() as cursor:
            cursor.execute(query)
            return cursor.fetchall()