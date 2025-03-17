from config import get_kepegawaian_connection_pool


def fetch_pendidikan_pegawai(biodataId: str = None):
    query = """
        SELECT
            pendidikan.biodata_id,
            pendidikan.id,
            pendidikan.jenjang_id,
            pendidikan.gelar_depan,
            pendidikan.gelar_belakang,
            pendidikan.jurusan,
            pendidikan.institusi,
            pendidikan.kota,
            pendidikan.tahun_masuk,
            pendidikan.tahun_lulus,
            pendidikan.gpa,
            pendidikan.is_latest 
        FROM
            pendidikan
    """
    params = None
    if biodataId is not None:
        query += " WHERE pendidikan.biodata_id = %s"
        params = (biodataId,)
    with get_kepegawaian_connection_pool() as conn:
        with conn.cursor() as cursor:
            cursor.execute(query, params)
            return cursor.fetchall()
