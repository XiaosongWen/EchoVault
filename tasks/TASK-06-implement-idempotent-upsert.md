# TASK-06 — Implement Idempotent Upsert

**Epic:** Epic 3: Memory Core API  
**Status:** Not started  
**Priority:** P0  
**Depends on:** TASK-05  
**Design refs:** `docs/EchoVault_BackEnd_Design.md` §4.5, §6  
**Notes:** Extraction writes must go through the merge workflow (TASK-14), never directly bypass version checks.

## TODO

- [ ] Implement memory upsert using `(project_id, topic)` as the lookup key.
- [ ] Support `expected_version`.
- [ ] Handle duplicate requests and concurrent writes.
- [ ] Distinguish direct user writes from AI-generated extraction writes.

## Acceptance Criteria (ACs)

- The same project and topic cannot produce duplicate memory records.
- Retrying the same idempotent request does not create duplicate memories.
- Version mismatches return `409 VERSION_CONFLICT`.
- Automated extraction cannot bypass the automatic merge workflow or version protection.

---
See `docs/EchoVault-Implementation-Tasks.md` (cross-task requirements) and `docs/EchoVault_BackEnd_Design.md`.
