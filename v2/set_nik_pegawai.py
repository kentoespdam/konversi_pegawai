import pandas as pd

from core.config import get_smartoffice_connection_pool, LOGGER

# Constants
KTP_IDENTITY_TYPE = 4


def fetch_pegawai_without_nik() -> pd.DataFrame:
    """
    Fetch employees (pegawai) whose emp_identity_number (NIK) is NULL.
    Returns a DataFrame with columns:
    emp_profile_id, emp_code, emp_name, emp_identity_type, emp_identity_number
    """
    query = """
        SELECT
            ep.emp_profile_id, 
            em.emp_code,
            ep.emp_name, 
            ep.emp_identity_type, 
            ep.emp_identity_number
        FROM
            emp_profile AS ep
            INNER JOIN employee AS em ON ep.emp_profile_id = em.emp_profile_id
        WHERE
            ep.emp_identity_number IS NULL OR ep.emp_identity_number = ''
        GROUP BY
            ep.emp_profile_id
    """
    with get_smartoffice_connection_pool() as conn:
        with conn.cursor() as cursor:
            cursor.execute(query)
            rows = cursor.fetchall()
            columns = [desc[0] for desc in cursor.description]
            return pd.DataFrame(rows, columns=columns)


# ... existing code ...
def fetch_emp_cards_by_emp_codes(emp_codes: list[str]) -> pd.DataFrame:
    """
    Fetch emp_card rows for the given employee codes.
    Returns a DataFrame with columns: ei_id, emp_code, ei_type, ei_number.
    """
    if not emp_codes:
        return pd.DataFrame(columns=["ei_id", "emp_code", "ei_type", "ei_number"])
    query = """
        SELECT
            ec.ei_id,
            ec.emp_code, 
            ec.ei_type, 
            ec.ei_number
        FROM
            emp_card AS ec
        WHERE
            ec.emp_code IN %s
        """
    with get_smartoffice_connection_pool() as conn:
        with conn.cursor() as cursor:
            cursor.execute(query, (tuple(emp_codes),))
            rows = cursor.fetchall()
            columns = [desc[0] for desc in cursor.description]
            return pd.DataFrame(rows, columns=columns)


# ... existing code ...
def update_nik_emp_profile(pegawai_df: pd.DataFrame):
    """
    Bulk update emp_profile with emp_identity_number and emp_identity_type
    using emp_profile_id from the provided DataFrame.
    """
    if pegawai_df.empty:
        LOGGER.info("No rows to update.")
        return

    data_list = [(
        row.emp_identity_number,
        row.emp_identity_type,
        row.emp_profile_id
    ) for row in pegawai_df.itertuples(index=False)]

    sql = """
        UPDATE emp_profile SET
            emp_identity_number=%s,
            emp_identity_type=%s
        WHERE emp_profile_id=%s
    """
    with get_smartoffice_connection_pool() as conn:
        with conn.cursor() as cursor:
            cursor.executemany(sql, data_list)
            LOGGER.info("%s row(s) affected", cursor.rowcount)
            conn.commit()


class CleanupNikEmpProfile:
    def __init__(self):
        self.emp_without_nik = pd.DataFrame()
        self.emp_codes = []
        self.emp_cards = pd.DataFrame()

    def run(self):
        self.emp_without_nik = fetch_pegawai_without_nik()
        if self.emp_without_nik.empty:
            LOGGER.info("No employees without NIK found.")
            return
        LOGGER.info(f"Found {self.emp_without_nik['emp_profile_id'].size} without NIK")
        self.emp_codes = self.emp_without_nik["emp_code"].tolist()
        self.emp_cards = fetch_emp_cards_by_emp_codes(self.emp_codes)

        self._cleanup_nik_from_emp_card()
        LOGGER.info(f"Found {self.emp_without_nik['emp_profile_id'].size} with NIK")
        LOGGER.info(self.emp_without_nik.head().to_dict("records"))
        update_nik_emp_profile(self.emp_without_nik)

    def _cleanup_nik_from_emp_card(self):
        for idx, row in self.emp_without_nik.iterrows():
            emp_code = row["emp_code"]
            ec_list = self.emp_cards.query(f"emp_code == '{emp_code}'")
            if ec_list.empty:
                self.emp_without_nik.loc[idx, "emp_identity_number"] = emp_code
                self.emp_without_nik.loc[idx, "emp_identity_type"] = KTP_IDENTITY_TYPE
                continue
            ec_ktp = ec_list.query(f"ei_type == {KTP_IDENTITY_TYPE}")
            if ec_ktp.empty:
                self.emp_without_nik.loc[idx, "emp_identity_number"] = emp_code
                self.emp_without_nik.loc[idx, "emp_identity_type"] = KTP_IDENTITY_TYPE
                continue
            self.emp_without_nik.loc[idx, "emp_identity_number"] = ec_ktp["ei_number"].values[0]
            self.emp_without_nik.loc[idx, "emp_identity_type"] = KTP_IDENTITY_TYPE

if __name__ == "__main__":
    CleanupNikEmpProfile().run()