import unittest
import pandas as pd
from v2.v2_helper import str_to_float_series, str_to_float, format_date_series, format_datetime_series

class TestV2Helper(unittest.TestCase):
    
    def test_str_to_float_series(self):
        # European format
        s = pd.Series(["1.250.500,50", "1.500", "500,25"])
        expected = pd.Series([1250500.5, 1500.0, 500.25])
        pd.testing.assert_series_equal(str_to_float_series(s), expected)
        
        # Edge cases and placeholders
        s = pd.Series(["-", "", "None", "nan", None])
        expected = pd.Series([0.0, 0.0, 0.0, 0.0, 0.0])
        pd.testing.assert_series_equal(str_to_float_series(s), expected)
        
        # Mixed and invalid
        s = pd.Series(["1,23", "abc", "10.000"])
        expected = pd.Series([1.23, 0.0, 10000.0])
        pd.testing.assert_series_equal(str_to_float_series(s), expected)

    def test_str_to_float_scalar(self):
        self.assertEqual(str_to_float("1.250.500,50"), 1250500.5)
        self.assertEqual(str_to_float("-"), 0.0)
        self.assertEqual(str_to_float(""), 0.0)
        self.assertEqual(str_to_float(None), 0.0)
        self.assertEqual(str_to_float(123), 123.0)
        self.assertEqual(str_to_float(123.45), 123.45)

    def test_format_date_series(self):
        s = pd.Series(["2023-01-01", "01/01/2023", "invalid", None])
        
        # Without default date
        expected = pd.Series(["2023-01-01", "2023-01-01", None, None], dtype=object)
        # Note: we need to handle the fact that pd.to_datetime might be smart about formats
        result = format_date_series(s)
        pd.testing.assert_series_equal(result, expected)
        
        # With default date
        expected_default = pd.Series(["2023-01-01", "2023-01-01", "1945-08-17", "1945-08-17"], dtype=object)
        result_default = format_date_series(s, default_date=True)
        pd.testing.assert_series_equal(result_default, expected_default)

    def test_format_datetime_series(self):
        s = pd.Series(["2023-01-01 12:00:00", "2023-01-01", "invalid", None])
        expected = pd.Series(["2023-01-01 12:00:00", "2023-01-01 00:00:00", None, None], dtype=object)
        result = format_datetime_series(s)
        pd.testing.assert_series_equal(result, expected)

if __name__ == '__main__':
    unittest.main()
