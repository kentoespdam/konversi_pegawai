import pandas as pd
from icecream import ic

from core.config import get_kepegawaian_connection_pool


def save_riwayat_mutasi_from_emp_work_history(df: pd.DataFrame):
    data = [(
        row.pegawai_id,
        row.nipam,
        row.nama,
        row.riwayat_sk_id,
        row.tmt_berlaku,
        row.tanggal_berakhir,
        row.jenis_mutasi,
        row.organisasi_id if row.organisasi_id > 0 else None,
        row.nama_organisasi,
        row.jabatan_id if row.jabatan_id > 0 else None,
        row.nama_jabatan,
        row.profesi_id if row.profesi_id > 0 else None,
        row.nama_profesi,
        row.golongan_id if row.golongan_id > 0 else None,
        row.nama_golongan,
        row.organisasi_lama_id if row.organisasi_lama_id > 0 else None,
        row.nama_organisasi_lama,
        row.jabatan_lama_id if row.jabatan_lama_id > 0 else None,
        row.nama_jabatan_lama,
        row.profesi_lama_id if row.profesi_lama_id > 0 else None,
        row.nama_profesi_lama,
        row.is_deleted,
        row.notes,
        0,
        'SYSTEM'
    ) for row in df.itertuples(index=False)]
    query = """
        INSERT INTO riwayat_mutasi (
            pegawai_id, nipam, nama, riwayat_sk_id, tmt_berlaku, 
            tanggal_berakhir, jenis_mutasi, organisasi_id, nama_organisasi, jabatan_id, 
            nama_jabatan, profesi_id, nama_profesi, golongan_id, nama_golongan, 
            organisasi_lama_id, nama_organisasi_lama, jabatan_lama_id, nama_jabatan_lama, profesi_lama_id, 
            nama_profesi_lama, is_deleted, notes, version, created_by
        ) VALUES (
            %s, %s, %s, %s, %s, 
            %s, %s, %s, %s, %s, 
            %s, %s, %s, %s, %s,
            %s, %s, %s, %s, %s,
            %s, %s, %s, %s, %s
        )
    """
    with get_kepegawaian_connection_pool(autocommit=True) as connection:
        with connection.cursor() as cursor:
            try:
                cursor.executemany(query, data)
                affected = cursor.rowcount
                ic(affected, "row(s) affected")
                connection.commit()
            except Exception as e:
                ic(e)
                connection.rollback()
