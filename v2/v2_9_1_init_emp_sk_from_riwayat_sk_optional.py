import time

import numpy as np
import pandas as pd

from core.config import LOGGER
from core.smartoffice.emp_sk import save_emp_sk_from_emp_work_history
from core.smartoffice.emp_work_history import fetch_emp_work_history_for_emp_sk
from v2.v2_helper import log_duration


def main():
    start_time = time.time()
    sk_df = fetch_emp_work_history_for_emp_sk()
    if sk_df.empty:
        LOGGER.error("sk_df is empty")
        return
    sk_df = cleanup_init(sk_df)
    log_duration("generating data", start_time)

    start_time = time.time()
    save_emp_sk_from_emp_work_history(sk_df)
    log_duration("posting data", start_time)


def filter_sk(df: pd.DataFrame, no_sk: str, esk_no_sk: str = None):
    mask = df["esk_no_sk"].isnull() or df["no_sk"].eq(no_sk)
    return df[mask].reset_index(drop=True)


def cleanup_init(df: pd.DataFrame):
    df = df.copy()
    df["ref_id"] = 0
    df["status"] = 1
    df["notes"] = np.where(
        df["notes"].isna() | df["notes"].eq(""),
        "Init Smartoffice",
        df["notes"].astype(str)
    )
    return df


if __name__ == "__main__":
    main()
