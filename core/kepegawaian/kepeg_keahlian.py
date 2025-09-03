import pandas as pd
from icecream import ic
from core.config import get_kepegawaian_connection_pool


def save_keahlian_from_emp_skill(df: pd.DataFrame):
    data = [(
        row.biodata_id,
        row.jenis_keahlian_id if row.jenis_keahlian_id > 0 else None,
        row.kualifikasi,
        row.sertifikasi,
        row.institusi,
        row.tahun,
        True,
        row.tanggal_pengajuan,
        row.tanggal_disetujui,
        row.is_deleted,
        0,
        'SYSTEM'
    )for row in df.itertuples(index=False)]

    query = """
        INSERT INTO keahlian (
            biodata_id, jenis_keahlian_id, kualifikasi, sertifikasi, institusi, 
            tahun, disetujui, tanggal_pengajuan, tanggal_disetujui, is_deleted, 
            version, created_by
        ) VALUES (
            %s, %s, %s, %s, %s, 
            %s, %s, %s, %s, %s, 
            %s, %s
        ) ON DUPLICATE KEY UPDATE biodata_id=VALUES(biodata_id)
    """

    try:
        with get_kepegawaian_connection_pool(autocommit=True) as connection:
            with connection.cursor() as cursor:
                cursor.executemany(query, data)
                affected = cursor.rowcount
                ic(affected, "row(s) affected")
                connection.commit()
    except Exception as e:
        ic(e)
        raise e
