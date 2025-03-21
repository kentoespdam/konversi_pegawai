import time
import pandas as pd
from core.kepegawaian.kepeg_golongan import fetch_all_golongan
from core.kepegawaian.kepeg_pegawai import fetch_all_pegawai
from core.kepegawaian.kepeg_sk import save_data_riwayat_sk
from core.smartoffice.emp_sk import fetch_data_for_riwayat_sk
from icecream import ic
import swifter


def main():
    """
    Fetch data for riwayat sk, pegawai, and golongan, then join them together
    """
    start_time = time.time()

    riwayat_sk_df = pd.DataFrame(fetch_data_for_riwayat_sk())
    riwayat_sk_df = cleanup_data_sk(riwayat_sk_df)
    riwayat_sk_tuple = df_to_tuple_list(riwayat_sk_df)

    ic(f"Execution time: {time.time() - start_time} seconds")
    # ic(riwayat_sk_tuple)

    start_time = time.time()
    save_data_riwayat_sk(riwayat_sk_tuple)
    ic(f"Execution time: {time.time() - start_time} seconds")


def df_to_tuple_list(df: pd.DataFrame):
    return [
        (
            row.pegawai_id,
            row.nipam,
            row.nama,
            row.nomor_sk,
            row.jenis_sk,
            row.tanggal_sk,
            row.tmt_berlaku,
            row.golongan_id if row.golongan_id > 0 else None,
            row.gaji_pokok,
            row.mkg_tahun,
            row.mkg_bulan,
            row.kenaikan_berikutnya,
            row.mkgb_tahun,
            row.mkgb_bulan,
            row.update_master,
            row.notes
        )
        for row in df.itertuples(index=False)
    ]


def cleanup_data_sk(riwayat_sk_df: pd.DataFrame):
    pegawai_df = pd.DataFrame(fetch_all_pegawai())
    golongan_df = pd.DataFrame(fetch_all_golongan())

    riwayat_sk_df['pegawai_id'] = riwayat_sk_df['nipam'].swifter.apply(
        lambda x: get_pegawai_id(x, pegawai_df)
    )
    riwayat_sk_df["jenis_sk"] = riwayat_sk_df["jenis_sk"].swifter.apply(
        lambda x: x - 1)
    riwayat_sk_df['golongan_id'] = riwayat_sk_df['golongan'].swifter.apply(
        lambda x: get_golongan_id(x, golongan_df)
    )
    date_columns = ['tanggal_sk', 'tmt_berlaku', 'kenaikan_berikutnya']
    for col in date_columns:
        riwayat_sk_df[col] = riwayat_sk_df[col].swifter.apply(
            lambda date: date.strftime(
                '%Y-%m-%d') if date is not None else None
        )
    riwayat_sk_df = riwayat_sk_df[riwayat_sk_df['pegawai_id'] != 0].drop(
        columns=['golongan']).reset_index(drop=True)
    riwayat_sk_df.mask(riwayat_sk_df.isna(), 0, inplace=True)

    return riwayat_sk_df


def get_pegawai_id(nipam, pegawai_df):
    result = pegawai_df.query("nipam==@nipam")
    return result.id.values[0] if not result.empty else 0


def get_golongan_id(golongan, golongan_df):
    result = golongan_df.query("golongan==@golongan")
    return result.id.values[0] if not result.empty else 0


if __name__ == "__main__":
    main()
