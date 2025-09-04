import time

from core.kepegawaian.kepeg_gaji_tunjangan import save_gaji_tunjangan
from core.kepegawaian.kepeg_parameter_setting import save_parameter_setting
from core.kepegawaian.kepeg_potongan_tkk import cleanup_potongan_tkk, save_potongan_tkk
from core.smartoffice.eo_salary_allowance import fetch_salary_allowance, cleanup_salary_allowance
from core.smartoffice.eo_salary_tkk_reduction import fetch_tkk_reduction
from core.smartoffice.eo_sys_reference import fetch_maks_potongan
from v2.v2_helper import log_duration


def main():
    start_time = time.time()
    master_tunjangan = fetch_salary_allowance()
    master_tunjangan = cleanup_salary_allowance(master_tunjangan)
    save_gaji_tunjangan(master_tunjangan)
    log_duration("Posting gaji_tunjangan finished", start_time)

    start_time = time.time()
    parameter_df = fetch_maks_potongan()
    save_parameter_setting(parameter_df)
    log_duration("Posting parameter_setting finished", start_time)

    start_time = time.time()
    potongan_tkk_df = fetch_tkk_reduction()
    potongan_tkk_df = cleanup_potongan_tkk(potongan_tkk_df)
    save_potongan_tkk(potongan_tkk_df)
    log_duration("Posting potongan_tkk finished", start_time)


if __name__ == "__main__":
    main()
