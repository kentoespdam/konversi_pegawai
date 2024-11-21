import concurrent
import time
from kepegawaian.master import find_golongan_id
from pegawai import ambil_pegawai_dari_smartoffice
from pandas import DataFrame
from icecream import ic

from post_data import kirim_pegawai


def main() -> None:
    """Send pegawai data from SmartOffice to the PAMS API."""
    start = time.time()
    pegawai_data = ambil_pegawai_dari_smartoffice()
    ic(len(pegawai_data))
    pegawai_data.to_json("pegawai.json", orient="records", date_format="iso")
    ic(time.time()-start)
    # with concurrent.futures.ThreadPoolExecutor() as executor:
    #     futures = {
    #         executor.submit(kirim_pegawai, row): row
    #         for index, row in pegawai_data.iterrows()
    #     }

    #     for future in concurrent.futures.as_completed(futures):
    #         try:
    #             future.result()
    #         except Exception as e:
    #             print(f"Error sending pegawai data: {e}")


if __name__ == '__main__':
    main()
