import time

import pandas as pd
from icecream import ic

from core.smartoffice.emp_sk import save_emp_sk_from_emp_work_history
from core.smartoffice.emp_work_history import fetch_emp_work_history_for_emp_sk


def main():
    start_time = time.time()
    sk_df = pd.DataFrame(fetch_emp_work_history_for_emp_sk())
    if sk_df.empty:
        ic("sk_df is empty")
        return
    sk_df = cleanup_init(sk_df)
    ic(f"generating data finish in {time.time() - start_time}s")

    start_time = time.time()
    save_emp_sk_from_emp_work_history(sk_df)
    ic(f"posting data finish in {time.time() - start_time}s")


def filter_sk(df: pd.DataFrame, no_sk: str, esk_no_sk: str = None):
    return df.query("esk_no_sk.isnull() or no_sk==@no_sk").reset_index(drop=True)


def cleanup_init(df: pd.DataFrame):
    df["ref_id"] = 0
    df["status"] = 1
    df["notes"] = df["notes"].apply(
        lambda x: _cleanup_notes(x))
    return df


def _cleanup_notes(notes):
    if notes is None or notes == "":
        return "Init Smartoffice"
    else:
        return notes


if __name__ == "__main__":
    main()
