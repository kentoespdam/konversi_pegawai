import pandas as pd

from core.config import get_smartoffice_connection_pool


def fetch_maks_potongan():
    query = "SELECT text AS kode, num_1 AS nominal FROM sys_reference WHERE status=%s AND `code`=%s"
    with get_smartoffice_connection_pool() as conn:
        with conn.cursor() as cursor:
            cursor.execute(query, ("Enable", "payroll"))
            columns = [col[0] for col in cursor.description] if cursor.description else None
            result = cursor.fetchall()
            return pd.DataFrame(result, columns=columns)
