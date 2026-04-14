# Project Memory & Context Index

This file serves as a compact overview of the project context. Detailed documentation is split into the `memory/` directory to prevent this file from becoming too large. Please refer to those files for specific requirements.

## 🗂️ Core Knowledge Base

- **[Main Index](memory/MEMORY.md)**
- **[Active Work Items](memory/project_active_work.md)**: Current migration state, fixed bugs, and next targets (Currently: implement `v2_8`, audit `v2_9+`).
- **[Architecture & ETL](memory/project_architecture.md)**: Rules for 3-layer ETL, Pandas usage, raw SQL (pymysql), connection pooling, and helpers.
- **[Migration Index](memory/project_migration_index.md)**: Breakdown of migration scripts `v2_1` through `v2_17`.
- **[Bug Patterns](memory/project_bug_patterns.md)**: 12 recurring bug patterns and best practices for DataFrame mapping, NaN sanitization, idempotency, and logging.
- **[Database Schema](memory/project_db_schema.md)**: Reference for source (`smartoffice`) and target (`kepegawaian_migrasi`) structures.
- **[Feedback & Style](memory/feedback_docs_style.md)**: Rules for writing documentation and migration plans (Indonesian, high-level).
- **[Issue Template](memory/project_issue_template.md)**: Template for new issue generation.
- **[Branching Strategy](memory/project_branching.md)**: Workflow standard (`BUG-FIX-OPTIMIZE-V2` → `v2` → `master`).
- **[User Profile](memory/user_profile.md)**: User preferences and delegation structure.

*Note: Keep this file compact. If expanding project knowledge, create new segmented markdown files in the `memory/` directory and link them here.*
