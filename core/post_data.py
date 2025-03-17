import pandas as pd
from icecream import ic
import requests
import os
from dotenv import load_dotenv

load_dotenv()


def kirim_pegawai(data: pd.DataFrame):
    payload = {
        "nik": data["nik"],
        "nama": data["nama"],
        "jenisKelamin": data["jenisKelamin"],
        "tempatLahir": data["tempatLahir"],
        "tanggalLahir": data["tanggalLahir"],
        "alamat": data["alamat"],
        "telp": data["telp"],
        "agama": data["agama"],
        "ibuKandung": data["ibuKandung"],
        "pendidikanTerakhirId": data["pendidikanTerakhirId"] if data["pendidikanTerakhirId"] > 0 else None,
        "statusKawin": data["statusKawin"],
        "notes": data["notes"],
        "nipam": data["nipam"],
        "statusPegawai": data["statusPegawai"],
        "organisasiId": data["organisasiId"],
        "jabatanId": data["jabatanId"],
        "statusKerja": data["statusKerja"],
        "nomorSk": data["nomorSk"],
        "tanggalSk": data["tanggalSk"],
        "tmtBerlakuSk": data["tmtBerlakuSk"],
        "gajiPokok": data["gajiPokok"],
    }

    if data["profesiId"] > 0:
        payload["profesiId"] = data["profesiId"]
    if data["golonganId"] > 0:
        payload["golonganId"] = data["golonganId"]
    if data["kodePajakId"] > 0:
        payload["kodePajakId"] = data["kodePajakId"]
    if data["tmtKontrakSelesai"] is not pd.NA:
        payload["tmtKontrakSelesai"] = data["tmtKontrakSelesai"]

    try:
        url = f"{os.getenv("API_URL")}/pegawai"
        req = requests.post(url, json=payload, headers={
                            "Content-Type": "application/json"})
        if req.status_code != 201:
            ic(data.to_dict(), payload, req.text)

    except Exception as e:
        ic("error posting: ", payload)


def do_post(path, payload):
    try:
        url = f"{os.getenv('API_URL')}/{path}"
        req = requests.post(url, json=payload, headers={
                            "Content-Type": "application/json"})
        # if req.status_code != 201:
        #     ic(payload, req.text)

        return req.json()

    except Exception as e:
        ic("error posting: ", payload)
        return None


def do_put(path: str, payload: dict, id: int | str = None):
    try:
        url = f"{os.getenv('API_URL')}/{path}/{id}"
        req = requests.put(url, json=payload, headers={
            "Content-Type": "application/json"})
        if req.status_code != 200:
            ic(payload, req.text)
        return req.json()

    except Exception as e:
        ic("error posting: ", payload)
        return None
