import time

from core.config import LOGGER
from core.kepegawaian.kepeg_cuti_approval import save_cuti_approval
from core.kepegawaian.kepeg_cuti_approval_chain import update_approval_chain
from core.smartoffice.eo_cuti_approval import fetch_cuti_approval
from v2.v2_helper import format_datetime_series, log_duration


def main():
    try:
        start_overall = time.time()

        # 1. Fetching data
        start = time.time()
        df = fetch_cuti_approval()
        log_duration("Fetching cuti_approval", start)

        if df.empty:
            LOGGER.info("No cuti_approval data to process.")
            return

        # 2. Formatting
        df["created_at"] = format_datetime_series(df["created_at"])

        # 3. Saving cuti approval
        start = time.time()
        save_cuti_approval(df)
        log_duration("Posting cuti_approval", start)

        # 4. Updating approval chain status
        start = time.time()
        update_approval_chain(df)
        log_duration("Updating cuti_approval_chain", start)

        log_duration("Migration v2_16_cuti_approval total process", start_overall)

    except Exception as e:
        LOGGER.error(f"Critical error in v2_16_cuti_approval: {e}", exc_info=True)


if __name__ == "__main__":
    main()
