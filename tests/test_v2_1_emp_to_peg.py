import unittest

from icecream import ic

from core.config import LOGGER
from core.kepegawaian.kepeg_gaji_pendapatan_non_pajak import fetch_all_gaji_pendapatan_non_pajak
from core.smartoffice.eo_employee import fetch_employee_for_pegawai, fetch_gaji_employee


class MyTestCase(unittest.TestCase):
    def test_data_fetched(self):
        self.assertEqual(True, False)  # add assertion here

    def test_emp_fetched(self):
        df = fetch_employee_for_pegawai()
        self.assertEqual(False, df.empty)

    def test_fetch_ptkp(self):
        df = fetch_all_gaji_pendapatan_non_pajak()
        self.assertEqual(False, df.empty)
        LOGGER.info(df.to_dict("records"))

    def test_fetch_gaji_empl(self):
        df=fetch_gaji_employee()
        self.assertEqual(False, df.empty)
        ic(df.to_dict("records"))


if __name__ == '__main__':
    unittest.main()
