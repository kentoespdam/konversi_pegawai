from core.config import get_kepegawaian_connection_pool
import pandas as pd
from icecream import ic


def save_pengalaman_kerja_from_emp_work_experience(df: pd.DataFrame):
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
        0,
        'SYSTEM'
    )for row in df.itertuples(index=False)]

    query = """
        INSERT INTO pengalaman_kerja (
            biodata_id, nama_perusahaan, type_perusahaan, jabatan, lokasi, 
            tahun_masuk, tahun_keluar, notes, is_deleted, version, 
            created_by
        ) VALUES (
            %s, %s, %s, %s, %s, 
            %s, %s, %s, %s, %s,
            %s
        )
    """

    with get_kepegawaian_connection_pool(autocommit=True) as connection:
        with connection.cursor() as cursor:
            cursor.executemany(query, data)
            affected = cursor.rowcount
            ic(affected, "row(s) affected")
            connection.commit()
