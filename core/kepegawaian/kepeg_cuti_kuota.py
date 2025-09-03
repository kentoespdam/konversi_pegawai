import pandas as pd
from icecream import ic

from core.config import get_kepegawaian_connection_pool


def save_cuti_kuota(df: pd.DataFrame):
    data_list=[(
        row.id,
        row.pegawai_id,
        row.tahun,
        row.kuota,
        row.kuota_terpakai,
        0,
        row.sisa_kuota,
        row.expired,
        False,
        'SYSTEM'
    ) for row in df.itertuples(index=False)]
    query = """
            INSERT INTO cuti_kuota (id, pegawai_id, tahun, kuota, kuota_terpakai,
                                    kuota_tambahan, sisa_kuota, expired, is_deleted, created_by)
            VALUES (%s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE pegawai_id=VALUES(pegawai_id),
                                    tahun=VALUES(tahun),
                                    kuota=VALUES(kuota),
                                    kuota_terpakai=VALUES(kuota_terpakai),
                                    kuota_tambahan=VALUES(kuota_tambahan),
                                    sisa_kuota=VALUES(sisa_kuota),
                                    expired=VALUES(expired),
                                    is_deleted=VALUES(is_deleted)
            """
    with get_kepegawaian_connection_pool(autocommit=True) as connection:
        with connection.cursor() as cursor:
            cursor.executemany(query, data_list)
            affected = cursor.rowcount
            ic(affected, "row(s) affected")
            connection.commit()
