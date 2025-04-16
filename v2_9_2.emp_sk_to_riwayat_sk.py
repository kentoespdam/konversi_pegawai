import time
import pandas as pd
from icecream import ic
from core.kepegawaian.kepeg_riwayat_sk import save_riwayat_sk_from_emp_sk
from core.smartoffice.emp_sk import fetch_emp_sk_for_riwayat_sk
import swifter


def main():
    start_time = time.time()
    sk_df = pd.DataFrame(fetch_emp_sk_for_riwayat_sk())
    sk_df = cleanup(sk_df)
    ic(f"generating data finish in {time.time()-start_time}s")

    start_time = time.time()
    save_riwayat_sk_from_emp_sk(sk_df)
    ic(f"posting data finish in {time.time()-start_time}s")


def cleanup(df: pd.DataFrame):
    df["update_master"] = df["update_master"].swifter.apply(
        lambda x: True if x == 1 else False
    )
    df["is_deleted"] = df["is_deleted"].swifter.apply(
        lambda x: True if x == 1 else False
    )
    return df


if __name__ == "__main__":
    main()
