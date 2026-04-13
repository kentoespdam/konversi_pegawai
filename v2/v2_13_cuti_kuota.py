import time

from core.kepegawaian.kepeg_cuti_kuota import save_cuti_kuota
from core.smartoffice.eo_cuti_kuota import fetch_cuti_kuota

from v2.v2_helper import format_date_series, log_duration


def main():
    start=time.time()
    ck_df = fetch_cuti_kuota()
    ck_df = cleanup(ck_df)
    save_cuti_kuota(ck_df)
    log_duration("Posting cuti_kuota finished", start)


def cleanup(df):
    df["expired"] = format_date_series(df["expired"])
    return df


if __name__ == "__main__":
    main()
