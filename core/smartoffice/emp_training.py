from config import get_smartoffice_connection_pool
from core.enums import EmpWorkStatus


def fetch_data_for_pelatihan(id: int = None):
    query = """
        SELECT
            ep.emp_identity_number AS biodataId,
            et.training_id AS jenisPelatihanId,
            et.nama_pelatihan AS nama,
            et.lembaga,
            et.tgl_mulai AS tanggalMulai,
            et.tgl_selesai AS tanggalSelesai,
            et.lulus,
            et.nilai,
            et.ikatan_dinas AS ikatanDinas,
            et.tgl_akhir_ikatan AS tanggalAkhirIkatan,
            et.keterangan AS notes 
        FROM
            emp_training AS et
            INNER JOIN emp_profile AS ep ON et.emp_profile_id = ep.emp_profile_id
            INNER JOIN employee AS em ON ep.emp_profile_id = em.emp_profile_id 
        WHERE
            em.emp_work_status = %s 
        """
    params = (EmpWorkStatus.KaryawanAktif.value)
    if id is not None:
        query += " AND et.id = %s"
        params = (EmpWorkStatus.KaryawanAktif.value, id,)
    with get_smartoffice_connection_pool() as conn:
        with conn.cursor() as cursor:
            cursor.execute(query, params)
            return cursor.fetchall()
