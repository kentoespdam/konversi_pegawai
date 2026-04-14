---
name: Migration Scripts Index (v2_1–v2_17)
description: Compact index semua script migrasi — source/target table, kolom, join, cleanup logic, status optimasi
type: project
---

## Status Optimasi
- **Sudah dioptimasi**: v2_1, v2_2, v2_3, v2_4, v2_5, v2_6, v2_7
- **Issue dibuat, belum diimplementasi**: v2_8
- **Belum diaudit**: v2_9 sampai v2_17

## Index Per Script

### v2_1: emp_profile → biodata
- **Fetch**: `core/smartoffice/emp_profile.py::fetch_data_for_biodata()`
- **Source**: `emp_profile` LEFT JOIN `emp_education`(last_edu_flag=1), `sys_reference`, `employee`
- **Target**: `biodata` via `save_biodata_from_emp_profile()` + `kartu_identitas` via `save_kartu_identitas_from_emp_profile()`
- **Transform** (`transform_biodata`): tanggal_lahir→format_date, pendidikanTerakhir→pendidikan_id (dict map dari jenjang_pendidikan master), is_deleted→fillna(0).int, emp_flag→is_pegawai(.ne(0).int)
- **Save**: ON DUPLICATE KEY UPDATE (14 kolom), REPLACE INTO (biodata)

### v2_2: employee → pegawai
- **Fetch**: `core/smartoffice/eo_employee.py::fetch_employee_for_pegawai()`
- **Source**: `employee` INNER JOIN `emp_profile`, LEFT JOIN `position`, `organization`, `golongan`
- **Target**: `pegawai` via `save_pegawai_from_employee()` — **REPLACE INTO** (bukan ON DUPLICATE)
- **Transform** (`cleanup`): 6 date columns→format_date, namaOrganisasi→organisasi_id, namaJabatan→jabatan_id, golongan→golongan_id, jabatan_id→profesi_id+grade_id (dict map dari master tables), emp_tax_code→gaji_pendapatan_non_pajak_id, is_askes→eq('1'), is_deleted→eq(1)
- **Extra**: Juga fetch+update phdp via `update_pegawai_phdp()`

### v2_3: emp_card → kartu_identitas
- **Fetch**: `core/smartoffice/emp_card.py::fetch_emp_card_for_kartu_identitas()`
- **Source**: `emp_card` INNER JOIN `employee`, `emp_profile`, LEFT JOIN `sys_reference`(code='emp_card')
- **Target**: `kartu_identitas` via `save_kartu_identitas_from_emp_card()`
- **Transform** (`cleanup`): jenis_kitas→jenis_kitas_id (dict map dari jenis_kartu master), tanggal_expired→format_date, tanggal_terima→format_date, is_deleted→int

### v2_4: emp_skill → keahlian
- **Fetch**: `core/smartoffice/emp_skill.py::fetch_emp_skill_for_keahlian()`
- **Source**: `emp_skill` INNER JOIN `emp_profile`
- **Target**: `keahlian` via `save_keahlian_from_emp_skill()`
- **Transform** (`cleanup`): sertifikat→sertifikasi(.eq(1)), tanggal_pengajuan→format_date, tanggal_disetujui→format_date, disetujui→dynamic(tanggal_disetujui.notna() & .ne("")), status_raw→is_deleted(.eq(3))

### v2_5: emp_training → pelatihan
- **Fetch**: `core/smartoffice/emp_training.py::fetch_emp_training_for_pelatihan()`
- **Source**: `emp_training` INNER JOIN `emp_profile`
- **Kolom fetch**: biodata_id, jenis_pelatihan_id, nama, lembaga, tanggal_mulai, tanggal_selesai, lulus, nilai, ikatan_dinas, tanggal_akhir_ikatan, notes, tanggal_pengajuan, tanggal_disetujui, disetujui_oleh, is_deleted
- **Target**: `pelatihan` via `save_pelatihan_from_emp_training()` — ON DUPLICATE KEY UPDATE (14 kolom) + `updated_at=CURRENT_TIMESTAMP`
- **Transform** (`cleanup`): disetujui→dynamic(.notnull()), tanggal_mulai/selesai→format_date, ikatan_dinas→eq(1), tanggal_akhir_ikatan→format_date, tanggal_pengajuan/disetujui→format_datetime, is_deleted→eq(1), **NaN/NaT→None sanitization**

### v2_6: emp_education → pendidikan
- **Fetch**: `core/smartoffice/emp_education.py::fetch_emp_education_for_pendidikan()`
- **Source**: `emp_education` INNER JOIN `emp_profile`, LEFT JOIN `gelar_akademik`, `sys_reference`(code='pendidikan')
- **Kolom fetch**: edu_id, biodata_id, jenjang_pendidikan, gelar_belakang, jurusan, institusi, tahun_masuk, is_lulus, tahun_lulus, gpa, is_latest, tanggal_pengajuan, tanggal_disetujui, disetujui_oleh, is_deleted
- **Target**: `pendidikan` via `save_pendidikan_from_emp_education()` — ON DUPLICATE KEY UPDATE (14 kolom) + `updated_at=CURRENT_TIMESTAMP`
- **Transform** (`cleanup`): jenjang_pendidikan→jenjang_id (dict map dari jenjang_pendidikan master, default 0), is_lulus/is_latest/is_deleted→eq(1), gpa→str_to_float, tanggal_pengajuan/disetujui→format_datetime, disetujui→dynamic(.notnull()), **NaN/NaT→None sanitization**

### v2_7: emp_work_experience → pengalaman_kerja *(sudah dioptimasi)*
- **Fetch**: `core/smartoffice/emp_work_experience.py::fetch_emp_work_experience_for_pengalaman_kerja()`
- **Source**: `emp_work_experience` LEFT JOIN `bidang_perusahaan`, `emp_profile` (diubah dari INNER JOIN)
- **Kolom fetch**: ewe_id, biodata_id, nama_perusahaan, type_perusahaan, jabatan, lokasi, tahun_masuk, tahun_keluar, notes, is_deleted, tanggal_pengajuan, tanggal_disetujui
- **Target**: `pengalaman_kerja` via `save_pengalaman_kerja_from_emp_work_experience()` — TRUNCATE + INSERT (idempotency)
- **Transform** (`cleanup`): tanggal_pengajuan/disetujui→format_datetime, is_deleted→eq(1), tahun_masuk/keluar→replace(0,None), NaN/NaT sanitization, error handling, record logging

### v2_8: emp_family → profil_keluarga *(issue dibuat, belum diimplementasi)*
- **Fetch**: `core/smartoffice/emp_family.py::fetch_emp_family_for_profil_keluarga()`
- **Source**: `emp_family` INNER JOIN `emp_profile`, LEFT JOIN `sys_reference`(code='hub_keluarga')
- **Target**: `profil_keluarga` via `save_profil_keluarga_from_emp_profile()`
- **Transform** (`transform_family_df`): tanggal_lahir→format_date, tanggungan→eq(1), agama→default 1, status_pendidikan→vectorized masks (hubungan+umur), status_kawin→vectorized masks (hubungan), menggunakan `EHubunganKeluarga` enum
- **Issue doc**: `issues/v2_8_emp_family_to_profil_keluarga_plan.md` — 12 bugs: version column mismatch, nik/pendidikan_id tidak diisi, idempotency rusak (no unique key), masking status_kawin order bug, potential negative values dari -1 offset, no empty check, no error handling, no record logging, NaN/NaT tidak disanitasi

### v2_9_1: emp_work_history → emp_sk (init)
- **Fetch**: `emp_work_history` LEFT JOIN `emp_sk`(subquery), INNER JOIN `employee` — hanya NEW records (esk_no_sk IS NULL)
- **Target**: `emp_sk` (INSERT ke **source DB** smartoffice) via `save_emp_sk_from_emp_work_history()`
- **Transform** (`cleanup_init`): ref_id→default 0, status→default 1, notes→np.where conditional "Init Smartoffice"

### v2_9_2: emp_sk → riwayat_sk
- **Pre-step**: `update_init_smartoffice_no_sk()` — set blank no_sk ke "Init SmartOffice"
- **Fetch**: `emp_sk` INNER JOIN `employee`, `emp_profile`
- **Target**: `riwayat_sk` via `save_riwayat_sk_from_emp_sk()` — **Simple INSERT** (no ON DUPLICATE)
- **Transform** (`cleanup`): update_master→eq(1), is_deleted→eq(1)

### v2_10: emp_work_history → riwayat_mutasi
- **Complex multi-merge cleanup**: merge riwayat_sk→riwayat_sk_id, merge golongan, merge profesi (current+old)
- **JENIS_MUTASI_MAP**: {1→0, 2→1, 3→4, 4→6}
- **Filter**: hanya rows dengan riwayat_sk_id > 0
- **Target**: `riwayat_mutasi` — ON DUPLICATE KEY UPDATE pegawai_id only

### v2_11: emp_contract → riwayat_kontrak
- **Special logic**: pegawai_id lookup dengan preference status_kerja==2, sentinel "0000-00-00"→"1945-08-17", is_latest dari max(tanggal_sk) per nik, jenis_kontrak conditional (nipam prefix, status_kerja)

### v2_12: upd_emp_sk (update SK pegawai)
- **Fetch**: latest SK per pegawai via ROW_NUMBER() PARTITION BY
- **Split**: per jenis SK (CAPEG, JABATAN, KENAIKAN_PANGKAT_GOLONGAN, MUTASI, PEGAWAI_TETAP)
- **Target**: UPDATE `pegawai` — dynamic column based on jenis SK type

### v2_13: cuti_kuota
- Minimal: fetch → format expired date → save. Target: `cuti_kuota`

### v2_14: cuti_pegawai
- **Transform**: is_claimed logic (approved claims set), tanggal_mulai/selesai→format_date(default_date=True)
- Target: `cuti_pegawai`

### v2_15: cuti_approval_chain
- Minimal: fetch → save (no cleanup). Target: `cuti_approval_chain`

### v2_16: cuti_approval
- Inline: format created_at → save + update_approval_chain. Target: `cuti_approval`

### v2_17: cuti_klaim_detail
- Minimal: fetch → format tanggal → save. Target: `cuti_klaim_detail`

## Kolom Umum Target (pola berulang di tabel kepegawaian)
`biodata_id/pegawai_id`, `is_deleted`, `created_by('SYSTEM')`, `created_at`, `updated_at`, `disetujui`, `disetujui_oleh`, `tanggal_pengajuan`, `tanggal_disetujui`, `version(0)`, `notes`
