import pandas as pd

from core.config import get_smartoffice_connection_pool


def fetch_tkk_reduction():
    query = """
        SELECT
            stkkr.id, 
            stkkr.emp_flag AS status_pegawai, 
            stkkr.pos_level AS level_id, 
            stkkr.golongan AS golongan_id, 
            stkkr.potongan AS nominal
        FROM
            salary_tkk_reduction AS stkkr
    """
    with get_smartoffice_connection_pool() as conn:
        with conn.cursor() as cursor:
            cursor.execute(query)
            columns = [col[0] for col in cursor.description] if cursor.description else None
            rows = cursor.fetchall()
            return pd.DataFrame(rows, columns=columns)
