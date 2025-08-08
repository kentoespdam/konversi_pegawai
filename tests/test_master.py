import unittest
from config import LOGGER
from core.kepegawaian.gaji_tunjangan import save_gaji_tunjangan
from core.smartoffice.sallary_allowance import (
    cleanup_sallary_allowance,
    fetch_sallary_allowance,
)


class TestMaster(unittest.TestCase):
    def test_master(self):
        LOGGER.debug("test master")
        master_tunjangan = fetch_sallary_allowance()
        # master_tunjangan.to_json("master_tunjangan_before.json", orient="records")
        master_tunjangan = cleanup_sallary_allowance(master_tunjangan)
        # master_tunjangan.to_json("master_tunjangan_after.json", orient="records")
        # LOGGER.debug(master_tunjangan.to_dict("records"))

        save_gaji_tunjangan(master_tunjangan)
        assert master_tunjangan["id"].size > 0
