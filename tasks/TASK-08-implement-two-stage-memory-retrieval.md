# TASK-08 — Implement Two-Stage Memory Retrieval

**Epic:** Epic 4: Memory Retrieval and MCP  
**Status:** Not started  
**Priority:** P0  
**Depends on:** TASK-05  
**Design refs:** `docs/EchoVault_BackEnd_Design.md` §4.4  
**Notes:** Enforce a token-budget cap (~1,000 tokens) on index pages.

## TODO

- [ ] Implement topic-index retrieval.
- [ ] Implement full-content retrieval by topic.
- [ ] Ensure the index returns only topics, descriptions, tags, and required pagination metadata.
- [ ] Support pagination, tag filtering, and keyword search.
- [ ] Implement a token-budget limit for index responses.

## Acceptance Criteria (ACs)

- Index responses do not include Markdown memory bodies.
- Full-content retrieval returns only the requested topic within the authorized project.
- A nonexistent topic returns `404 RESOURCE_NOT_FOUND`.
- Normal index responses target a maximum of 1,000 tokens; larger result sets can be paginated.

---
See `docs/EchoVault-Implementation-Tasks.md` (cross-task requirements) and `docs/EchoVault_BackEnd_Design.md`.
