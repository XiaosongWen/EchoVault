# TASK-10 — Integrate Browser Extension Write API

**Epic:** Epic 5: Browser Extension and Dashboard  
**Status:** Not started  
**Priority:** P0  
**Depends on:** TASK-03, TASK-05  
**Design refs:** `docs/EchoVault_BackEnd_Design.md` §4.2, §3.1  
**Notes:** Duplicate topics return 409 `TOPIC_ALREADY_EXISTS`; no silent overwrite.

## TODO

- [ ] Provide a memory-creation API for the browser extension.
- [ ] Support `project_id`, `topic`, `description`, `tags`, and `content`.
- [ ] Validate project permissions and request formats.
- [ ] Define conflict handling for duplicate topics.
- [ ] Provide API documentation for browser-extension developers.

## Acceptance Criteria (ACs)

- The browser extension can write memories through the REST API.
- A successful response confirms that the memory has been durably persisted.
- Unauthorized access, invalid parameters, and duplicate topics return clear errors.
- Newly written memories are available through the Dashboard and MCP.

---
See `docs/EchoVault-Implementation-Tasks.md` (cross-task requirements) and `docs/EchoVault_BackEnd_Design.md`.
