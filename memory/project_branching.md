---
name: Branching Strategy
description: Branch workflow — BUG-FIX-OPTIMIZE-V2 for bug fixes, v2 for development, main is remote default
type: project
---

- Branches: `main` (remote default) → `v2` (dev) → `BUG-FIX-OPTIMIZE-V2` (bug fixes/optimization)
- Bug fix work uses `BUG-FIX-OPTIMIZE-V2` as base, not `v2` or `main`
- User corrected this explicitly on 2026-04-13

**Why:** Specific branching workflow — bug fixes go through intermediate branch before v2.
**How to apply:** Use `BUG-FIX-OPTIMIZE-V2` as base branch for bug fix tasks in issue docs and git workflows.
