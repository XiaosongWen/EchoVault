# TASK-12 — Implement Transcript Ingestion and Archiving

**Epic:** Epic 6: Transcript Archiving and Asynchronous Extraction  
**Status:** Not started  
**Priority:** P1  
**Depends on:** TASK-02, TASK-04  
**Design refs:** `docs/EchoVault_BackEnd_Design.md` §5.1, §2.1(2,4), T08, T11  
**Notes:** Persist transcript + job atomically before returning 202. Idempotent on `transcript_id`. Never auto-delete.

## TODO

- [ ] Implement `POST /ingest/transcripts`.
- [ ] Archive original conversation content and source metadata for long-term retention.
- [ ] Support external transcript IDs and idempotent requests.
- [ ] Use a reliable consistency mechanism for transcript archival and job creation.
- [ ] Enforce project-level authorization and access controls for raw data.

## Acceptance Criteria (ACs)

- Successfully ingested transcripts can be retrieved and traced to their original content.
- Duplicate submissions do not create duplicate ingestion jobs.
- Service restarts do not lose data whose acceptance has already been confirmed.
- Unauthorized users cannot access original conversations.
- Original transcripts are not automatically deleted after successful extraction.

---
See `docs/EchoVault-Implementation-Tasks.md` (cross-task requirements) and `docs/EchoVault_BackEnd_Design.md`.
