import time

from core.kepegawaian.kepeg_cuti_approval_chain import save_approval_chain
from core.smartoffice.eo_cuti_aproval_chain import fetch_cuti_approval_chain
from v2.v2_helper import log_duration


def main():
    start = time.time()
    cac_df = fetch_cuti_approval_chain()
    save_approval_chain(cac_df)
    log_duration("Posting cuti_approval_chain finished", start)


if __name__ == "__main__":
    main()
