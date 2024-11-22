import uuid
import requests
from pandas import DataFrame
from icecream import ic


baseUrl = "http://192.168.1.214:8080"


def kirim_biodata(data: DataFrame):
    session_id = uuid.uuid4().hex
    data["session_id"] = session_id
    json_data = data.to_json(date_format="iso")
    url = f"{baseUrl}/profil/biodata"
    # url = f"http://localhost:8088"
    req = requests.post(
        url, data=json_data, headers={"Content-Type": "application/json"}
    )
    # print(req.request.prepare_body())
    # res = req.text()
    ic(req.text)
    # return res.get("statusText")
    return req.status_code


def kirim_pegawai(data: DataFrame):
    session_id = uuid.uuid4().hex
    data["session_id"] = session_id
    json_data = data.to_json(date_format="iso")
    url = f"{baseUrl}/pegawai"
    # url = f"http://localhost:8088"
    req = requests.post(
        url, data=json_data, headers={"Content-Type": "application/json"}
    )
    if req.status_code != 201:
        ic(data["nipam"], req.text)
    return req.status_code
