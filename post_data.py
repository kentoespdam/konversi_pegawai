import json
import pandas as pd
from icecream import ic
import requests

baseUrl = "http://localhost:8080"


def kirim_pegawai(data: pd.DataFrame):
    dict_data = {
        "nik": data["nik"],
        "nama": data["nama"],
        "jenisKelamin": data["jenisKelamin"],
        "tempatLahir": data["tempatLahir"],
        "tanggalLahir": data["tanggalLahir"],
        "alamat": data["alamat"],
        "telp": data["telp"],
        "agama": data["agama"],
        "ibuKandung": data["ibuKandung"],
        "pendidikanTerakhirId": data["pendidikanTerakhirId"],
        "statusKawin": data["statusKawin"],
        "notes": data["notes"],
        "nipam": data["nipam"],
        "statusPegawai": data["statusPegawai"],
        "statusKerja": data["statusKerja"],
        "jabatanId": data["jabatanId"],
        "organisasiId": data["organisasiId"],
        "profesiId": data["profesiId"],
        "golonganId": data["golonganId"],
        "gradeId": data["gradeId"],
        "nomorSk": data["nomorSk"],
        "tanggalSk": data["tanggalSk"],
        "tmtBerlakuSk": data["tmtBerlakuSk"],
        "gajiPokok": data["gajiPokok"],
    }
    # json_data = json.dumps(dict_data)
    url = f"{baseUrl}/pegawai"
    req = requests.post(url, json=dict_data, headers={
                        "Content-Type": "application/json"})
    ic(req.status_code, req.json())
    if req.status_code != 201:
        ic(data["nipam"], req.text, req.json())
