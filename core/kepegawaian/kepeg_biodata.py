import pandas as pd

from core.config import save_update_kepegawaian, fetch_kepegawaian
from core.enums import EStatusPegawai


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
            INSERT INTO biodata (nik, nama, jenis_kelamin, tempat_lahir, tanggal_lahir,
                                 alamat, telp, agama, ibu_kandung, pendidikan_id,
                                 golongan_darah, status_kawin, notes, is_pegawai, is_deleted,
                                 version, created_by)
            VALUES (%s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s,
                    %s, %s)
            ON DUPLICATE KEY UPDATE nik=VALUES(nik),
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
                                    is_deleted=VALUES(is_deleted) \
            """

    save_update_kepegawaian(query, data_list)


def fetch_biodata_for_riwayat_kontrak() -> pd.DataFrame:
    query = """
            SELECT peg.id,
                   bio.nik,
                   bio.nama,
                   peg.status_kerja,
                   peg.status_pegawai
            FROM biodata AS bio
                     INNER JOIN pegawai AS peg ON bio.nik = peg.nik
            WHERE peg.status_pegawai < %s
            ORDER BY bio.nik \
            """
    where = (EStatusPegawai.NON_PEGAWAI.value,)
    return fetch_kepegawaian(query, where)
