import time

from core.kepegawaian.kepeg_gaji_pendapatan_non_pajak import save_gaji_pendapatan_non_pajak
from core.kepegawaian.kepeg_gaji_tunjangan import save_gaji_tunjangan
from core.kepegawaian.kepeg_parameter_setting import save_parameter_setting
from core.kepegawaian.kepeg_potongan_tkk import cleanup_potongan_tkk, save_potongan_tkk
from core.smartoffice.eo_salary_allowance import fetch_salary_allowance, cleanup_salary_allowance
from core.smartoffice.eo_salary_non_taxable_income import fetch_salary_non_taxable_income
from core.smartoffice.eo_salary_tkk_reduction import fetch_tkk_reduction
from core.smartoffice.eo_sys_reference import fetch_maks_potongan
from v2.v2_helper import log_duration


import pandas as pd
import traceback
import numpy as np
from core.config import LOGGER


def main():
    try:
        LOGGER.info("Starting Master Gaji Migration...")

        # 1. Gaji Tunjangan
        start_time = time.time()
        master_tunjangan = fetch_salary_allowance()
        if not master_tunjangan.empty:
            LOGGER.info(f"Fetched {len(master_tunjangan)} salary allowances.")
            master_tunjangan = cleanup_salary_allowance(master_tunjangan)
            save_gaji_tunjangan(master_tunjangan)
        else:
            LOGGER.info("No salary allowances found.")
        log_duration("Posting gaji_tunjangan finished", start_time)

        # 2. Pendapatan Non Pajak
        start_time = time.time()
        df_pnp = fetch_salary_non_taxable_income()
        if not df_pnp.empty:
            LOGGER.info(f"Fetched {len(df_pnp)} non-taxable income records.")
            # Sanitization (simple, no cleanup function needed)
            df_pnp = df_pnp.replace({np.nan: None, pd.NaT: None, pd.NA: None})
            save_gaji_pendapatan_non_pajak(df_pnp)
        else:
            LOGGER.info("No non-taxable income found.")
        log_duration("Posting gaji_pendapatan_non_pajak finished", start_time)

        # 3. Parameter Setting
        start_time = time.time()
        parameter_df = fetch_maks_potongan()
        if not parameter_df.empty:
            LOGGER.info(f"Fetched {len(parameter_df)} parameter settings.")
            parameter_df = parameter_df.replace({np.nan: None, pd.NaT: None, pd.NA: None})
            save_parameter_setting(parameter_df)
        else:
            LOGGER.info("No parameter settings found.")
        log_duration("Posting parameter_setting finished", start_time)

        # 4. Potongan TKK
        start_time = time.time()
        potongan_tkk_df = fetch_tkk_reduction()
        if not potongan_tkk_df.empty:
            LOGGER.info(f"Fetched {len(potongan_tkk_df)} TKK reductions.")
            potongan_tkk_df = cleanup_potongan_tkk(potongan_tkk_df)
            save_potongan_tkk(potongan_tkk_df)
        else:
            LOGGER.info("No TKK reductions found.")
        log_duration("Posting potongan_tkk finished", start_time)

        LOGGER.info("Master Gaji Migration finished successfully.")

    except Exception as e:
        LOGGER.error(f"Master Gaji Migration failed: {e}")
        LOGGER.error(traceback.format_exc())


if __name__ == "__main__":
    main()
