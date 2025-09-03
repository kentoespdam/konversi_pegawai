import sys
import os.path

sys.path.append(
    os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir))
)

from appwrite.client import Client
from appwrite.services.users import Users
from icecream import ic
import pandas as pd
from core.config import get_kepegawaian_connection_pool


client = Client()

(
    client.set_endpoint("http://192.168.230.254:82/v1")
    .set_project("65cd62cc3385d8434a53")
    .set_key(
        "061b4abb7743ecc570cc693483b36bc0f50616b2631c5f7cec3825e15cd196d703434b9c7d6a9bb0d44ef7d8ca9eb9d570a916c2e4867993b37fc29d9579278acdba9d2ad485eca0381e975aedf5f3217cf6653f4234265975c38186aa53ef572702a298e16576843d7dfd47cb77a649fff0f4460876c52b4c7d84c0b2c74706"
    )
)
users = Users(client)


def fetch_pegawai():
    query = """
        SELECT
            pegawai.id,
            pegawai.nipam,
            biodata.nama,
            pegawai.status_kerja
        FROM
            pegawai
            INNER JOIN biodata ON pegawai.nik = biodata.nik
        WHERE 
            pegawai.nipam NOT LIKE 'REC%'
    """
    with get_kepegawaian_connection_pool() as conn:
        with conn.cursor() as cursor:
            cursor.execute(query)
            return pd.DataFrame(cursor.fetchall())


def get_user(id: str):
    try:
        return users.get(f"{id}")
    except Exception:
        return None


def create_user(id: str, email: str, password: str, name: str):
    return users.create(user_id=f"{id}", email=email, password=password, name=name)


def update_email(id: str, email: str):
    users.update_email(id, email)


def update_prefrences(id: str, prefs: dict):
    users.update_prefs(id, prefs)


def update_status(id: str, status: bool):
    users.update_status(id, status)
    users.update_email_verification(id, status)


def main():
    df = fetch_pegawai()
    df["email"] = df["nipam"].swifter.apply(lambda x: f"{x}@perumdamts.com")
    df["password"] = "tirtasatria"
    for row in df.itertuples(index=False):
        exist_user = get_user(f"{row.id}")
        if exist_user:
            update_email(f"{row.id}", "{}@perumdamts.com".format(row.nipam))
            update_prefrences(
                f"{row.id}",
                {
                    "roles": ["USER", "ADMIN", "SYSTEM"]
                    if row.nipam == "900800456"
                    else ["USER"]
                },
            )
            update_status(f"{row.id}", False if row.status_kerja != 2 else True)
            ic(f"{row.nipam} updated")
            continue
        else:
            create_user(
                id=f"{row.id}",
                email=row.email,
                password=row.password,
                name=row.nama,
            )
            update_prefrences(
                f"{row.id}",
                {
                    "roles": ["USER", "ADMIN", "SYSTEM"]
                    if row.nipam == "900800456"
                    else ["USER"]
                },
            )
            update_status(f"{row.id}", False if row.status_kerja != 2 else True)
            ic(f"{row.nipam} created")
            continue


if __name__ == "__main__":
    main()
