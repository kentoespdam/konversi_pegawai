import pandas as pd
from icecream import ic
from core.config import get_kepegawaian_connection_pool, LOGGER


def save_biodata_from_emp_profile(df: pd.DataFrame):
    data_list = [(
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
        0,
        'SYSTEM'
    ) for row in df.itertuples(index=False)]

    query = """
    INSERT INTO biodata (
        nik, nama, jenis_kelamin, tempat_lahir, tanggal_lahir,
        alamat, telp, agama, ibu_kandung, pendidikan_id,
        golongan_darah, status_kawin, notes, is_pegawai, is_deleted, 
        version, created_by
    ) VALUES (
        %s, %s, %s, %s, %s, 
        %s, %s, %s, %s, %s,
        %s, %s, %s, %s, %s, 
        %s, %s
    ) ON DUPLICATE KEY UPDATE 
        nik=VALUES(nik),
        nama=VALUES(nama),
        jenis_kelamin=VALUES(jenis_kelamin),
        tempat_lahir=VALUES(tempat_lahir),
        tanggal_lahir=VALUES(tanggal_lahir),
        alamat=VALUES(alamat),
        telp=VALUES(telp),
        agama=VALUES(agama),
        ibu_kandung=VALUES(ibu_kandung),
        pendidikan_id=VALUES(pendidikan_id),
        golongan_darah=VALUES(golongan_darah),
        status_kawin=VALUES(status_kawin),
        notes=VALUES(notes),
        is_pegawai=VALUES(is_pegawai),
        is_deleted=VALUES(is_deleted)
    """

    with get_kepegawaian_connection_pool(autocommit=True) as connection:
        with connection.cursor() as cursor:
            try:
                cursor.executemany(query, data_list)
                LOGGER.info(f"{cursor.rowcount} row(s) affected")
                connection.commit()
            except Exception as e:
                LOGGER.error(e)
                raise e


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
