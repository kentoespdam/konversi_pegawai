import time

import pandas as pd

from core.kepegawaian.kepeg_cuti_approval import save_cuti_approval
from core.kepegawaian.kepeg_cuti_approval_chain import update_approval_chain
from core.smartoffice.eo_cuti_approval import fetch_cuti_approval
from v2.v2_helper import format_datetime_series, log_duration


def main():
    start = time.time()
    df = fetch_cuti_approval()
    cleanup(df)
    save_cuti_approval(df)
    log_duration("Posting cuti_approval finished", start)
    start = time.time()
    update_approval_chain(df)
    log_duration("Posting cuti_approval finished", start)


def cleanup(df: pd.DataFrame):
    df["created_at"] = format_datetime_series(df["created_at"])


if __name__ == "__main__":
    main()
