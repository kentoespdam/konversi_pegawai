import pandas as pd

from core.config import save_update_kepegawaian


def save_riwayat_mutasi_from_emp_work_history(df: pd.DataFrame):
    data = [(
        row.pegawai_id,
        row.nipam,
        row.nama,
        row.riwayat_sk_id,
        row.tmt_berlaku,
        row.tanggal_berakhir,
        row.jenis_mutasi,
        row.organisasi_id if row.organisasi_id > 0 else None,
        row.nama_organisasi,
        row.jabatan_id if row.jabatan_id > 0 else None,
        row.nama_jabatan,
        row.profesi_id if row.profesi_id > 0 else None,
        row.nama_profesi,
        row.golongan_id if row.golongan_id > 0 else None,
        row.nama_golongan,
        row.golongan_lama_id if hasattr(row, 'golongan_lama_id') and row.golongan_lama_id > 0 else None,
        row.nama_golongan_lama if hasattr(row, 'nama_golongan_lama') else None,
        row.organisasi_lama_id if row.organisasi_lama_id > 0 else None,
        row.nama_organisasi_lama,
        row.jabatan_lama_id if row.jabatan_lama_id > 0 else None,
        row.nama_jabatan_lama,
        row.profesi_lama_id if row.profesi_lama_id > 0 else None,
        row.nama_profesi_lama,
        row.is_deleted,
        row.notes,
        'SYSTEM'
    ) for row in df.itertuples(index=False)]
    query = """
            INSERT INTO riwayat_mutasi (pegawai_id, nipam, nama, riwayat_sk_id, tmt_berlaku,
                                        tanggal_berakhir, jenis_mutasi, organisasi_id, nama_organisasi, jabatan_id,
                                        nama_jabatan, profesi_id, nama_profesi, golongan_id, nama_golongan,
                                        golongan_lama_id, nama_golongan_lama, 
                                        organisasi_lama_id, nama_organisasi_lama, jabatan_lama_id, nama_jabatan_lama,
                                        profesi_lama_id, nama_profesi_lama, is_deleted, notes, created_by)
            VALUES (%s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE 
                nipam=VALUES(nipam),
                nama=VALUES(nama),
                tmt_berlaku=VALUES(tmt_berlaku),
                tanggal_berakhir=VALUES(tanggal_berakhir),
                jenis_mutasi=VALUES(jenis_mutasi),
                organisasi_id=VALUES(organisasi_id),
                nama_organisasi=VALUES(nama_organisasi),
                jabatan_id=VALUES(jabatan_id),
                nama_jabatan=VALUES(nama_jabatan),
                profesi_id=VALUES(profesi_id),
                nama_profesi=VALUES(nama_profesi),
                golongan_id=VALUES(golongan_id),
                nama_golongan=VALUES(nama_golongan),
                golongan_lama_id=VALUES(golongan_lama_id),
                nama_golongan_lama=VALUES(nama_golongan_lama),
                organisasi_lama_id=VALUES(organisasi_lama_id),
                nama_organisasi_lama=VALUES(nama_organisasi_lama),
                jabatan_lama_id=VALUES(jabatan_lama_id),
                nama_jabatan_lama=VALUES(nama_jabatan_lama),
                profesi_lama_id=VALUES(profesi_lama_id),
                nama_profesi_lama=VALUES(nama_profesi_lama),
                is_deleted=VALUES(is_deleted),
                notes=VALUES(notes),
                updated_at=CURRENT_TIMESTAMP
            """

    save_update_kepegawaian(query, data)
