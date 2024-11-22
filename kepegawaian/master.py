import pandas as pd
from core.koneksi import engine_kepegawaian
from icecream import ic


def find_jabatan_id(nama):
    sql = """
        SELECT id FROM jabatan WHERE nama = %s
    """
    result = pd.read_sql_query(sql, engine_kepegawaian.connect(), params=(nama,))
    if result is None:
        ic(nama)
        return 0
    return result["id"].values[0]


def find_organisasi_id(nama):
    sql = """
        SELECT id FROM organisasi WHERE nama = %s
    """
    result = pd.read_sql_query(sql, engine_kepegawaian.connect(), params=(nama,))
    return result["id"].values[0] if len(result) > 0 else None


def find_golongan_id(golongan_pangkat: str) -> int | None:
    if golongan_pangkat is None:
        return None

    arr = golongan_pangkat.split("-")
    golongan = arr[0]
    pangkat = arr[1]
    sql = """
        SELECT id FROM golongan WHERE (pangkat, golongan) = (%s, %s)
    """
    result = pd.read_sql_query(
        sql,
        engine_kepegawaian.connect(),
        params=(
            pangkat,
            golongan,
        ),
    )
    return result["id"].values[0]
