from core.config import fetch_smartoffice
from core.enums import EmpWorkStatus


def fetch_emp_training_for_pelatihan():
    query = """
            SELECT ep.emp_identity_number           AS biodata_id,
                   et.training_id                   AS jenis_pelatihan_id,
                   et.nama_pelatihan                AS nama,
                   et.lembaga,
                   et.tgl_mulai                     AS tanggal_mulai,
                   et.tgl_selesai                   AS tanggal_selesai,
                   et.lulus,
                   et.nilai,
                   et.ikatan_dinas,
                   et.tgl_akhir_ikatan              AS tanggal_akhir_ikatan,
                   et.keterangan                    AS notes,
                   TRUE                             AS disetujui,
                   et.entry_date                    AS tanggal_pengajuan,
                   et.approve_date                  AS tanggal_disetujui,
                   et.approve_by                    AS disetujui_oleh,
                   IF(et.`status` = 3, TRUE, FALSE) AS is_deleted
            FROM emp_training AS et
                     INNER JOIN emp_profile AS ep ON et.emp_profile_id = ep.emp_profile_id \
            """
    return fetch_smartoffice(query)


def fetch_data_for_pelatihan(_id: int = None):
    query = """
            SELECT ep.emp_identity_number AS biodataId,
                   et.training_id         AS jenisPelatihanId,
                   et.nama_pelatihan      AS nama,
                   et.lembaga,
                   et.tgl_mulai           AS tanggalMulai,
                   et.tgl_selesai         AS tanggalSelesai,
                   et.lulus,
                   et.nilai,
                   et.ikatan_dinas        AS ikatanDinas,
                   et.tgl_akhir_ikatan    AS tanggalAkhirIkatan,
                   et.keterangan          AS notes
            FROM emp_training AS et
                     INNER JOIN emp_profile AS ep ON et.emp_profile_id = ep.emp_profile_id
                     INNER JOIN employee AS em ON ep.emp_profile_id = em.emp_profile_id
            WHERE em.emp_work_status = %s \
            """
    params = (EmpWorkStatus.KaryawanAktif.value,)
    if _id is not None:
        query += " AND et.id = %s"
        params += (_id,)

    return fetch_smartoffice(query, params)
