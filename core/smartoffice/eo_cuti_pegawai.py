from core.config import fetch_smartoffice


def fetch_cuti_pegawai():
    query = """
            SELECT cp.cp_id                                  AS id,
                   em.emp_id                                 AS pegawai_id,
                   cp.emp_code                               AS nipam,
                   cp.emp_name                               AS nama,
                   CONCAT_WS(' - ', cp.gol_name, cp.pangkat) AS pangkat_golongan,
                   cp.org_id                                 AS organisasi_id,
                   cp.pos_id                                 AS jabatan_id,
                   (cp.cp_type - 1)                          AS jenis_pengajuan_cuti,
                   cp.cp_jenis                               AS jenis_cuti_id,
                   IFNULL(cp.cp_sub_jenis, 0)                AS sub_jenis_cuti_id,
                   cp.cp_ref_id                              AS ref_cuti_id,
                   cp.cp_request_at                          AS created_at,
                   cp.cp_sdate                               AS tanggal_mulai,
                   cp.cp_edate                               AS tanggal_selesai,
                   cp.cp_days                                AS jumlah_hari,
                   cp.cp_work_days                           AS jumlah_hari_kerja,
                   IFNULL(cp.cp_before, 0)                   AS kuota_awal,
                   IFNULL(cp.cp_after, 0)                    AS kuota_akhir,
                   cp.cp_alasan                              AS alasan,
                   (cp.cp_approval_status - 1)               AS approval_cuti_status,
                   cp.cp_approval_level                      AS approval_level,
                   cp.cp_curr_pos                            AS pic_saat_ini_id,
                   IFNULL(cp.cp_k0, 0)                       AS riwayat_kuota0,
                   IFNULL(cp.cp_k1, 0)                       AS riwayat_kuota1,
                   IFNULL(cp.cp_n0, 0)                       AS riwayat_pakai0,
                   IFNULL(cp.cp_n1, 0)                       AS riwayat_pakai1,
                   IFNULL(cp.cp_w0, 0)                       AS riwayat_sisa0,
                   IFNULL(cp.cp_w1, 0)                       AS riwayat_sisa1
            FROM cuti_pegawai AS cp
                     INNER JOIN employee AS em ON cp.emp_code = em.emp_code
            """
    return fetch_smartoffice(query)
