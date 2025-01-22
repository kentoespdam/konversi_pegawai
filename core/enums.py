from enum import Enum


class EHubunganKeluarga(Enum):
    SUAMI = 0
    ISTRI = 1
    AYAH = 2
    IBU = 3
    ANAK = 4
    SAUDARA = 5


class EJenisGaji(Enum):
    NONE = 0
    PEMASUKAN = 1
    POTONGAN = 2


class EJenisKontrak(Enum):
    PERPANJANGAN = 0
    PENGANGKATAN = 1


class EJenisLampiranProfil(Enum):
    PROFIL_KELUARGA = 0
    PROFIL_PENDIDIKAN = 1
    PROFIL_PELATIHAN = 2
    PROFIL_KEAHLIAN = 3
    FOTO_PROFIL = 4
    KARTU_IDENTITAS = 5
    PROFIL_PENGALAMAN_KERJA = 6


class EJenisMutasi(Enum):
    PENGANGKATAN_PERTAMA = 0
    MUTASI_LOKER = 1
    MUTASI_JABATAN = 2
    MUTASI_GOLONGAN = 3
    MUTASI_GAJI = 4
    MUTASI_GAJI_BERKALA = 5
    TERMINASI = 6


class EmpFlag(Enum):
    PegawaiTetap = 1
    PegawaiKontrak = 2
    NonPegawai = 3
    CalonPegawai = 4
    HonorerTetap = 5
    CalonHonorerTetap = 6


class EStatusPegawai(Enum):
    KONTRAK = 0
    CAPEG = 1
    PEGAWAI = 2
    CALON_HONORER = 3
    HONORER = 4
    NON_PEGAWAI = 5


class EmpWorkStatus(Enum):
    LamaranBaru = 1
    TahapSeleksi = 2
    Diterima = 3
    Direkomendasikan = 4
    Ditolak = 5
    KaryawanAktif = 6
    Dirumahkan = 7
    BerhentiOrKeluar = 8


class EStatusKerja(Enum):
    BERHENTI_OR_KELUAR = 0
    DIRUMAHKAN = 1
    KARYAWAN_AKTIF = 2
    LAMARAN_BARU = 3
    TAHAP_SELEKSI = 4
    DITERIMA = 5
    DIREKOMENDASIKAN = 6
    DITOLAK = 7
