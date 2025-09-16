import pandas as pd

from core.config import save_update_kepegawaian


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
    ) for row in df.itertuples(index=False)]

    query = """
            INSERT INTO pengalaman_kerja (biodata_id, nama_perusahaan, type_perusahaan, jabatan, lokasi,
                                          tahun_masuk, tahun_keluar, notes, is_deleted, version,
                                          created_by)
            VALUES (%s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s,
                    %s)
            ON DUPLICATE KEY UPDATE biodata_id=VALUES(biodata_id),
                                    nama_perusahaan=VALUES(nama_perusahaan),
                                    type_perusahaan=VALUES(type_perusahaan),
                                    jabatan=VALUES(jabatan),
                                    lokasi=VALUES(lokasi),
                                    tahun_masuk=VALUES(tahun_masuk),
                                    tahun_keluar=VALUES(tahun_keluar),
                                    notes=VALUES(notes),
                                    is_deleted=VALUES(is_deleted)
            """

    save_update_kepegawaian(query, data)
