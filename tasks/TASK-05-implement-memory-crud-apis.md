# TASK-05 — Implement Memory CRUD APIs

**Epic:** Epic 3: Memory Core API  
**Status:** Not started  
**Priority:** P0  
**Depends on:** TASK-04  
**Design refs:** `docs/EchoVault_BackEnd_Design.md` §4.1, §4.2, §4.4  
**Notes:** Index responses must exclude `content`. Business logic lives in `services/` so MCP can reuse it.

## TODO

- [ ] Implement memory creation: `POST /projects/{project_id}/memories`.
- [ ] Implement memory listing: `GET /projects/{project_id}/memories`.
- [ ] Implement memory detail retrieval: `GET /memories/{memory_id}`.
- [ ] Implement memory updates: `PATCH /memories/{memory_id}`.
- [ ] Implement memory deletion: `DELETE /memories/{memory_id}`.
- [ ] Support pagination, tag filtering, and keyword search.
- [ ] Standardize request validation and error responses.

## Acceptance Criteria (ACs)

- All CRUD operations enforce project-level authorization.
- Creating a duplicate topic returns `409 TOPIC_ALREADY_EXISTS`.
- List endpoints support pagination and do not return full memory content by default.
- After deletion, the memory no longer appears in normal list or retrieval responses.
- Invalid requests return identifiable error codes.

---
See `docs/EchoVault-Implementation-Tasks.md` (cross-task requirements) and `docs/EchoVault_BackEnd_Design.md`.
