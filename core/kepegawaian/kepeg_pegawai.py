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
