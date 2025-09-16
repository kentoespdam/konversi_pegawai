import time
from core.kepegawaian.kepeg_gaji_pendapatan_non_pajak import fetch_all_gaji_pendapatan_non_pajak
from core.kepegawaian.kepeg_pegawai import fetch_all_pegawai
from core.post_data import do_patch
from core.smartoffice.eo_employee import fetch_data_for_profil_gaji
import pandas as pd
import concurrent.futures
from icecream import ic
import swifter


def main():
    start_time = time.time()
    profil_gaji_df = fetch_data_for_profil_gaji()
    emp_df = pd.DataFrame(fetch_all_pegawai())
    profil_gaji_df["tmtKerja"] = profil_gaji_df["tmtKerja"].swifter.apply(
        lambda x: x.strftime('%Y-%m-%d') if x is not None else "")
    profil_gaji_df["tmtPensiun"] = profil_gaji_df["tmtPensiun"].swifter.apply(
        lambda x: x.strftime('%Y-%m-%d') if x is not None else "")
    profil_gaji_df["isAskes"] = profil_gaji_df["isAskes"].swifter.apply(
        lambda x: True if x == 1 else False)
    profil_gaji_df["pegawaiId"] = profil_gaji_df["nipam"].swifter.apply(
        lambda x: get_pegawai_id(x, emp_df)
    )
    gaji_pendapatan_non_pajak_df = pd.DataFrame(
        fetch_all_gaji_pendapatan_non_pajak())
    profil_gaji_df["kodePajakId"] = profil_gaji_df["kodePajak"].swifter.apply(
        lambda x: get_gaji_pendapatan_non_pajak_id(
            x, gaji_pendapatan_non_pajak_df)
    )
    profil_gaji_df.mask(profil_gaji_df.isna(), 0, inplace=True)
    profil_gaji_df.drop(columns=["nipam", "kodePajak"], inplace=True)
    # ic(profil_gaji_df.to_dict(orient="records"))
    ic(f"generating data finish in {time.time()-start_time}s")

    start_time = time.time()
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        executor.map(patch_data, [row for row in profil_gaji_df.itertuples()])
    ic(f"posting data finish in {time.time()-start_time}s")


def get_pegawai_id(nipam: str, emp_df: pd.DataFrame):
    result = emp_df.query("nipam==@nipam").reset_index(drop=True)
    return result.id.values[0] if not result.empty else 0


def get_gaji_pendapatan_non_pajak_id(kode: str, df: pd.DataFrame):
    result = df.query("kode==@kode").reset_index(drop=True)
    return result.id.values[0] if not result.empty else 0


def patch_data(row: dict):
    try:
        payload = {
            "pegawaiId": row.pegawaiId,
            "tmtKerja": row.tmtKerja,
            "tmtPensiun": row.tmtPensiun,
            "statusPegawai": row.statusPegawai,
            "gajiPokok": row.gajiPokok,
            "phdp": row.phdp,
            "isAskes": row.isAskes,
            "kodePajakId": row.kodePajakId,
            "gajiProfilId": row.gajiProfilId,
            "rumahDinasId": row.rumahDinasId
        }
        do_patch(f"pegawai/{row.pegawaiId}/gaji", payload)
    except Exception as e:
        ic(e)


if __name__ == "__main__":
    main()
