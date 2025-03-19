import icecream
from config import get_kepegawaian_connection_pool


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
