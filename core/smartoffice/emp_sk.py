from config import get_smartoffice_connection_pool


def fetch_data_for_riwayat_sk():
    query = """
        SELECT
            em.emp_code AS nipam,
            ep.emp_name AS nama,
            esk.no_sk AS nomor_sk,
            esk.jenis_sk,
            esk.tgl_sk AS tanggal_sk,
            esk.tmt_sk AS tmt_berlaku,
            gol.golongan,
            esk.gaji_pokok,
            esk.mkg_tahun,
            esk.mkg_bulan,
            esk.kenaikan_berikutnya,
            esk.mkgb_tahun,
            esk.mkgb_bulan,
            esk.flag_update_master AS update_master,
            esk.keterangan AS notes 
        FROM
            emp_sk AS esk
            INNER JOIN employee AS em ON esk.emp_id = em.emp_id
            INNER JOIN emp_profile AS ep ON em.emp_profile_id = ep.emp_profile_id
            LEFT JOIN golongan AS gol ON esk.golongan_id = gol.id
        """
    with get_smartoffice_connection_pool() as conn:
        with conn.cursor() as cursor:
            cursor.execute(query)
            return cursor.fetchall()