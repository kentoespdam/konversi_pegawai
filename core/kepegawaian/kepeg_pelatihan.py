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
        'SYSTEM'
    ) for row in df.itertuples(index=False)]

    query = """
            INSERT INTO pelatihan (biodata_id, jenis_pelatihan_id, nama, lembaga, tanggal_mulai,
                                   tanggal_selesai, lulus, nilai, ikatan_dinas, tanggal_akhir_ikatan,
                                   notes, disetujui, tanggal_pengajuan, tanggal_disetujui, is_deleted,
                                   created_by)
            VALUES (%s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s,
                    %s)
            ON DUPLICATE KEY UPDATE 
                jenis_pelatihan_id=VALUES(jenis_pelatihan_id),
                nama=VALUES(nama),
                lembaga=VALUES(lembaga),
                tanggal_mulai=VALUES(tanggal_mulai),
                tanggal_selesai=VALUES(tanggal_selesai),
                lulus=VALUES(lulus),
                nilai=VALUES(nilai),
                ikatan_dinas=VALUES(ikatan_dinas),
                tanggal_akhir_ikatan=VALUES(tanggal_akhir_ikatan),
                notes=VALUES(notes),
                disetujui=VALUES(disetujui),
                tanggal_pengajuan=VALUES(tanggal_pengajuan),
                tanggal_disetujui=VALUES(tanggal_disetujui),
                is_deleted=VALUES(is_deleted),
                updated_at=CURRENT_TIMESTAMP
            """

    save_update_kepegawaian(query, data)
