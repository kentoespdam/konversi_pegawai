import time
import pandas as pd
from core.config import LOGGER
from core.kepegawaian.kepeg_biodata import save_biodata_from_emp_profile
from core.kepegawaian.kepeg_jenjang_pendidikan import fetch_jenjang_pendidikan
from core.kepegawaian.kepeg_kartu_identitas import save_kartu_identitas_from_emp_profile
from core.smartoffice.emp_profile import fetch_data_for_biodata
from v2.v2_helper import format_date_series, log_duration

# Explicit default ID used across lookups
DEFAULT_ID = 0


def main() -> None:
    try:
        start_time = time.time()
        raw_data = fetch_data_for_biodata()
        if not raw_data:
            LOGGER.info("No data found in emp_profile. Skipping migration.")
            return

        biodata_df = pd.DataFrame(raw_data)
        biodata_df = transform_biodata(biodata_df)
        log_duration("generating data finish", start_time)

        start_time = time.time()
        save_biodata_from_emp_profile(biodata_df)
        save_kartu_identitas_from_emp_profile(biodata_df)
        log_duration("posting data finish", start_time)
    except Exception as e:
        LOGGER.error(f"Error during emp_profile to biodata migration: {str(e)}")
        raise


def transform_biodata(df: pd.DataFrame) -> pd.DataFrame:
    """
    Transform raw emp_profile data into the format expected by kepegawaian biodata.
    - Normalize date columns
    - Map pendidikanTerakhir -> pendidikan_id using master jenjang_pendidikan
    - Normalize boolean flags
    """
    jenjang_pendidikan_df = pd.DataFrame(fetch_jenjang_pendidikan())

    # Dates
    df["tanggal_lahir"] = format_date_series(df["tanggal_lahir"])

    # Pendidikan mapping (Optimized Bug 4)
    pendidikan_map = dict(zip(jenjang_pendidikan_df["nama"], jenjang_pendidikan_df["id"]))
    df["pendidikan_id"] = df["pendidikanTerakhir"].map(pendidikan_map).fillna(DEFAULT_ID).astype(int)

    # Booleans & NULL handling (Bug 3 & 6)
    df["is_deleted"] = df["is_deleted"].fillna(0).astype(int)
    df["is_pegawai"] = df["emp_flag"].fillna(0).ne(0).astype(int)

    return df


if __name__ == "__main__":
    main()
