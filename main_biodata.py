import core.kamus as kamus
from smartoffice.biodata import ambil_biodata_dari_smartoffice
from core.post_data import kirim_biodata
import concurrent.futures
from icecream import ic
import sys


def manipulate_biodata():
    bio = ambil_biodata_dari_smartoffice()
    # bio["id"] = bio["id"].apply(lambda x: None)
    bio["jenisKelamin"] = bio["jenisKelamin"].apply(
        lambda x: "LAKI_LAKI" if x == "Pria" else "PEREMPUAN")
    bio["agama"] = bio["agama"].apply(lambda x: kamus.replace_agama(x))
    bio["statusKawin"] = bio["statusKawin"].apply(
        lambda x: kamus.replace_status_kawin(x))
    return bio


def main():
    bio = manipulate_biodata()
    bio.drop(["id"], axis=1, inplace=True)
    # for index, row in bio.iterrows():
    #     kirim_biodata(row)
    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = {executor.submit(kirim_biodata, row): row for index, row in bio.iterrows()}

        for future in concurrent.futures.as_completed(futures):
            hasil=futures[future]
            result=future.result()
            ic(result)


if __name__ == '__main__':
    main()
