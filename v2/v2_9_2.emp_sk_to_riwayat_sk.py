import time

import pandas as pd

from core.kepegawaian.kepeg_riwayat_sk import save_riwayat_sk_from_emp_sk
from core.smartoffice.emp_sk import fetch_emp_sk_for_riwayat_sk, update_init_smartoffice_no_sk
from v2.v2_helper import log_duration


def main():
    start_time = time.time()
    update_init_smartoffice_no_sk()
    sk_df = pd.DataFrame(fetch_emp_sk_for_riwayat_sk())
    sk_df = cleanup(sk_df)
    log_duration("generating data finish in ", start_time)

    start_time = time.time()
    save_riwayat_sk_from_emp_sk(sk_df)
    log_duration("posting data finish in ", start_time)


def cleanup(df: pd.DataFrame):
    df["update_master"] = df["update_master"].eq(1)
    df["is_deleted"] = df["is_deleted"].eq(1)
    return df


if __name__ == "__main__":
    main()
