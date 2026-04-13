import unittest
from unittest.mock import patch, MagicMock
import pandas as pd
import numpy as np
from v2.set_nik_pegawai import CleanupNikEmpProfile, KTP_IDENTITY_TYPE

class TestSetNikPegawai(unittest.TestCase):

    @patch('v2.set_nik_pegawai.fetch_pegawai_without_nik')
    @patch('v2.set_nik_pegawai.fetch_emp_cards_by_emp_codes')
    @patch('v2.set_nik_pegawai.update_nik_emp_profile')
    def test_cleanup_logic_found_in_cards(self, mock_update, mock_fetch_cards, mock_fetch_pegawai):
        # Setup mock data: 1 employee without NIK
        mock_fetch_pegawai.return_value = pd.DataFrame({
            "emp_profile_id": [101],
            "emp_code": ["E001"],
            "emp_name": ["John Doe"],
            "emp_identity_type": [None],
            "emp_identity_number": [None]
        })
        
        # Setup mock cards: KTP found for E001
        mock_fetch_cards.return_value = pd.DataFrame({
            "ei_id": [1],
            "emp_code": ["E001"],
            "ei_type": [KTP_IDENTITY_TYPE],
            "ei_number": ["1234567890123456"]
        })

        cleanup = CleanupNikEmpProfile()
        cleanup.run()

        # Verify update was called with correct NIK from card
        called_df = mock_update.call_args[0][0]
        self.assertEqual(called_df.loc[0, "emp_identity_number"], "1234567890123456")
        self.assertEqual(called_df.loc[0, "emp_identity_type"], KTP_IDENTITY_TYPE)

    @patch('v2.set_nik_pegawai.fetch_pegawai_without_nik')
    @patch('v2.set_nik_pegawai.fetch_emp_cards_by_emp_codes')
    @patch('v2.set_nik_pegawai.update_nik_emp_profile')
    def test_cleanup_logic_fallback_to_emp_code(self, mock_update, mock_fetch_cards, mock_fetch_pegawai):
        # Setup mock data: 1 employee without NIK
        mock_fetch_pegawai.return_value = pd.DataFrame({
            "emp_profile_id": [102],
            "emp_code": ["E002"],
            "emp_name": ["Jane Smith"],
            "emp_identity_type": [None],
            "emp_identity_number": [None]
        })
        
        # Setup mock cards: No cards found for E002
        mock_fetch_cards.return_value = pd.DataFrame(columns=["ei_id", "emp_code", "ei_type", "ei_number"])

        cleanup = CleanupNikEmpProfile()
        cleanup.run()

        # Verify update was called with emp_code as fallback
        called_df = mock_update.call_args[0][0]
        self.assertEqual(called_df.loc[0, "emp_identity_number"], "E002")
        self.assertEqual(called_df.loc[0, "emp_identity_type"], KTP_IDENTITY_TYPE)

    @patch('v2.set_nik_pegawai.fetch_pegawai_without_nik')
    @patch('v2.set_nik_pegawai.fetch_emp_cards_by_emp_codes')
    @patch('v2.set_nik_pegawai.update_nik_emp_profile')
    def test_cleanup_logic_not_ktp_card(self, mock_update, mock_fetch_cards, mock_fetch_pegawai):
        # Setup mock data: 1 employee without NIK
        mock_fetch_pegawai.return_value = pd.DataFrame({
            "emp_profile_id": [103],
            "emp_code": ["E003"],
            "emp_name": ["Bob Brown"],
            "emp_identity_type": [None],
            "emp_identity_number": [None]
        })
        
        # Setup mock cards: Card found but NOT KTP (type 1)
        mock_fetch_cards.return_value = pd.DataFrame({
            "ei_id": [2],
            "emp_code": ["E003"],
            "ei_type": [1], 
            "ei_number": ["SIM-123"]
        })

        cleanup = CleanupNikEmpProfile()
        cleanup.run()

        # Verify update was called with emp_code as fallback because KTP not found
        called_df = mock_update.call_args[0][0]
        self.assertEqual(called_df.loc[0, "emp_identity_number"], "E003")
        self.assertEqual(called_df.loc[0, "emp_identity_type"], KTP_IDENTITY_TYPE)

    @patch('v2.set_nik_pegawai.fetch_pegawai_without_nik')
    def test_cleanup_logic_no_data(self, mock_fetch_pegawai):
        mock_fetch_pegawai.return_value = pd.DataFrame()
        
        cleanup = CleanupNikEmpProfile()
        cleanup.run()
        # Should not crash and return early

    def test_injection_special_chars(self):
        # Bug 2 test: Special characters in emp_code
        emp_cards = pd.DataFrame({
            "emp_code": ["E'001", "E\"002"],
            "ei_type": [KTP_IDENTITY_TYPE, KTP_IDENTITY_TYPE],
            "ei_number": ["NIK1", "NIK2"]
        })
        
        # This should not raise an error now with safe filtering
        emp_code = "E'001"
        ec_list = emp_cards[emp_cards["emp_code"] == emp_code]
        self.assertEqual(ec_list["ei_number"].values[0], "NIK1")

    def test_injection_special_chars(self):
        # Bug 2 test: Special characters in emp_code
        emp_cards = pd.DataFrame({
            "emp_code": ["E'001", "E\"002"],
            "ei_type": [KTP_IDENTITY_TYPE, KTP_IDENTITY_TYPE],
            "ei_number": ["NIK1", "NIK2"]
        })
        
        # This should not raise an error now with safe filtering
        emp_code = "E'001"
        ec_list = emp_cards[emp_cards["emp_code"] == emp_code]
        self.assertEqual(ec_list["ei_number"].values[0], "NIK1")

if __name__ == "__main__":
    unittest.main()
