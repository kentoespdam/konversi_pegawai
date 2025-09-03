from core.kepegawaian.kepeg_pegawai import update_pegawai_phdp
from core.smartoffice.eo_employee import fetch_gaji_employee
from icecream import ic


def main():
    salary_rows = fetch_gaji_employee()
    update_pegawai_phdp(salary_rows)


if __name__ == "__main__":
    main()
