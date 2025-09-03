import unittest
from unittest.mock import patch, MagicMock

from main_v2 import main
from v2.set_nik_pegawai import CleanupNikEmpProfile


class TestMainV2(unittest.TestCase):
    @patch('v2.set_nik_pegawai.CleanupNikEmpProfile')
    def test_main_runs_cleanup_nik_employee_profile(self, MockCleanupNikEmpProfile):
        mock_instance = MagicMock()
        MockCleanupNikEmpProfile.return_value = mock_instance

        main()

        MockCleanupNikEmpProfile.assert_called_once()
        mock_instance.run.assert_called_once()


if __name__ == '__main__':
    unittest.main()
