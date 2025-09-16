from core.config import get_smartoffice_connection_pool, fetch_smartoffice
from core.enums import EmpWorkStatus


def fetch_emp_card_for_kartu_identitas():
    query = """
            SELECT ep.emp_identity_number          AS nik,
                   ec.ei_number                    AS nomor_kartu,
                   ec.ei_exp_date                  AS tanggal_expired,
                   ec.ei_received_date             AS tanggal_terima,
                   ec.ei_description               AS notes,
                   IF
                   (ec.ei_status = 3, TRUE, FALSE) AS is_deleted,
                   ejc.text                        AS jenis_kitas
            FROM emp_card AS ec
                     INNER JOIN employee AS em ON ec.emp_code = em.emp_code
                     INNER JOIN emp_profile AS ep ON em.emp_profile_id = ep.emp_profile_id
                     INNER JOIN sys_reference AS ejc ON ec.ei_type = ejc.`value`
                AND ejc.`code` = %s \
            """
    where = ("emp_card",)
    return fetch_smartoffice(query, where)


def fetch_data_for_kartu_identitas(id: int = None):
    query = """
            SELECT ep.emp_identity_number AS nik,
                   ref_card_type.text     AS jenisKartu,
                   ec.ei_number           AS nomorKartu,
                   ec.ei_exp_date         AS tanggalExpired,
                   ec.ei_received_date    AS tanggalTerima,
                   ec.ei_description      AS notes
            FROM emp_card AS ec
                     INNER JOIN employee AS em ON ec.emp_code = em.emp_code
                     INNER JOIN emp_profile AS ep ON em.emp_profile_id = ep.emp_profile_id
                     INNER JOIN sys_reference AS ref_card_type ON ec.ei_type = ref_card_type.`value`
                AND ref_card_type.`code` = 'emp_card'
            WHERE em.emp_work_status = %s \
            """
    params = (EmpWorkStatus.KaryawanAktif.value,)
    if id is not None:
        query += " AND ec.id = %s"
        params = (EmpWorkStatus.KaryawanAktif.value, id,)
    with get_smartoffice_connection_pool() as conn:
        with conn.cursor() as cursor:
            cursor.execute(query, params)
            return cursor.fetchall()
