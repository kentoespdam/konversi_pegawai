from pandas import DataFrame
from pegawai import ambil_pegawai_dari_smartoffice


data: DataFrame = ambil_pegawai_dari_smartoffice()
golongans = data["golonganId"]
print(len(golongans))
golongans.drop_duplicates(inplace=True)
golongans.dropna(inplace=True)
# make golongans to list
golongans = list(golongans)
print(golongans)