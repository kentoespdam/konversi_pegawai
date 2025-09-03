import pandas as pd
from icecream import ic
from core.config import get_kepegawaian_connection_pool


def save_kartu_identitas_from_emp_profile(df: pd.DataFrame):
    list = [(row.nik, row.nik, 'SYSTEM') for row in df.itertuples(index=False)]

    query = "INSERT INTO kartu_identitas (nomor_kartu, nik, created_by, jenis_kitas_id) VALUES (%s, %s, %s, 1)"
    with get_kepegawaian_connection_pool(autocommit=True) as connection:
        with connection.cursor() as cursor:
            cursor.executemany(query, list)
            affected = cursor.rowcount
            ic(affected, "row(s) affected")
            connection.commit()


def save_kartu_identitas_from_emp_card(df: pd.DataFrame):
    data = [(
        row.nik,
        row.jenis_kitas_id if row.jenis_kitas_id > 0 else None,
        row.nomor_kartu,
        row.tanggal_expired,
        row.tanggal_terima,
        row.notes,
        row.is_deleted,
        0,
        'SYSTEM'
    ) for row in df.itertuples(index=False)]

    query = """
        INSERT INTO kartu_identitas (
            nik, jenis_kitas_id, nomor_kartu, tanggal_expired, tanggal_terima, 
            notes, is_deleted, version, created_by
        ) VALUES (
            %s, %s, %s, %s, %s, 
            %s, %s, %s, %s
        ) ON DUPLICATE KEY UPDATE 
            nik=VALUES(nik),
            jenis_kitas_id=VALUES(jenis_kitas_id),
            nomor_kartu=VALUES(nomor_kartu),
            tanggal_expired=VALUES(tanggal_expired),
            tanggal_terima=VALUES(tanggal_terima),
            notes=VALUES(notes),
            is_deleted=VALUES(is_deleted)
    """

    with get_kepegawaian_connection_pool() as connection:
        with connection.cursor() as cursor:
            cursor.executemany(query, data)
            affected = cursor.rowcount
            ic(affected, "row(s) affected")
            connection.commit()
