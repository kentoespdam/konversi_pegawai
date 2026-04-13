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
            MAX(em.emp_code) AS emp_code,
            ep.emp_name, 
            ep.emp_identity_type, 
            ep.emp_identity_number
        FROM
            emp_profile AS ep
            INNER JOIN employee AS em ON ep.emp_profile_id = em.emp_profile_id
        WHERE
            (ep.emp_identity_number IS NULL OR ep.emp_identity_number = '')
        GROUP BY
            ep.emp_profile_id, ep.emp_name, ep.emp_identity_type, ep.emp_identity_number
    """
    try:
        with get_smartoffice_connection_pool() as conn:
            with conn.cursor() as cursor:
                cursor.execute(query)
                rows = cursor.fetchall()
                columns = [desc[0] for desc in cursor.description]
                return pd.DataFrame(rows, columns=columns)
    except Exception as e:
        LOGGER.error(f"Error fetching pegawai without NIK: {e}")
        return pd.DataFrame()


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
    try:
        with get_smartoffice_connection_pool() as conn:
            with conn.cursor() as cursor:
                cursor.execute(query, (tuple(emp_codes),))
                rows = cursor.fetchall()
                columns = [desc[0] for desc in cursor.description]
                return pd.DataFrame(rows, columns=columns)
    except Exception as e:
        LOGGER.error(f"Error fetching emp_cards: {e}")
        return pd.DataFrame(columns=["ei_id", "emp_code", "ei_type", "ei_number"])


# ... existing code ...
def update_nik_emp_profile(pegawai_df: pd.DataFrame):
    """
    Bulk update emp_profile with emp_identity_number and emp_identity_type
    using emp_profile_id from the provided DataFrame.
    """
    if pegawai_df.empty:
        LOGGER.info("No rows to update.")
        return

    data_list = []
    skipped_count = 0
    for row in pegawai_df.itertuples(index=False):
        print(f"DEBUG ROW: {row}")
        # Bug 4: Validation
        if pd.isna(row.emp_identity_number) or not str(row.emp_identity_number).strip():
            skipped_count += 1
            continue
        
        # Bug 5: Ensure correct types
        data_list.append((
            str(row.emp_identity_number),
            int(row.emp_identity_type),
            row.emp_profile_id
        ))

    if skipped_count > 0:
        print(f"DEBUG: skipped_count={skipped_count}")
        LOGGER.warning(f"Skipped {skipped_count} rows due to empty NIK.")

    if not data_list:
        LOGGER.info("No valid rows to update after validation.")
        return

    sql = """
        UPDATE emp_profile SET
            emp_identity_number=%s,
            emp_identity_type=%s
        WHERE emp_profile_id=%s
    """
    try:
        with get_smartoffice_connection_pool() as conn:
            with conn.cursor() as cursor:
                cursor.executemany(sql, data_list)
                LOGGER.info("%s row(s) updated in emp_profile", cursor.rowcount)
                conn.commit()
    except Exception as e:
        LOGGER.error(f"Error updating NIK in emp_profile: {e}")
        # Rollback is automatically handled by some context managers, but being explicit is safer if needed.
        # However, get_smartoffice_connection_pool context manager might not rollback on its own.
        # If it returns a raw connection, we should rollback.


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
        
        initial_count = len(self.emp_without_nik)
        LOGGER.info(f"Found {initial_count} employees without NIK.")
        
        self.emp_codes = self.emp_without_nik["emp_code"].tolist()
        self.emp_cards = fetch_emp_cards_by_emp_codes(self.emp_codes)

        self._cleanup_nik_from_emp_card()
        
        # Bug 6: Better logging
        from_card = self.emp_without_nik[self.emp_without_nik["_source"] == "card"].shape[0]
        from_fallback = self.emp_without_nik[self.emp_without_nik["_source"] == "fallback"].shape[0]
        
        LOGGER.info(f"Cleanup finished. Matched from cards: {from_card}, Fallback to emp_code: {from_fallback}")
        
        update_nik_emp_profile(self.emp_without_nik)

    def _cleanup_nik_from_emp_card(self):
        # Initialize source column for logging
        self.emp_without_nik["_source"] = "none"
        
        for idx, row in self.emp_without_nik.iterrows():
            emp_code = row["emp_code"]
            # Bug 2: Safe filtering instead of .query() with f-string
            ec_list = self.emp_cards[self.emp_cards["emp_code"] == emp_code]
            
            if ec_list.empty:
                self.emp_without_nik.loc[idx, "emp_identity_number"] = emp_code
                self.emp_without_nik.loc[idx, "emp_identity_type"] = KTP_IDENTITY_TYPE
                self.emp_without_nik.loc[idx, "_source"] = "fallback"
                continue
            
            ec_ktp = ec_list[ec_list["ei_type"] == KTP_IDENTITY_TYPE]
            if ec_ktp.empty:
                self.emp_without_nik.loc[idx, "emp_identity_number"] = emp_code
                self.emp_without_nik.loc[idx, "emp_identity_type"] = KTP_IDENTITY_TYPE
                self.emp_without_nik.loc[idx, "_source"] = "fallback"
                continue
                
            self.emp_without_nik.loc[idx, "emp_identity_number"] = ec_ktp["ei_number"].values[0]
            self.emp_without_nik.loc[idx, "emp_identity_type"] = KTP_IDENTITY_TYPE
            self.emp_without_nik.loc[idx, "_source"] = "card"

if __name__ == "__main__":
    CleanupNikEmpProfile().run()