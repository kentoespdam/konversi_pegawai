from unittest import TestCase
from appwrite.client import Client
from appwrite.services.users import Users
from icecream import ic
from app_write import create_users

client = Client()

(
    client.set_endpoint("http://192.168.230.254:82/v1")
    .set_project("65cd62cc3385d8434a53")
    .set_key(
        "061b4abb7743ecc570cc693483b36bc0f50616b2631c5f7cec3825e15cd196d703434b9c7d6a9bb0d44ef7d8ca9eb9d570a916c2e4867993b37fc29d9579278acdba9d2ad485eca0381e975aedf5f3217cf6653f4234265975c38186aa53ef572702a298e16576843d7dfd47cb77a649fff0f4460876c52b4c7d84c0b2c74706"
    )
)
users = Users(client)


class TestAppwrite(TestCase):
    def test_get_user(self):
        try:
            result = users.get("560")
            ic(result)
        except Exception as e:
            ic(e)

    def test_sync_user(self):
        create_users.main()

    def test_update_email(self):
        users.update_email("556","950800517@perumdamts.com")