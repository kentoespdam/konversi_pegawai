import unittest
import pandas as pd
import numpy as np
import importlib.util
import os
import sys

# Workaround for importing module with dot in filename
module_path = os.path.abspath("v2/v2_1.emp_profile_to_biodata.py")
spec = importlib.util.spec_from_file_location("v2_1_module", module_path)
v2_1 = importlib.util.module_from_spec(spec)
sys.modules["v2.v2_1"] = v2_1
spec.loader.exec_module(v2_1)

class TestV2_1Migration(unittest.TestCase):
    def setUp(self):
        # Mock data for jenjang_pendidikan
        def mock_fetch_jenjang_pendidikan():
            return [
                {"id": 1, "nama": "S1"},
                {"id": 2, "nama": "S2"},
                {"id": 10, "nama": "SMA - Sederajat"}
            ]
        
        # Patch the fetch function in the module
        v2_1.fetch_jenjang_pendidikan = mock_fetch_jenjang_pendidikan
        self.DEFAULT_ID = v2_1.DEFAULT_ID

    def test_transform_biodata_logic(self):
        # Create test dataset with edge cases
        data = {
            "tanggal_lahir": ["1990-01-01", None],
            "pendidikanTerakhir": ["S1", "Unknown"],
            "is_deleted": [1, 0],
            "emp_flag": [1, None] # Bug 3: NULL should be handled
        }
        df = pd.DataFrame(data)
        
        # Execute transformation
        result_df = v2_1.transform_biodata(df)
        
        # Verify Bug 4: Mapping logic
        self.assertEqual(result_df.loc[0, "pendidikan_id"], 1)
        self.assertEqual(result_df.loc[1, "pendidikan_id"], self.DEFAULT_ID)
        
        # Verify Bug 6: Integer types
        self.assertEqual(result_df.loc[0, "is_deleted"], 1)
        self.assertEqual(result_df.loc[1, "is_deleted"], 0)
        self.assertTrue(np.issubdtype(result_df["is_deleted"].dtype, np.integer))
        
        # Verify Bug 3: emp_flag NULL handling
        self.assertEqual(result_df.loc[0, "is_pegawai"], 1)
        self.assertEqual(result_df.loc[1, "is_pegawai"], 0)
        self.assertTrue(np.issubdtype(result_df["is_pegawai"].dtype, np.integer))

    def test_empty_dataframe(self):
        # Verify Bug 2: Shouldn't crash on empty DataFrame
        df = pd.DataFrame(columns=["tanggal_lahir", "pendidikanTerakhir", "is_deleted", "emp_flag"])
        result_df = v2_1.transform_biodata(df)
        self.assertTrue(result_df.empty)

if __name__ == "__main__":
    unittest.main()
