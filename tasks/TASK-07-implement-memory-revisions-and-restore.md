# TASK-07 — Implement Memory Revisions and Restore

**Epic:** Epic 3: Memory Core API  
**Status:** Not started  
**Priority:** P0  
**Depends on:** TASK-05  
**Design refs:** `docs/EchoVault_BackEnd_Design.md` §4.3, §6, T13  
**Notes:** Update + revision snapshot must be one transaction. Restore creates a new version.

## TODO

- [ ] Record the previous memory version before each update.
- [ ] Implement the revision-history listing endpoint.
- [ ] Implement the historical revision restore endpoint.
- [ ] Ensure content updates and revision snapshots are committed atomically.

## Acceptance Criteria (ACs)

- Every successful update preserves a traceable previous version.
- Revision history is accessible only to users authorized to access the project.
- Restoring a historical revision creates a new version without deleting existing history.
- Failed updates do not leave inconsistent revision records.

---
See `docs/EchoVault-Implementation-Tasks.md` (cross-task requirements) and `docs/EchoVault_BackEnd_Design.md`.
