# TASK-13 — Implement Persistent Ingestion Jobs

**Epic:** Epic 6: Transcript Archiving and Asynchronous Extraction  
**Status:** Not started  
**Priority:** P1  
**Depends on:** TASK-12  
**Design refs:** `docs/EchoVault_BackEnd_Design.md` §5.2, §5.3, T09, T10  
**Notes:** Use a safe claim mechanism (e.g. `FOR UPDATE SKIP LOCKED`). Jobs must survive restarts.

## TODO

- [ ] Implement a persistent task queue or database-backed job table.
- [ ] Define the `pending`, `processing`, `succeeded`, and `failed` states.
- [ ] Implement job claiming, retries, and error recording.
- [ ] Provide `GET /ingest/jobs/{job_id}`.
- [ ] Prevent concurrent workers from processing the same job in an uncontrolled manner.

## Acceptance Criteria (ACs)

- Return `202 Accepted` only after the transcript and its ingestion job have been durably persisted.
- Incomplete jobs can resume after a service restart.
- Job status and failure reasons are queryable.
- Retries are idempotent and do not write the same extraction results more than once.

---
See `docs/EchoVault-Implementation-Tasks.md` (cross-task requirements) and `docs/EchoVault_BackEnd_Design.md`.
