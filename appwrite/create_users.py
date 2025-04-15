import swifter
from config import get_kepegawaian_connection_pool
import pandas as pd
from icecream import ic
from appwrite.services.users import Users
from appwrite.client import Client
import sys
import os.path
sys.path.append(
    os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir)))

client = Client()

(
    client
    .set_endpoint("http://192.168.230.254:82/v1")
    .set_project("65cd62cc3385d8434a53")
    .set_key("061b4abb7743ecc570cc693483b36bc0f50616b2631c5f7cec3825e15cd196d703434b9c7d6a9bb0d44ef7d8ca9eb9d570a916c2e4867993b37fc29d9579278acdba9d2ad485eca0381e975aedf5f3217cf6653f4234265975c38186aa53ef572702a298e16576843d7dfd47cb77a649fff0f4460876c52b4c7d84c0b2c74706")
)
users = Users(client)


def fetch_pegawai():
    query = """
        SELECT
        pegawai.id,
        pegawai.nipam,
        biodata.nama 
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


def main():
    df = fetch_pegawai()
    df["email"] = df["nipam"].swifter.apply(lambda x: f"{x}@perumdamts.com")
    df["password"] = "tirtasatria"
    for row in df.itertuples(index=False):
        users.create(
            user_id=f"{row.id}",
            email=row.email,
            password=row.password,
            name=row.nama)


if __name__ == "__main__":
    main()
