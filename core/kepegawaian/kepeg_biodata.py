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


def fetch_biodata_for_riwayat_kontrak():
    query = """
        SELECT
            peg.id,
            bio.nik,
            bio.nama,
            peg.status_kerja,
            peg.status_pegawai 
        FROM
            biodata AS bio
            INNER JOIN pegawai AS peg ON bio.nik = peg.nik 
        WHERE
            peg.status_pegawai < 5 
        ORDER BY
            bio.nik
    """
    with get_kepegawaian_connection_pool() as connection:
        with connection.cursor() as cursor:
            cursor.execute(query)
            return cursor.fetchall()
