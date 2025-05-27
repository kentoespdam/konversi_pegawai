import icecream
from config import get_kepegawaian_connection_pool
import pandas as pd
from icecream import ic

from core.enums import EJenisSk


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
        row.tmt_mutasi,
        row.tmt_jabatan,
        row.tmt_golongan,
        row.tmt_kerja,
        row.tanggal_pengangkatan,
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
        0,
        'SYSTEM'
    ) for row in df.itertuples(index=False)]

    query = """
        REPLACE INTO pegawai (
            id, nipam, nik, status_pegawai, organisasi_id,
            jabatan_id, profesi_id, golongan_id, grade_id, status_kerja,
            tmt_mutasi, tmt_jabatan, tmt_golongan, tmt_kerja, tanggal_pengangkatan,
            tmt_pensiun, gaji_profil_id, gaji_pendapatan_non_pajak_id, rumah_dinas_id, gaji_pokok,
            is_askes, phdp, jml_tanggungan, mkg_tahun, mkg_bulan,
            notes, version, created_by
        ) VALUES (
            %s, %s, %s, %s, %s,
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


def update_sk_pegawai(df: pd.DataFrame, jenis_sk: EJenisSk):
    data = [(
        row.id,
        row.pegawai_id
    ) if jenis_sk == EJenisSk.SK_CAPEG else (row.id, row.tmt_berlaku, row.pegawai_id) for row in df.itertuples(index=False)]

    query = _generate_query_sk_capeg(jenis_sk)
    if query is None:
        return

    try:
        with get_kepegawaian_connection_pool(autocommit=True) as connection:
            with connection.cursor() as cursor:
                cursor.executemany(query, data)
                affected = cursor.rowcount
                ic(affected, "row(s) affected")
                connection.commit()
    except Exception as e:
        ic(e)
        raise e


def _generate_query_sk_capeg(jenis_sk: EJenisSk):
    if (jenis_sk == EJenisSk.SK_CAPEG):
        return "UPDATE pegawai SET ref_sk_capeg_id=%s WHERE id=%s"
    elif (jenis_sk == EJenisSk.SK_KENAIKAN_GAJI_BERKALA):
        return "UPDATE pegawai SET ref_sk_gaji_berkala_id=%s, tmt_gaji_berkala=%s WHERE id=%s"
    elif (jenis_sk == EJenisSk.SK_KENAIKAN_PANGKAT_GOLONGAN):
        return "UPDATE pegawai SET ref_sk_gol_id=%s, tmt_golongan=%s WHERE id=%s"
    elif (jenis_sk == EJenisSk.SK_JABATAN):
        return "UPDATE pegawai SET ref_sk_jabatan_id=%s, tmt_jabatan=%s WHERE id=%s"
    elif (jenis_sk == EJenisSk.SK_MUTASI):
        return "UPDATE pegawai SET ref_sk_mutasi_id=%s, tmt_mutasi=%s WHERE id=%s"
    elif (jenis_sk == EJenisSk.SK_PEGAWAI_TETAP):
        return "UPDATE pegawai SET ref_sk_pegawai_id=%s, tmt_pegawai=%s WHERE id=%s"
    else:
        return None
