from config import get_kepegawaian_connection_pool


def save_data_riwayat_sk(datas: list):
    query = """
        INSERT INTO riwayat_sk (
            pegawai_id, nipam, nama, nomor_sk, jenis_sk, 
            tanggal_sk, tmt_berlaku, golongan_id, gaji_pokok, mkg_tahun, 
            mkg_bulan, kenaikan_berikutnya, mkgb_tahun, mkgb_bulan, update_master, 
            notes, created_by, version
        ) VALUES (
            %s, %s, %s, %s, %s, 
            %s, %s, %s, %s, %s, 
            %s, %s, %s, %s, %s, 
            %s, 'SYSTEM', 1
        )
    """
    with get_kepegawaian_connection_pool() as conn:
        with conn.cursor() as cursor:
            cursor.executemany(query, datas)
            conn.commit()
