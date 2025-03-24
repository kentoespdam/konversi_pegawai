from config import get_smartoffice_connection_pool


def fetch_data_for_riwayat_kontrak():
    query = """
        SELECT
            em.emp_code AS nipam,
            ep.emp_name AS nama,
            ec.contract_no AS nomor_kontrak,
            ec.contract_received_date AS tanggal_sk,
            ec.contract_start_date AS tanggal_mulai,
            ec.contract_exp_date AS tanggal_selesai,
            ec.ec_description AS notes,
            ep.emp_identity_number 
        FROM
            emp_contract AS ec
            INNER JOIN employee AS em ON ec.emp_code = em.emp_code
            INNER JOIN emp_profile AS ep ON em.emp_profile_id = ep.emp_profile_id 
        WHERE
            ep.emp_identity_number != NULL 
            OR ep.emp_identity_number != ''
        """
    with get_smartoffice_connection_pool() as conn:
        with conn.cursor() as cursor:
            cursor.execute(query)
            return cursor.fetchall()
