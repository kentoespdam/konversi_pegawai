from config import get_smartoffice_connection_pool
import pandas as pd
from icecream import ic


def fetch_pegawai_without_nik():
    query = """
        SELECT
            ep.emp_profile_id, 
            em.emp_code,
            ep.emp_name, 
            ep.emp_identity_type, 
            ep.emp_identity_number
        FROM
            emp_profile AS ep
            INNER JOIN
            employee AS em
            ON 
                ep.emp_profile_id = em.emp_profile_id
        WHERE
            ep.emp_identity_number IS NULL
    """
    with get_smartoffice_connection_pool() as conn:
        with conn.cursor() as cursor:
            cursor.execute(query)
            return pd.DataFrame(cursor.fetchall())


def fetch_emp_card_by_nipam_in(nipam: list):
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
            cursor.execute(query, (tuple(nipam),))
            return pd.DataFrame(cursor.fetchall())


def main():
    pwn = fetch_pegawai_without_nik()
    list_nipam = pwn["emp_code"].to_list()
    ec_df = fetch_emp_card_by_nipam_in(list_nipam)
    pwn = set_nik_in_pegawai_without_nik(pwn, ec_df)
    update_nik_emp_profile(pwn)
    # ic(pwn.to_dict(orient="records"))
    # ic(ec_df["ei_id"].size)


def set_nik_in_pegawai_without_nik(pegawai_df: pd.DataFrame, emp_card_df: pd.DataFrame) -> pd.DataFrame:
    """Set NIK on pegawai without NIK from emp_card"""
    for idx, row in pegawai_df.iterrows():
        emp_code = row["emp_code"]
        ec_list = emp_card_df.query(f"emp_code == '{emp_code}'")
        if ec_list.empty:
            pegawai_df.at[idx, "emp_identity_number"] = emp_code
            pegawai_df.at[idx, "emp_identity_type"] = 4
            continue
        ec_ktp = ec_list.query(f"ei_type == 4")
        if ec_ktp.empty:
            pegawai_df.at[idx, "emp_identity_number"] = emp_code
            pegawai_df.at[idx, "emp_identity_type"] = 4
            continue
        pegawai_df.at[idx,
                      "emp_identity_number"] = ec_ktp["ei_number"].values[0]
        pegawai_df.at[idx, "emp_identity_type"] = 4
    return pegawai_df


def update_nik_emp_profile(pegawai_df: pd.DataFrame):
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
            ic(cursor.rowcount, "row(s) affected")
            conn.commit()


if __name__ == "__main__":
    main()
