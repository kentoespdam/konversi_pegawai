import pandas as pd
from icecream import ic
from config import get_kepegawaian_connection_pool


def save_biodata_from_emp_profile(df: pd.DataFrame):
    list = [(
        row.nik,
        row.nama,
        row.jenis_kelamin,
        row.tempat_lahir,
        row.tanggal_lahir,
        row.alamat,
        row.telp,
        row.agama,
        row.ibu_kandung,
        row.pendidikan_id,
        row.golongan_darah,
        row.status_kawin,
        row.notes,
        row.is_pegawai,
        row.is_deleted,
        'SYSTEM'
    ) for row in df.itertuples(index=False)]

    query = """
    INSERT INTO biodata (
        nik, nama, jenis_kelamin, tempat_lahir, tanggal_lahir,
        alamat, telp, agama, ibu_kandung, pendidikan_id,
        golongan_darah, status_kawin, notes, is_pegawai, is_deleted, 
        created_by
    ) VALUES (
        %s, %s, %s, %s, %s, 
        %s, %s, %s, %s, %s,
        %s, %s, %s, %s, %s, 
        %s
    )
    """

    with get_kepegawaian_connection_pool(autocommit=True) as connection:
        with connection.cursor() as cursor:
            cursor.executemany(query, list)
            ic(cursor.rowcount, "row(s) affected")
            connection.commit()
