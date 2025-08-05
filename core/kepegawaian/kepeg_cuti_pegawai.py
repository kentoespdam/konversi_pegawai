import pandas as pd
from config import get_kepegawaian_connection_pool
from icecream import ic


def save_cuti_pegawai(df: pd.DataFrame):
    data_list = [(
        row.id,
        row.pegawai_id,
        row.nipam,
        row.nama,
        row.pangkat_golongan,
        row.organisasi_id if row.organisasi_id > 0 else None,
        row.jabatan_id if row.jabatan_id > 0 else None,
        row.jenis_pengajuan_cuti,
        row.ref_cuti_id if row.ref_cuti_id > 0 else None,
        row.jenis_cuti_id,
        row.sub_jenis_cuti_id if row.sub_jenis_cuti_id > 0 else None,
        row.tanggal_mulai,
        row.tanggal_selesai,
        row.jumlah_hari,
        row.jumlah_hari_kerja,
        row.kuota_awal,
        row.kuota_akhir,
        row.alasan,
        row.approval_cuti_status,
        row.approval_level,
        row.pic_saat_ini_id,
        row.riwayat_kuota0,
        row.riwayat_kuota1,
        row.riwayat_pakai0,
        row.riwayat_pakai1,
        row.riwayat_sisa0,
        row.riwayat_sisa1,
        row.is_claimed,
        False,
        row.created_at,
        "DEV",
        0
    ) for row in df.itertuples(index=False)]
    sql = """
          INSERT INTO cuti_pegawai (id, pegawai_id, nipam, nama, pangkat_golongan, 
                                    organisasi_id, jabatan_id, jenis_pengajuan_cuti, ref_cuti_id, jenis_cuti_id, 
                                    sub_jenis_cuti_id, tanggal_mulai, tanggal_selesai, jumlah_hari, jumlah_hari_kerja, 
                                    kuota_awal, kuota_akhir, alasan, approval_cuti_status, approval_level, 
                                    pic_saat_ini_id, riwayat_kuota0, riwayat_kuota1, riwayat_pakai0, riwayat_pakai1, 
                                    riwayat_sisa0, riwayat_sisa1, is_claimed, is_deleted, created_at, 
                                    created_by, version)
          VALUES (%s, %s, %s, %s, %s, 
                  %s, %s, %s, %s, %s, 
                  %s, %s, %s, %s, %s, 
                  %s, %s, %s, %s, %s, 
                  %s, %s, %s, %s, %s, 
                  %s, %s, %s, %s, %s, 
                  %s, %s)
          ON DUPLICATE KEY UPDATE pegawai_id=VALUES(pegawai_id),
                                  nipam=VALUES(nipam),
                                  nama=VALUES(nama),
                                  pangkat_golongan=VALUES(pangkat_golongan),
                                  organisasi_id=VALUES(organisasi_id),
                                  jabatan_id=VALUES(jabatan_id),
                                  jenis_pengajuan_cuti=VALUES(jenis_pengajuan_cuti),
                                  ref_cuti_id=VALUES(ref_cuti_id),
                                  jenis_cuti_id=VALUES(jenis_cuti_id),
                                  sub_jenis_cuti_id=VALUES(sub_jenis_cuti_id),
                                  tanggal_mulai=VALUES(tanggal_mulai),
                                  tanggal_selesai=VALUES(tanggal_selesai),
                                  jumlah_hari=VALUES(jumlah_hari),
                                  jumlah_hari_kerja=VALUES(jumlah_hari_kerja),
                                  kuota_awal=VALUES(kuota_awal),
                                  kuota_akhir=VALUES(kuota_akhir),
                                  alasan=VALUES(alasan),
                                  approval_cuti_status=VALUES(approval_cuti_status),
                                  approval_level=VALUES(approval_level),
                                  pic_saat_ini_id=VALUES(pic_saat_ini_id),
                                  riwayat_kuota0=VALUES(riwayat_kuota0),
                                  riwayat_kuota1=VALUES(riwayat_kuota1),
                                  riwayat_pakai0=VALUES(riwayat_pakai0),
                                  riwayat_pakai1=VALUES(riwayat_pakai1),
                                  riwayat_sisa0=VALUES(riwayat_sisa0),
                                  riwayat_sisa1=VALUES(riwayat_sisa1),
                                  is_claimed=VALUES(is_claimed),
                                  is_deleted=VALUES(is_deleted),
                                  created_at=VALUES(created_at),
                                  created_by=VALUES(created_by),
                                  version=VALUES(version)
          """
    try:
        with get_kepegawaian_connection_pool() as conn:
            with conn.cursor() as cursor:
                cursor.executemany(sql, data_list)
                ic(cursor.rowcount, "row(s) affected")
                conn.commit()
    except Exception as e:
        ic(e)
        # raise e