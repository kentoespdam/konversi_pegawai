import time
import pandas as pd
from icecream import ic
from core.kepegawaian.kepeg_golongan import fetch_all_golongan
from core.kepegawaian.kepeg_profesi import fetch_profesi
from core.kepegawaian.kepeg_riwayat_mutasi import save_riwayat_mutasi_from_emp_work_history
from core.kepegawaian.kepeg_riwayat_sk import fetch_all_riwayat_sk
from core.smartoffice.emp_work_history import fetch_emp_work_history_for_riwayat_mutasi
import swifter


def main():
    start_time = time.time()
    work_history_df = pd.DataFrame(fetch_emp_work_history_for_riwayat_mutasi())
    work_history_df = cleanup(work_history_df)
    work_history_df=work_history_df[work_history_df["riwayat_sk_id"]>0].reset_index(drop=True)
    ic(f"generating data finish in {time.time()-start_time}s")

    start_time = time.time()
    save_riwayat_mutasi_from_emp_work_history(work_history_df)
    ic(f"posting data finish in {time.time()-start_time}s")


def cleanup(df: pd.DataFrame):
    sk_df = pd.DataFrame(fetch_all_riwayat_sk())
    sk_df["golongan_id"] = sk_df["golongan_id"].swifter.apply(
        lambda x: 0 if pd.isna(x) else x).astype(int)
    df["riwayat_sk_id"] = df.swifter.apply(
        lambda x: _cleanup_riwayat_sk_id(sk_df, x["pegawai_id"], x["nomor_sk"]), axis=1)
    df["golongan_id"] = df["riwayat_sk_id"].swifter.apply(
        lambda x: _cleanup_golongan_id(sk_df, x))

    golongan_df = pd.DataFrame(fetch_all_golongan())
    df["nama_golongan"] = df["golongan_id"].swifter.apply(
        lambda x: _cleanup_nama_golongan(golongan_df, x))

    profesi_df = pd.DataFrame(fetch_profesi())
    df["profesi_id"] = df["jabatan_id"].swifter.apply(
        lambda x: _cleanup_profesi_id(profesi_df, x, "id")
    )
    df["nama_profesi"] = df["jabatan_id"].swifter.apply(
        lambda x: _cleanup_profesi_id(profesi_df, x, "nama")
    )
    df["profesi_lama_id"] = df["jabatan_lama_id"].swifter.apply(
        lambda x: _cleanup_profesi_id(profesi_df, x, "id")
    )
    df["nama_profesi_lama"] = df["jabatan_lama_id"].swifter.apply(
        lambda x: _cleanup_profesi_id(profesi_df, x, "nama")
    )

    df["tmt_berlaku"] = df["tmt_berlaku"].swifter.apply(
        lambda x: x.strftime("%Y-%m-%d") if x is not None else None)
    df["tanggal_berakhir"] = df["tanggal_berakhir"].swifter.apply(
        lambda x: x.strftime("%Y-%m-%d") if x is not None else None)
    df["jenis_mutasi"] = df.swifter.apply(
        lambda x: _cleanup_jenis_mutasi(x), axis=1)
    df["is_deleted"] = df["is_deleted"].swifter.apply(
        lambda x: True if x == 1 else False)
    df = df.astype({"organisasi_id": int, "jabatan_id": int,
                   "organisasi_lama_id": int, "jabatan_lama_id": int})

    return df


def _cleanup_riwayat_sk_id(sk_df: pd.DataFrame, pegawai_id: int, nomor_sk: str) -> int:
    result = sk_df.query(
        "pegawai_id==@pegawai_id and nomor_sk==@nomor_sk").reset_index(drop=True)
    return result.iloc[0]["id"] if not result.empty else 0


def _cleanup_golongan_id(sk_df: pd.DataFrame, id: int) -> int:
    result = sk_df.query(
        "id==@id").reset_index(drop=True)
    return result.iloc[0]["golongan_id"] if not result.empty else 0


def _cleanup_nama_golongan(golongan_df: pd.DataFrame, id: int) -> str:
    result = golongan_df.query(
        "id==@id").reset_index(drop=True)
    return result.iloc[0]["golongan"] if not result.empty else None


def _cleanup_profesi_id(profesi_df: pd.DataFrame, jabatan_id: int, col: str = "id") -> pd.Series:
    if jabatan_id is None or jabatan_id == 0:
        return 0 if col == "id" else None
    result = profesi_df.query("jabatan_id==@jabatan_id").reset_index(drop=True)
    return result.iloc[0][col] if not result.empty else 0 if col == "id" else None


def _cleanup_jenis_mutasi(row: pd.Series) -> int:
    """
    Clean up jenis_mutasi column.

    Maps Smartoffice jenis_mutasi to Kepegawaian jenis_mutasi.
    """
    if row["nomor_sk"] == "Init Smartoffice":
        return 0
    jenis_mutasi_mapping = {
        1: 0,
        2: 1,
        3: 4,
        4: 6
    }
    return jenis_mutasi_mapping.get(row["jenis_mutasi"], 0)


if __name__ == '__main__':
    main()
