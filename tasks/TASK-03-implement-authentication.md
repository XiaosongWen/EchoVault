# TASK-03 — Implement Authentication

**Epic:** Epic 2: Authentication and Multi-User Project Isolation  
**Status:** Not started  
**Priority:** P0  
**Depends on:** TASK-01, TASK-02  
**Design refs:** `docs/EchoVault_BackEnd_Design.md` §3.1  
**Notes:** Never trust a client-supplied `user_id`; background workers use their own service identity.

## TODO

- [ ] Integrate Supabase Auth or an equivalent OIDC authentication provider.
- [ ] Implement access-token validation.
- [ ] Define controlled credential-based access for the browser extension, CLI, and MCP clients.
- [ ] Implement API key revocation and rotation.

## Acceptance Criteria (ACs)

- Valid access tokens can access protected endpoints.
- Missing, invalid, or expired tokens return `401 UNAUTHORIZED`.
- API keys grant only the permissions within their authorized scopes.
- Logs and error responses never expose authentication credentials.

---
See `docs/EchoVault-Implementation-Tasks.md` (cross-task requirements) and `docs/EchoVault_BackEnd_Design.md`.
