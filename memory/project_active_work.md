---
name: Active Work Items
description: Current project state and recent work as of 2026-04-14
type: project
---

**Completed (since last update):**
- Issue #001 set_nik bugs fixed (commit `0057902`)
- Issue #002 config optimization — singleton connection pools, env validation, DB retry logic (commit `ac81cab`)
- v2_2 employee_to_pegawai — optimized memory usage, vectorized mapping, removed redundant DataFrame copies (commit `f625043`)
- v2_3 kartu_identitas — vectorized data mapping, fixed type casting, added error handling (commit `679388e`)
- v2_4 keahlian + v2_5 pelatihan — robust error handling, dynamic upsert logic, null sanitization (commits `bf20a1b`, `89d4497`)
- Plan docs created for v2_2 through v2_5 in `issues/`
- v2_6 pendidikan — plan/issue doc created, code optimized (commit `673ecd5`)
- v2_7 pengalaman_kerja — plan/issue doc created (`issues/v2_7_emp_work_experience_to_pengalaman_kerja_plan.md`), **code implemented and optimized** (12 bugs fixed: version column removed, INNER→LEFT JOIN, missing columns added, idempotency via TRUNCATE, NaN sanitization, error handling, record logging)
- v2_8 emp_family_to_profil_keluarga — plan/issue doc created (`issues/v2_8_emp_family_to_profil_keluarga_plan.md`), 12 bugs identified. **Code fix NOT YET implemented.**

**Open issues:**
- `issues/001-bug-review-v2_1-emp-profile-to-biodata.md` — review/fix bugs in v2_1 biodata conversion
- `issues/v2_8_emp_family_to_profil_keluarga_plan.md` — 12 bugs, code fix pending
- Migration scripts v2_9 through v2_17 not yet audited

**Working tree:** clean (as of 2026-04-14)

**Why:** Prevents duplicate effort across sessions.
**How to apply:** Check before starting new work. Next target: implement v2_8 fixes, then audit v2_9+ scripts.
