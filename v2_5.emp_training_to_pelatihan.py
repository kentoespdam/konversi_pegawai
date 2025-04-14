import time
import pandas as pd
from icecream import ic
from core.kepegawaian.kepeg_pelatihan import save_pelatihan_from_emp_training
from core.smartoffice.emp_training import fetch_emp_training_for_pelatihan
import swifter


def main():
    start_time = time.time()
    training_df = pd.DataFrame(fetch_emp_training_for_pelatihan())
    training_df = cleanup(training_df)
    ic(f"generating data finish in {time.time()-start_time}s")

    start_time = time.time()
    save_pelatihan_from_emp_training(training_df)
    ic(f"posting data finish in {time.time()-start_time}s")


def cleanup(df: pd.DataFrame):
    df["tanggal_mulai"] = df["tanggal_mulai"].swifter.apply(
        lambda x: x.strftime("%Y-%m-%d") if x is not None else None
    )
    df["tanggal_selesai"] = df["tanggal_selesai"].swifter.apply(
        lambda x: x.strftime("%Y-%m-%d") if x is not None else None
    )
    df["ikatan_dinas"] = df["ikatan_dinas"].swifter.apply(
        lambda x: True if x == 1 else False
    )
    df["tanggal_akhir_ikatan"] = df["tanggal_akhir_ikatan"].swifter.apply(
        lambda x: x.strftime("%Y-%m-%d") if x is not None else None
    )
    df["tanggal_pengajuan"] = df["tanggal_pengajuan"].swifter.apply(
        lambda x: x.strftime("%Y-%m-%d %X") if x is not None else None
    )
    df["tanggal_disetujui"] = df["tanggal_disetujui"].swifter.apply(
        lambda x: x.strftime("%Y-%m-%d %X") if x is not pd.NaT else None
    )
    df["is_deleted"] = df["is_deleted"].swifter.apply(
        lambda x: True if x == 1 else False
    )
    return df


if __name__ == "__main__":
    main()
