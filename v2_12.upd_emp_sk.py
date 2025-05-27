from core.enums import EJenisSk
from core.kepegawaian.kepeg_pegawai import update_sk_pegawai
from core.kepegawaian.kepeg_sk import fetch_latest_sk_by_pegawai
import pandas as pd
from icecream import ic
import swifter


def main():
    riwayat_sk = fetch_latest_sk_by_pegawai()
    if riwayat_sk.empty:
        return
    riwayat_sk = _cleanup(riwayat_sk)

    sk_capeg_list = riwayat_sk[riwayat_sk["jenis_sk"]
                               == EJenisSk.SK_CAPEG.value].reset_index(drop=True)
    sk_jabatan_list = riwayat_sk[riwayat_sk["jenis_sk"]
                                 == EJenisSk.SK_JABATAN.value].reset_index(drop=True)
    sk_golongan_list = riwayat_sk[riwayat_sk["jenis_sk"] ==
                                  EJenisSk.SK_KENAIKAN_PANGKAT_GOLONGAN.value].reset_index(drop=True)
    sk_mutasi_list = riwayat_sk[riwayat_sk["jenis_sk"]
                                == EJenisSk.SK_MUTASI.value].reset_index(drop=True)
    sk_pegawai_list = riwayat_sk[riwayat_sk["jenis_sk"] ==
                                 EJenisSk.SK_PEGAWAI_TETAP.value].reset_index(drop=True)

    # ic(sk_capeg_list.to_dict(orient="records"))
    update_sk_pegawai(sk_capeg_list, EJenisSk.SK_CAPEG)
    update_sk_pegawai(sk_jabatan_list, EJenisSk.SK_JABATAN)
    update_sk_pegawai(sk_golongan_list, EJenisSk.SK_KENAIKAN_PANGKAT_GOLONGAN)
    update_sk_pegawai(sk_mutasi_list, EJenisSk.SK_MUTASI)
    update_sk_pegawai(sk_pegawai_list, EJenisSk.SK_PEGAWAI_TETAP)


def _cleanup(df: pd.DataFrame):
    df["kenaikan_berikutnya"] = df["kenaikan_berikutnya"].swifter.apply(
        lambda x: x.strftime('%Y-%m-%d') if x is not None else None)
    df["tmt_berlaku"] = df["tmt_berlaku"].swifter.apply(
        lambda x: x.strftime('%Y-%m-%d') if x is not None else None)
    return df


if __name__ == "__main__":
    main()
