import pandas as pd

from core.config import save_update_kepegawaian


def save_pelatihan_from_emp_training(df: pd.DataFrame):
    data = [(
        row.biodata_id,
        row.jenis_pelatihan_id,
        row.nama,
        row.lembaga,
        row.tanggal_mulai,
        row.tanggal_selesai,
        row.lulus,
        row.nilai,
        row.ikatan_dinas,
        row.tanggal_akhir_ikatan,
        row.notes,
        row.disetujui,
        row.tanggal_pengajuan,
        row.tanggal_disetujui,
        row.is_deleted,
        0,
        'SYSTEM'
    ) for row in df.itertuples(index=False)]

    query = """
            INSERT INTO pelatihan (biodata_id, jenis_pelatihan_id, nama, lembaga, tanggal_mulai,
                                   tanggal_selesai, lulus, nilai, ikatan_dinas, tanggal_akhir_ikatan,
                                   notes, disetujui, tanggal_pengajuan, tanggal_disetujui, is_deleted,
                                   version, created_by)
            VALUES (%s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s,
                    %s, %s)
            ON DUPLICATE KEY UPDATE biodata_id=VALUES(biodata_id)
            """

    save_update_kepegawaian(query, data)
