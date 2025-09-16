import time

import pandas as pd

from core.kepegawaian.kepeg_golongan import fetch_all_golongan
from core.kepegawaian.kepeg_profesi import fetch_profesi
from core.kepegawaian.kepeg_riwayat_mutasi import save_riwayat_mutasi_from_emp_work_history
from core.kepegawaian.kepeg_riwayat_sk import fetch_all_riwayat_sk
from core.smartoffice.emp_work_history import fetch_emp_work_history_for_riwayat_mutasi
from v2.v2_helper import format_date_series, log_duration

# Constants

JENIS_MUTASI_MAP: dict[int, int] = {
    # Smartoffice -> Kepegawaian
    1: 0,
    2: 1,
    3: 4,
    4: 6,
}


def main():
    start_time = time.time()

    work_history_df = fetch_emp_work_history_for_riwayat_mutasi()
    work_history_df = cleanup(work_history_df)
    work_history_df = work_history_df[work_history_df["riwayat_sk_id"] > 0].reset_index(drop=True)
    log_duration("generating data finish in ", start_time)

    start_time = time.time()
    save_riwayat_mutasi_from_emp_work_history(work_history_df)
    log_duration("posting data finish in ", start_time)


def cleanup(df: pd.DataFrame) -> pd.DataFrame:
    """
    Transform and enrich raw emp_work_history data to the format expected by riwayat_mutasi.

    Steps:
    - Resolve riwayat_sk_id via merge on (pegawai_id, nomor_sk)
    - Map golongan_id and nama_golongan via merges
    - Map profesi (current and old) from jabatan via merges
    - Normalize date strings
    - Normalize jenis_mutasi and is_deleted
    - Ensure required integer dtypes
    """
    # Prepare SK data
    sk_df = pd.DataFrame(fetch_all_riwayat_sk())
    if not sk_df.empty:
        sk_df["golongan_id"] = sk_df["golongan_id"].apply(lambda x: 0 if pd.isna(x) else x).astype(int)

    # Merge to get riwayat_sk_id based on (pegawai_id, nomor_sk)
    # Keep only the 'id' from SK as 'riwayat_sk_id'
    df = df.merge(
        sk_df[["id", "pegawai_id", "nomor_sk"]],
        how="left",
        left_on=["pegawai_id", "nomor_sk"],
        right_on=["pegawai_id", "nomor_sk"],
    ).rename(columns={"id": "riwayat_sk_id"})
    df["riwayat_sk_id"] = df["riwayat_sk_id"].fillna(0).astype(int)

    # Map golongan_id from SK using riwayat_sk_id
    if not sk_df.empty:
        df = df.merge(
            sk_df[["id", "golongan_id"]].rename(columns={"id": "riwayat_sk_id"}),
            how="left",
            on="riwayat_sk_id",
        )
        df["golongan_id"] = df["golongan_id"].fillna(0).astype(int)
    else:
        df["golongan_id"] = 0

    # Map nama_golongan from master golongan
    golongan_df = pd.DataFrame(fetch_all_golongan())
    if not golongan_df.empty:
        df = df.merge(
            golongan_df[["id", "golongan"]].rename(columns={"id": "golongan_id", "golongan": "nama_golongan"}),
            how="left",
            on="golongan_id",
        )
    else:
        df["nama_golongan"] = None
    # cleanup nan nama_golongan
    df["nama_golongan"] = df["nama_golongan"].where(df["nama_golongan"].notna(), None)

    # Map profesi (current) from jabatan_id
    profesi_df = pd.DataFrame(fetch_profesi())
    if not profesi_df.empty:
        current_prof = profesi_df[["jabatan_id", "id", "nama"]].rename(
            columns={"id": "profesi_id", "nama": "nama_profesi"}
        )
        df = df.merge(current_prof, how="left", on="jabatan_id")

        # Map profesi (old) from jabatan_lama_id
        old_prof = profesi_df[["jabatan_id", "id", "nama"]].rename(
            columns={"jabatan_id": "jabatan_lama_id", "id": "profesi_lama_id", "nama": "nama_profesi_lama"}
        )
        df = df.merge(old_prof, how="left", on="jabatan_lama_id")

        # Fill defaults to match prior behavior: id -> 0, name -> None
        df["profesi_id"] = df["profesi_id"].fillna(0).astype(int)
        df["profesi_lama_id"] = df["profesi_lama_id"].fillna(0).astype(int)
        df["nama_profesi"] = df["nama_profesi"].where(df["nama_profesi"].notna(), None)
        df["nama_profesi_lama"] = df["nama_profesi_lama"].where(df["nama_profesi_lama"].notna(), None)
    else:
        df["profesi_id"] = 0
        df["profesi_lama_id"] = 0
        df["nama_profesi"] = None
        df["nama_profesi_lama"] = None

    # Format dates
    df["tmt_berlaku"] = format_date_series(df["tmt_berlaku"])
    df["tanggal_berakhir"] = format_date_series(df["tanggal_berakhir"])

    # Normalize jenis_mutasi (Init Smartoffice -> 0, else mapping with default 0)
    init_mask = df["nomor_sk"] == "Init Smartoffice"
    mapped = df["jenis_mutasi"].map(JENIS_MUTASI_MAP).fillna(0).astype(int)
    df["jenis_mutasi"] = mapped.where(~init_mask, 0)

    # Normalize is_deleted from {0,1} to {False,True}
    df["is_deleted"] = df["is_deleted"].eq(1)

    # Ensure integer types for these columns
    df = df.astype({
        "organisasi_id": int,
        "jabatan_id": int,
        "organisasi_lama_id": int,
        "jabatan_lama_id": int,
    })

    return df


if __name__ == '__main__':
    main()
