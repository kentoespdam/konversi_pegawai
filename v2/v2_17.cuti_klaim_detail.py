import time

from core.kepegawaian.kepeg_cuti_klaim_detail import save_cuti_klaim_detail
from core.smartoffice.eo_cuti_pegawai_detail import fetch_cuti_pegawai_detail
from v2.v2_helper import format_date_series, log_duration


def main():
    start = time.time()
    ckd_df = fetch_cuti_pegawai_detail()
    ckd_df["tanggal"] = format_date_series(ckd_df["tanggal"])
    save_cuti_klaim_detail(ckd_df)
    log_duration("Posting cuti_klaim_detail finished", start)


if __name__ == "__main__":
    main()