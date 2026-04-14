import time
from core.config import LOGGER
from core.kepegawaian.kepeg_cuti_klaim_detail import save_cuti_klaim_detail
from core.smartoffice.eo_cuti_pegawai_detail import fetch_cuti_pegawai_detail
from v2.v2_helper import format_date_series, log_duration


def main():
    start = time.time()
    try:
        LOGGER.info("Starting migration: cuti_klaim_detail")
        ckd_df = fetch_cuti_pegawai_detail()

        if ckd_df is None or ckd_df.empty:
            LOGGER.warning("No data found for cuti_klaim_detail")
            return

        LOGGER.info(f"Fetched {len(ckd_df)} rows for cuti_klaim_detail")

        # Data preparation
        ckd_df["tanggal"] = format_date_series(ckd_df["tanggal"])

        # Save data
        save_cuti_klaim_detail(ckd_df)

        log_duration("Posting cuti_klaim_detail finished", start)
    except Exception as e:
        LOGGER.error(f"Migration v2_17 failed: {e}")
        raise


if __name__ == "__main__":
    main()