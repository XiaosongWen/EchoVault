# TASK-02 — Set Up Supabase and Database Migrations

**Epic:** Epic 1: Project Initialization and Infrastructure  
**Status:** Not started  
**Priority:** P0  
**Depends on:** TASK-01  
**Design refs:** `docs/EchoVault_BackEnd_Design.md` §2, §2.1  
**Notes:** Service-role key is backend-only; authorization must be enforced in app code, not assumed from the DB.

## TODO

- [ ] Configure the Supabase PostgreSQL connection.
- [ ] Establish the logical entities: User, Project, Membership, Memory, Memory Revision, Transcript, and Ingestion Job.
- [ ] Add required uniqueness constraints and query indexes.
- [ ] Configure database migrations and test-environment initialization.
- [ ] Define the permitted use and security boundaries of privileged database credentials.

## Acceptance Criteria (ACs)

- Database migrations can be applied and upgraded according to the project's migration standards.
- A unique constraint exists on `(project_id, topic)`.
- Duplicate topics are rejected within the same project, while identical topics are allowed in different projects.
- Database connection failures are reported clearly by the service.

---
See `docs/EchoVault-Implementation-Tasks.md` (cross-task requirements) and `docs/EchoVault_BackEnd_Design.md`.
