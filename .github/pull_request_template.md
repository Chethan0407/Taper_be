# PR Checklist: Alembic Migration Protocol

- [ ] **Backup taken** (pg_dump before migration)
- [ ] **Dry-run SQL generated and reviewed** (`alembic upgrade head --sql > preview.sql`)
- [ ] **No destructive operations** (drop_table/drop_column) unless reviewed/approved
- [ ] **Migration logged in docs/migration-log.md or Notion**
- [ ] **Peer review completed** (second dev)
- [ ] **Destructive changes approved by founder**
- [ ] **Tested locally with sample data**

---

_This checklist is required for all DB migration PRs. No exceptions._ 