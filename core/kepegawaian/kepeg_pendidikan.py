import pandas as pd

from core.config import save_update_kepegawaian


def save_pendidikan_from_emp_education(df: pd.DataFrame):
    data = [(
        row.biodata_id,
        row.jenjang_id if row.jenjang_id > 0 else None,
        row.gelar_belakang,
        row.jurusan,
        row.institusi,
        row.tahun_masuk,
        row.is_lulus,
        row.tahun_lulus,
        row.gpa,
        row.is_latest,
        row.disetujui,
        row.tanggal_pengajuan,
        row.tanggal_disetujui,
        row.disetujui_oleh,
        row.is_deleted,
        'SYSTEM'
    ) for row in df.itertuples(index=False)]

    query = """
            INSERT INTO pendidikan (biodata_id, jenjang_id, gelar_belakang, jurusan, institusi,
                                    tahun_masuk, is_lulus, tahun_lulus, gpa, is_latest, disetujui,
                                    tanggal_pengajuan, tanggal_disetujui, disetujui_oleh, is_deleted,
                                created_by)
            VALUES (%s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s,
                    %s)
            ON DUPLICATE KEY UPDATE jenjang_id=VALUES(jenjang_id),
                                    gelar_belakang=VALUES(gelar_belakang),
                                    jurusan=VALUES(jurusan),
                                    institusi=VALUES(institusi),
                                    tahun_masuk=VALUES(tahun_masuk),
                                    is_lulus=VALUES(is_lulus),
                                    tahun_lulus=VALUES(tahun_lulus),
                                    gpa=VALUES(gpa),
                                    is_latest=VALUES(is_latest),
                                    disetujui=VALUES(disetujui),
                                    tanggal_pengajuan=VALUES(tanggal_pengajuan),
                                    tanggal_disetujui=VALUES(tanggal_disetujui),
                                    disetujui_oleh=VALUES(disetujui_oleh),
                                    is_deleted=VALUES(is_deleted),
                                    updated_at=CURRENT_TIMESTAMP \
            """
    save_update_kepegawaian(query, data)
