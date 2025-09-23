import time

import pandas as pd
from icecream import ic

from core.config import LOGGER
from core.kepegawaian.kepeg_organisasi import update_organisasi_from_organization
from core.smartoffice.eo_organisasi import fetch_organisasi
from v2.v2_helper import log_duration


def main():
    start_time = time.time()
    LOGGER.info("Synchronize Organisasi Started")
    df = fetch_organisasi()
    df = _cleanup(df)
    ic(df.to_dict("records"))
    update_organisasi_from_organization(df)
    log_duration("Sync Organisasi", start_time)


def _cleanup(df: pd.DataFrame):
    df = df.copy()
    df["is_deleted"] = df["org_status"].eq("Enabled")
    return df[["org_id", "org_name", "mail_code", "category", "is_deleted"]]


if __name__ == "__main__":
    main()
