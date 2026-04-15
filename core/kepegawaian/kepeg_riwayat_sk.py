import pandas as pd

from core.config import save_update_kepegawaian, fetch_kepegawaian


def save_riwayat_sk_from_emp_sk(df: pd.DataFrame):
    data = [(
        row.pegawai_id,
        row.nipam,
        row.nama,
        row.nomor_sk,
        row.jenis_sk,
        row.tanggal_sk,
        row.tmt_berlaku,
        row.golongan_id if row.golongan_id > 0 else None,
        row.gaji_pokok,
        row.mkg_tahun,
        row.mkg_bulan,
        row.kenaikan_berikutnya,
        row.mkgb_tahun,
        row.mkgb_bulan,
        row.update_master,
        row.notes,
        row.is_deleted,
        'SYSTEM'
    ) for row in df.itertuples(index=False)]

    query = """
            INSERT INTO riwayat_sk (pegawai_id, nipam, nama, nomor_sk, jenis_sk,
                                    tanggal_sk, tmt_berlaku, golongan_id, gaji_pokok, mkg_tahun,
                                    mkg_bulan, kenaikan_berikutnya, mkgb_tahun, mkgb_bulan, update_master,
                                    notes, is_deleted, created_by)
            VALUES (%s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s,
                    %s, %s, %s) \
            """

    save_update_kepegawaian(query, data)


def fetch_all_riwayat_sk():
    query = "SELECT * FROM riwayat_sk"
    return fetch_kepegawaian(query)
