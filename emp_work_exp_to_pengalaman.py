import concurrent.futures
import concurrent
import time
import pandas as pd
from icecream import ic
from core.post_data import do_post
from dotenv import load_dotenv

from core.smartoffice.emp_work_experience import fetch_data_for_pengalaman_kerja

load_dotenv()

def main():
    start_time = time.time()
    work_exp_df = pd.DataFrame(fetch_data_for_pengalaman_kerja())
    ic(f"generating data finish in {time.time()-start_time}s")
    
    start_time = time.time()
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        executor.map(post_data, [row for row in work_exp_df.itertuples()])
    ic(f"posting data finish in {time.time()-start_time}s")
    
        
def post_data(row):
    payload={
        "biodataId": row.biodataId,
        "namaPerusahaan": row.namaPerusahaan,
        "typePerusahaan": row.typePerusahaan,
        "jabatan": row.jabatan,
        "lokasi": row.lokasi,
        "tanggalMasuk": row.tanggalMasuk,
        "tanggalKeluar": row.tanggalKeluar,
        "notes": row.notes   
    }
    
    do_post("profil/pengalaman", payload)

    
if __name__ == "__main__":
    main()