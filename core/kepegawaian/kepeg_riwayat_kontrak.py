import pandas as pd
from icecream import ic

from config import get_kepegawaian_connection_pool


def save_riwayat_kontrak_from_emp_contract(df: pd.DataFrame):
    data = [(
        row.jenis_kontrak,
        row.pegawai_id,
        row.nipam,
        row.nama,
        row.nomor_kontrak,
        row.tanggal_sk,
        row.tanggal_mulai,
        row.tanggal_selesai,
        row.organisasi_id if row.organisasi_id > 0 else None,
        row.jabatan_id if row.jabatan_id > 0 else None,
        row.is_latest,
        row.notes,
        row.is_deleted,
        0,
        'SYSTEM'
    )for row in df.itertuples(index=False)]

    query = """
        INSERT INTO riwayat_kontrak (
            jenis_kontrak, pegawai_id, nipam, nama, nomor_kontrak, 
            tanggal_sk, tanggal_mulai, tanggal_selesai, organisasi_id, jabatan_id,
            is_latest, notes, is_deleted, version, created_by
        ) VALUES (
            %s, %s, %s, %s, %s, 
            %s, %s, %s, %s, %s, 
            %s, %s, %s, %s, %s
        )
    """

    with get_kepegawaian_connection_pool(autocommit=True) as connection:
        with connection.cursor() as cursor:
            cursor.executemany(query, data)
            affected = cursor.rowcount
            ic(affected, "row(s) affected")
            connection.commit()
