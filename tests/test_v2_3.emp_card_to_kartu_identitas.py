from unittest import TestCase

from core.smartoffice.emp_card import fetch_emp_card_for_kartu_identitas


class Test(TestCase):
    def test_fetch_emp_card_for_kartu_identitas(self):
        df=fetch_emp_card_for_kartu_identitas()
        self.assertEqual(False, df.empty)

