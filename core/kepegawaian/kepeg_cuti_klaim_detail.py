import pandas as pd

from core.config import save_update_kepegawaian


def save_cuti_klaim_detail(df: pd.DataFrame):
    data_list = [(
        row.id,
        row.tanggal,
        row.ref_cuti_id
    ) for row in df.itertuples(index=False)]

    query = """
            INSERT INTO cuti_klaim_detail (id, tanggal, ref_cuti_id)
            VALUES (%s, %s, %s) \
            """

    save_update_kepegawaian(query, data_list)
