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
        ) ON DUPLICATE KEY UPDATE 
            jenis_kontrak = VALUES(jenis_kontrak),
            pegawai_id = VALUES(pegawai_id),
            nipam = VALUES(nipam),
            nama = VALUES(nama),
            nomor_kontrak = VALUES(nomor_kontrak),
            tanggal_sk = VALUES(tanggal_sk),
            tanggal_mulai = VALUES(tanggal_mulai),
            tanggal_selesai = VALUES(tanggal_selesai),
            organisasi_id = VALUES(organisasi_id),
            jabatan_id = VALUES(jabatan_id),
            is_latest = VALUES(is_latest),
            notes = VALUES(notes),
            is_deleted = VALUES(is_deleted),
            version = version + 1,
            created_by = VALUES(created_by)
    """

    with get_kepegawaian_connection_pool(autocommit=True) as connection:
        with connection.cursor() as cursor:
            cursor.executemany(query, data)
            affected = cursor.rowcount
            ic(affected, "row(s) affected")
            connection.commit()
