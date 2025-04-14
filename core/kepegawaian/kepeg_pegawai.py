import icecream
from config import get_kepegawaian_connection_pool
import pandas as pd
from icecream import ic


def update_pegawai_phdp(salary_rows: list) -> None:
    """Update PHDP and rumah dinas ID in pegawai table."""

    query = """UPDATE pegawai SET
               gaji_profil_id=%s,
               phdp=%s,
               rumah_dinas_id=%s
               WHERE nipam=%s
    """
    data = [
        (row["gajiProfilId"],
         row["phdp"] or 0,
         row["rumahDinasId"] if row["rumahDinasId"] > 0 else None,
         row["nipam"])
        for row in salary_rows
    ]
    try:
        with get_kepegawaian_connection_pool(autocommit=True) as connection:
            with connection.cursor() as cursor:
                cursor.executemany(query, data)
                affected = cursor.rowcount
                icecream.ic(affected, "row(s) affected")
    except Exception as e:
        raise e


def fetch_all_pegawai():
    query = """
        SELECT
            pegawai.id, 
            pegawai.absensi_id, 
            pegawai.gaji_pokok, 
            pegawai.is_askes, 
            pegawai.jml_tanggungan, 
            pegawai.mkg_bulan, 
            pegawai.mkg_tahun, 
            pegawai.nipam, 
            pegawai.notes, 
            pegawai.phdp, 
            pegawai.ref_sk_capeg_id, 
            pegawai.ref_sk_gol_id, 
            pegawai.ref_sk_jabatan_id, 
            pegawai.ref_sk_mutasi_id, 
            pegawai.ref_sk_pegawai_id, 
            pegawai.status_kerja, 
            pegawai.status_pegawai, 
            pegawai.tmt_golongan, 
            pegawai.tmt_jabatan, 
            pegawai.tmt_kerja, 
            pegawai.tmt_mutasi, 
            pegawai.tmt_pegawai, 
            pegawai.tmt_pensiun, 
            pegawai.nik, 
            pegawai.gaji_profil_id, 
            pegawai.golongan_id, 
            pegawai.grade_id, 
            pegawai.jabatan_id, 
            pegawai.gaji_pendapatan_non_pajak_id, 
            pegawai.organisasi_id, 
            pegawai.profesi_id, 
            pegawai.rumah_dinas_id
        FROM
            pegawai
        WHERE 
            pegawai.is_deleted = FALSE
        """

    with get_kepegawaian_connection_pool() as connection:
        with connection.cursor() as cursor:
            cursor.execute(query)
            return cursor.fetchall()


def save_pegawai_from_employee(df: pd.DataFrame):
    data = [(
        row.pegawai_id,
        row.nipam,
        row.nik,
        row.status_pegawai,
        row.organisasi_id if row.organisasi_id > 0 else None,
        row.jabatan_id if row.jabatan_id > 0 else None,
        row.profesi_id if row.profesi_id > 0 else None,
        row.golongan_id if row.golongan_id > 0 else None,
        row.grade_id if row.grade_id > 0 else None,
        row.status_kerja,
        row.tmt_kerja,
        row.tmt_pensiun,
        row.gaji_profil_id if row.gaji_profil_id > 0 else None,
        row.gaji_pendapatan_non_pajak_id if row.gaji_pendapatan_non_pajak_id > 0 else None,
        row.rumah_dinas_id if row.rumah_dinas_id > 0 else None,
        row.gaji_pokok,
        row.is_askes,
        row.phdp,
        row.jml_tanggungan,
        row.mkg_tahun,
        row.mkg_bulan,
        row.notes,
        'SYSTEM'
    ) for row in df.itertuples(index=False)]

    query = """
        INSERT INTO pegawai (
            id, nipam, nik, status_pegawai, organisasi_id, 
            jabatan_id, profesi_id, golongan_id, grade_id, status_kerja, 
            tmt_kerja, tmt_pensiun, gaji_profil_id, gaji_pendapatan_non_pajak_id, rumah_dinas_id, 
            gaji_pokok, is_askes, phdp, jml_tanggungan, mkg_tahun, 
            mkg_bulan, notes, created_by
        ) VALUES (
            %s, %s, %s, %s, %s,
            %s, %s, %s, %s, %s,
            %s, %s, %s, %s, %s,
            %s, %s, %s, %s, %s,
            %s, %s, %s
        )
    """

    try:
        with get_kepegawaian_connection_pool(autocommit=True) as connection:
            with connection.cursor() as cursor:
                cursor.executemany(query, data)
                affected = cursor.rowcount
                icecream.ic(affected, "row(s) affected")
                connection.commit()
    except Exception as e:
        ic(e)
        raise e
