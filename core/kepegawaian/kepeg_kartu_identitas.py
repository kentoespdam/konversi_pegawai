import pandas as pd

from core.config import save_update_kepegawaian


def save_kartu_identitas_from_emp_profile(df: pd.DataFrame):
    data = [(row.nik, row.nik, 'SYSTEM') for row in df.itertuples(index=False)]

    query = """INSERT INTO kartu_identitas (nomor_kartu, nik, created_by, jenis_kitas_id)
               VALUES (%s, %s, %s, 1)
               ON DUPLICATE KEY UPDATE nomor_kartu=VALUES(nomor_kartu),
                                       nik=VALUES(nik),
                                       created_by=VALUES(created_by),
                                       jenis_kitas_id=VALUES(jenis_kitas_id) \
            """
    save_update_kepegawaian(query, data)


def save_kartu_identitas_from_emp_card(df: pd.DataFrame):
    data = [(
        row.nik,
        row.jenis_kitas_id if row.jenis_kitas_id > 0 else None,
        row.nomor_kartu,
        row.tanggal_expired,
        row.tanggal_terima,
        row.notes,
        row.is_deleted,
        'SYSTEM'
    ) for row in df.itertuples(index=False)]

    query = """
            INSERT INTO kartu_identitas (nik, jenis_kitas_id, nomor_kartu, tanggal_expired, tanggal_terima,
                                         notes, is_deleted, created_by)
            VALUES (%s, %s, %s, %s, %s,
                    %s, %s, %s)
            ON DUPLICATE KEY UPDATE nik=VALUES(nik),
                                    jenis_kitas_id=VALUES(jenis_kitas_id),
                                    nomor_kartu=VALUES(nomor_kartu),
                                    tanggal_expired=VALUES(tanggal_expired),
                                    tanggal_terima=VALUES(tanggal_terima),
                                    notes=VALUES(notes),
                                    is_deleted=VALUES(is_deleted) \
            """
    save_update_kepegawaian(query, data)
