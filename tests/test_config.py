import unittest
from unittest.mock import patch, MagicMock
import os
import sys

# Add project root to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from core.config import (
    get_smartoffice_connection_pool,
    get_kepegawaian_connection_pool,
    _do_save_update,
    _get_fetch_result
)

class TestConfig(unittest.TestCase):
    def test_singleton_pools(self):
        # Verify that multiple calls return connections from the same pool type
        conn1 = get_smartoffice_connection_pool()
        conn2 = get_smartoffice_connection_pool()
        
        # In pymysqlpool, the context manager returns a connection
        # We can check if the pool object is the same if we could access it,
        # but since it's private in our implementation, we can verify it doesn't re-log "Initializing..."
        # or we can check the pool instance if we expose it (we didn't).
        
        # Test connection retrieval doesn't crash
        self.assertIsNotNone(conn1)
        self.assertIsNotNone(conn2)
        
        # Close connections
        conn1.close()
        conn2.close()

    @patch("core.config.LOGGER")
    def test_save_update_error_handling(self, mock_logger):
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
        
        # Simulate error during execution
        mock_cursor.executemany.side_effect = Exception("Test DB Error")
        
        with self.assertRaises(Exception) as cm:
            _do_save_update(mock_conn, "INSERT INTO table VALUES (%s)", [("data",)])
        
        self.assertEqual(str(cm.exception), "Test DB Error")
        mock_conn.rollback.assert_called_once()
        # Verify FK checks restoration
        mock_cursor.execute.assert_any_call("SET FOREIGN_KEY_CHECKS=0")
        mock_cursor.execute.assert_any_call("SET FOREIGN_KEY_CHECKS=1")

    def test_fetch_result_none_check(self):
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
        mock_cursor.description = [("id",), ("name",)]
        mock_cursor.fetchall.return_value = [(1, "test")]
        
        import pandas as pd
        
        # Test with where=None
        df = _get_fetch_result(mock_conn, "SELECT * FROM table", where=None)
        mock_cursor.execute.assert_called_with("SELECT * FROM table")
        self.assertIsInstance(df, pd.DataFrame)
        self.assertEqual(len(df), 1)
        
        # Test with where=(1,)
        df = _get_fetch_result(mock_conn, "SELECT * FROM table WHERE id=%s", where=(1,))
        mock_cursor.execute.assert_called_with("SELECT * FROM table WHERE id=%s", (1,))

if __name__ == "__main__":
    unittest.main()
