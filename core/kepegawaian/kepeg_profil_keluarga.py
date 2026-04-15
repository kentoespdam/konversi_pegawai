import pandas as pd

from core.config import save_update_kepegawaian


def save_profil_keluarga_from_emp_profile(df: pd.DataFrame):
    # Idempotency: Truncate table before migration since it lacks unique keys
    save_update_kepegawaian("TRUNCATE TABLE profil_keluarga", None)

    data = [(
        row.biodata_id,
        row.nik,
        row.nama,
        row.jenis_kelamin,
        row.agama,
        row.hubungan_keluarga,
        row.tempat_lahir,
        row.tanggal_lahir,
        row.tanggungan,
        0,  # pendidikan_id
        row.status_pendidikan,
        row.status_kawin,
        row.notes,
        row.is_deleted,
        'SYSTEM'
    ) for row in df.itertuples(index=False)]

    query = """
            INSERT INTO profil_keluarga (biodata_id, nik, nama, jenis_kelamin, agama, hubungan_keluarga,
                                         tempat_lahir, tanggal_lahir, tanggungan, pendidikan_id, status_pendidikan,
                                         status_kawin, notes, is_deleted, created_by)
            VALUES (%s, %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s,
                    %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE nama=VALUES(nama),
                                    jenis_kelamin=VALUES(jenis_kelamin),
                                    agama=VALUES(agama),
                                    hubungan_keluarga=VALUES(hubungan_keluarga),
                                    tempat_lahir=VALUES(tempat_lahir),
                                    tanggal_lahir=VALUES(tanggal_lahir),
                                    tanggungan=VALUES(tanggungan),
                                    pendidikan_id=VALUES(pendidikan_id),
                                    status_pendidikan=VALUES(status_pendidikan),
                                    status_kawin=VALUES(status_kawin),
                                    notes=VALUES(notes),
                                    is_deleted=VALUES(is_deleted),
                                    updated_at=CURRENT_TIMESTAMP \
            """
    save_update_kepegawaian(query, data)
