import pandas as pd

from core.config import save_update_kepegawaian, get_kepegawaian_connection_pool


def save_pengalaman_kerja_from_emp_work_experience(df: pd.DataFrame):
    # TRUNCATE to ensure idempotency as table lacks Unique Key
    with get_kepegawaian_connection_pool() as connection:
        with connection.cursor() as cursor:
            cursor.execute("TRUNCATE TABLE pengalaman_kerja")
        connection.commit()

    data = [(
        row.biodata_id,
        row.nama_perusahaan,
        row.type_perusahaan,
        row.jabatan,
        row.lokasi,
        row.tahun_masuk,
        row.tahun_keluar,
        row.notes,
        row.is_deleted,
        row.disetujui,
        row.tanggal_pengajuan,
        row.tanggal_disetujui,
        row.disetujui_oleh,
        'SYSTEM'
    ) for row in df.itertuples(index=False)]

    query = """
            INSERT INTO pengalaman_kerja (biodata_id, nama_perusahaan, type_perusahaan, jabatan, lokasi,
                                          tahun_masuk, tahun_keluar, notes, is_deleted,
                                          disetujui, tanggal_pengajuan, tanggal_disetujui, disetujui_oleh,
                                          created_by)
            VALUES (%s, %s, %s, %s, %s,
                    %s, %s, %s, %s,
                    %s, %s, %s, %s,
                    %s)
            ON DUPLICATE KEY UPDATE nama_perusahaan=VALUES(nama_perusahaan),
                                    type_perusahaan=VALUES(type_perusahaan),
                                    jabatan=VALUES(jabatan),
                                    lokasi=VALUES(lokasi),
                                    tahun_masuk=VALUES(tahun_masuk),
                                    tahun_keluar=VALUES(tahun_keluar),
                                    notes=VALUES(notes),
                                    is_deleted=VALUES(is_deleted),
                                    disetujui=VALUES(disetujui),
                                    tanggal_pengajuan=VALUES(tanggal_pengajuan),
                                    tanggal_disetujui=VALUES(tanggal_disetujui),
                                    disetujui_oleh=VALUES(disetujui_oleh),
                                    updated_at=CURRENT_TIMESTAMP
            """

    save_update_kepegawaian(query, data)
