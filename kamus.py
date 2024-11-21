def replace_agama(agamaId):
    switcher = {
        1: "ISLAM",
        2: "KRISTEN",
        3: "KATOLIK",
        4: "HINDU",
        5: "BUDHA",
        6: "LAINNYA",
        7: "LAINNYA",
        99: "TIDAK_TAHU"
    }
    return switcher.get(agamaId)


def replace_status_kawin(statusKawinId: int):
    switcher = {
        1: "BELUM_KAWIN",
        2: "KAWIN",
        3: "JANDA_DUDA",
        4: "MENIKAH_SEKANTOR",
        99: "TIDAK_TAHU"
    }
    return switcher.get(statusKawinId)
    # return result


def replace_status_pegawai(statusPegawaiId: int):
    switcher = {
        1: "PEGAWAI",
        2: "KONTRAK",
        3: "NON_PEGAWAI",
        4: "CAPEG",
        5: "HONORER",
        6: "CALON_HONORER"
    }
    return switcher.get(statusPegawaiId)


def replace_status_kerja(statusKerjaId: int):
    switcher = {
        1: "LAMARAN_BARU",
        2: "TAHAP_SELEKSI",
        3: "DITERIMA",
        4: "DIREKOMENDASIKAN",
        5: "DITOLAK",
        6: "KARYAWAN_AKTIF",
        7: "DIRUMAHKAN",
        8: "BERHENTI_OR_KELUAR"
    }
    return switcher.get(statusKerjaId)
