import pandas as pd

from core.config import save_update_kepegawaian


def save_keahlian_from_emp_skill(df: pd.DataFrame):
    # Convert NaN to None for database compatibility
    df = df.where(pd.notnull(df), None)

    data = [(
        row.biodata_id,
        row.jenis_keahlian_id if row.jenis_keahlian_id and row.jenis_keahlian_id > 0 else None,
        row.kualifikasi,
        row.sertifikasi,
        row.institusi,
        row.tahun,
        row.disetujui,
        row.tanggal_pengajuan,
        row.tanggal_disetujui,
        row.is_deleted,
        'SYSTEM'
    ) for row in df.itertuples(index=False)]

    query = """
            INSERT INTO keahlian (biodata_id, jenis_keahlian_id, kualifikasi, sertifikasi, institusi,
                                  tahun, disetujui, tanggal_pengajuan, tanggal_disetujui, is_deleted,
                                  created_by)
            VALUES (%s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s,
                    %s)
            ON DUPLICATE KEY UPDATE 
                jenis_keahlian_id=VALUES(jenis_keahlian_id),
                kualifikasi=VALUES(kualifikasi),
                sertifikasi=VALUES(sertifikasi),
                institusi=VALUES(institusi),
                tahun=VALUES(tahun),
                disetujui=VALUES(disetujui),
                tanggal_pengajuan=VALUES(tanggal_pengajuan),
                tanggal_disetujui=VALUES(tanggal_disetujui),
                is_deleted=VALUES(is_deleted),
                updated_by='SYSTEM'
            """

    save_update_kepegawaian(query, data)
