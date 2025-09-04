import unittest
from core.config import LOGGER
from core.smartoffice.eo_salary_allowance import (
    cleanup_salary_allowance,
    fetch_salary_allowance,
)


class TestMaster(unittest.TestCase):
    def test_master(self):
        LOGGER.debug("test master")
        master_tunjangan = fetch_salary_allowance()
        master_tunjangan.to_json("master_tunjangan_before.json", orient="records")
        master_tunjangan = cleanup_salary_allowance(master_tunjangan)
        master_tunjangan.to_json("master_tunjangan_after.json", orient="records")
        # LOGGER.debug(master_tunjangan.to_dict("records"))

        # save_gaji_tunjangan(master_tunjangan)
        assert master_tunjangan["id"].size > 0
