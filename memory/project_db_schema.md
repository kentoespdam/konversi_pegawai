---
name: DB Schema Reference (Source & Target)
description: Compact reference tabel source smartoffice dan target kepegawaian — kolom, relasi, pola umum
type: reference
---

## Source DB: `smartoffice`

### Tabel Utama
| Tabel | Kolom Kunci | Relasi |
|-------|------------|--------|
| `emp_profile` | emp_profile_id (PK), emp_identity_number (NIK) | Parent semua emp_* |
| `employee` | emp_id, emp_code, emp_profile_id (FK), pos_id, org_id, gol_id | Master pegawai |
| `emp_card` | ei_id, emp_code (FK→employee) | Kartu identitas |
| `emp_skill` | es_id, emp_profile_id (FK) | Keahlian |
| `emp_training` | et_id, emp_profile_id (FK) | Pelatihan |
| `emp_education` | eed_id, emp_profile_id (FK), gelar_id | Pendidikan |
| `emp_work_experience` | ewe_id, emp_profile_id (FK), ewe_company_type (FK→bidang_perusahaan) | Pengalaman kerja |
| `emp_family` | ef_id, emp_profile_id (FK), fam_relation (FK→sys_reference) | Keluarga |
| `emp_sk` | esk_id, emp_id (FK→employee) | Surat keputusan |
| `emp_work_history` | ewh_id, emp_code (FK→employee) | Riwayat mutasi |
| `emp_contract` | ec_id, emp_code (FK→employee), pos_id | Kontrak |

### Tabel Referensi
| Tabel | Kegunaan |
|-------|----------|
| `bidang_perusahaan` | id, nama_bidang — tipe perusahaan |
| `sys_reference` | code, value, name — referensi dinamis (emp_card, pendidikan, hub_keluarga, keahlian, kualifikasi_keahlian) |
| `position` | pos_id, pos_name — jabatan |
| `organization` | org_id, org_name — organisasi |
| `golongan` | gol_id, golongan, pangkat |
| `gelar_akademik` | id, singkatan — gelar belakang |
| `salary_non_taxable_income` | id, sni_code — kode pajak |
| `salary_allowance` | id, jenis_tunjangan — tunjangan |
| `salary_tkk_reduction` | id, status_pegawai — potongan TKK |
| `cuti_*` | Tabel-tabel cuti (kuota, pegawai, approval, detail) |

### Pola Umum Source
- **Status deletion**: `*_status = 3` → is_deleted (berlaku di emp_card, emp_skill, emp_training, emp_education, emp_work_experience, emp_work_history, emp_contract)
- **Approval**: kolom `approve_date` + `approve_by` (ada di emp_training, emp_education, emp_work_experience, emp_skill)
- **Entry**: kolom `*_entry_date` + `*_entry_by_name`

## Target DB: `kepegawaian_migrasi`

### Tabel Target
| Tabel | Dari Script | PK | Unique Key | Kolom Approval |
|-------|-------------|-----|------------|----------------|
| `biodata` | v2_1 | id (auto) | nik | - |
| `pegawai` | v2_2 | id (auto) | nipam | - |
| `kartu_identitas` | v2_1, v2_3 | id (auto) | (nik+jenis?) | - |
| `keahlian` | v2_4 | id (auto) | ? | disetujui, tanggal_pengajuan, tanggal_disetujui |
| `pelatihan` | v2_5 | id (auto) | ? | disetujui, tanggal_pengajuan, tanggal_disetujui, disetujui_oleh |
| `pendidikan` | v2_6 | id (auto) | ? | disetujui, tanggal_pengajuan, tanggal_disetujui, disetujui_oleh |
| `pengalaman_kerja` | v2_7 | id (auto) | **TIDAK ADA** | disetujui, tanggal_pengajuan, tanggal_disetujui, disetujui_oleh |
| `profil_keluarga` | v2_8 | id (auto) | ? | - |
| `riwayat_sk` | v2_9_2 | id (auto) | ? | - |
| `riwayat_mutasi` | v2_10 | id (auto) | ? | - |
| `riwayat_kontrak` | v2_11 | id (auto) | ? | - |
| `cuti_kuota` | v2_13 | id (auto) | ? | - |
| `cuti_pegawai` | v2_14 | id (auto) | ? | - |
| `cuti_approval_chain` | v2_15 | id (auto) | ? | - |
| `cuti_approval` | v2_16 | id (auto) | ? | - |
| `cuti_klaim_detail` | v2_17 | id (auto) | ? | - |

### Kolom Standar Target (ada di hampir semua tabel)
```
id           BIGINT(20) PK auto_increment
created_at   TIMESTAMP  DEFAULT current_timestamp()
created_by   VARCHAR(255)
updated_at   TIMESTAMP  DEFAULT current_timestamp() ON UPDATE current_timestamp()
updated_by   VARCHAR(255)
is_deleted   TINYINT(1) DEFAULT 0
biodata_id   VARCHAR(255) — FK ke biodata (atau pegawai_id ke pegawai)
notes        VARCHAR(255)
```

### Kolom Approval (ada di pelatihan, pendidikan, keahlian, pengalaman_kerja)
```
disetujui          TINYINT(1) DEFAULT 0
disetujui_oleh     VARCHAR(255)
tanggal_pengajuan  DATETIME(6)
tanggal_disetujui  DATETIME(6)
```

### Tips Audit Schema
- Selalu jalankan `DESCRIBE <table>` sebelum menulis issue — kolom bisa berbeda dari asumsi
- Cek `SHOW INDEX FROM <table> WHERE Non_unique = 0` untuk unique key
- Jika tabel **hanya punya PK auto-increment** tanpa unique key → ON DUPLICATE KEY UPDATE tidak berfungsi → perlu strategi TRUNCATE atau unique constraint
- Kolom `version` **TIDAK ada** di semua tabel (ditemukan absen di pengalaman_kerja, perlu dicek per tabel)
