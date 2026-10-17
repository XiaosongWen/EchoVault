# TASK-04 — Implement Project-Level Authorization

**Epic:** Epic 2: Authentication and Multi-User Project Isolation  
**Status:** Not started  
**Priority:** P0  
**Depends on:** TASK-03  
**Design refs:** `docs/EchoVault_BackEnd_Design.md` §3.2, T01–T02, T14  
**Notes:** Return 403 or a non-disclosing 404 so resource existence isn't leaked.

## TODO

- [ ] Implement project creation and project-list retrieval.
- [ ] Implement project membership management and permission checks.
- [ ] Enforce project-level authorization across all memory, revision-history, and transcript endpoints.
- [ ] Define permission rules for project owners, read-only members, and members with write access.

## Acceptance Criteria (ACs)

- Users can access only projects they own or are explicitly authorized to access.
- Cross-project read and write operations are rejected.
- Knowing a resource ID cannot bypass authorization checks.
- Every write operation performs server-side authorization.

---
See `docs/EchoVault-Implementation-Tasks.md` (cross-task requirements) and `docs/EchoVault_BackEnd_Design.md`.
