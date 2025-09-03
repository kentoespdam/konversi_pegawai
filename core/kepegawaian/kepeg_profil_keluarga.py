import pandas as pd
from icecream import ic
from core.config import get_kepegawaian_connection_pool


def save_profil_keluarga_from_emp_profile(df: pd.DataFrame):
    data = [(
        row.biodata_id,
        row.nama,
        row.jenis_kelamin,
        row.agama,
        row.hubungan_keluarga,
        row.tempat_lahir,
        row.tanggal_lahir,
        row.tanggungan,
        row.status_pendidikan,
        row.status_kawin,
        row.notes,
        row.is_deleted,
        0, 
        'SYSTEM'
    )for row in df.itertuples(index=False)]

    query = """
        INSERT INTO profil_keluarga (
            biodata_id, nama, jenis_kelamin, agama, hubungan_keluarga, 
            tempat_lahir, tanggal_lahir, tanggungan, status_pendidikan, status_kawin, 
            notes, is_deleted, version, created_by
        ) VALUES (
            %s, %s, %s, %s, %s,
            %s, %s, %s, %s, %s, 
            %s, %s, %s, %s
        )
        ON DUPLICATE KEY UPDATE 
        biodata_id=VALUES(biodata_id),
        nama=VALUES(nama),
        jenis_kelamin=VALUES(jenis_kelamin),
        agama=VALUES(agama),
        hubungan_keluarga=VALUES(hubungan_keluarga),
        tempat_lahir=VALUES(tempat_lahir),
        tanggal_lahir=VALUES(tanggal_lahir),
        tanggungan=VALUES(tanggungan),
        status_pendidikan=VALUES(status_pendidikan),
        status_kawin=VALUES(status_kawin),
        notes=VALUES(notes),
        is_deleted=VALUES(is_deleted)
    """

    with get_kepegawaian_connection_pool(autocommit=True) as connection:
        cursor = connection.cursor()
        cursor.executemany(query, data)
        affected = cursor.rowcount
        ic(affected, "row(s) affected")
        connection.commit()
