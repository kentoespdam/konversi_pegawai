import pytest
from pegawai import ambil_pegawai_dari_smartoffice

def test_ambil_pegawai_dari_smartoffice():
    pegawai_data = ambil_pegawai_dari_smartoffice()
    print(len(pegawai_data))
    assert len(pegawai_data) > 0


if __name__ == "__main__":
    pytest.main()
