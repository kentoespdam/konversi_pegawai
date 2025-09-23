import pandas as pd

from core.config import save_update_kepegawaian


def update_organisasi_from_organization(df: pd.DataFrame):
    data = [(
        row.org_name,
        row.mail_code,
        row.category,
        row.is_deleted,
        row.org_id
    ) for row in df.itertuples(index=False)]

    query = """
            UPDATE organisasi
            SET nama=%s,
                short_name=%s,
                category=%s,
                is_deleted=%s
            WHERE id = %s \
            """

    save_update_kepegawaian(query, data)
