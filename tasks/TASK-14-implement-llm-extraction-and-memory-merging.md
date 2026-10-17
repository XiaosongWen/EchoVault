# TASK-14 — Implement LLM Extraction and Memory Merging

**Epic:** Epic 6: Transcript Archiving and Asynchronous Extraction  
**Status:** Not started  
**Priority:** P1  
**Depends on:** TASK-06, TASK-07, TASK-13  
**Design refs:** `docs/EchoVault_BackEnd_Design.md` §5.3, §6, T06, T07  
**Notes:** Validate LLM output against a schema. Keep conflicting candidates instead of discarding them.

## TODO

- [ ] Define the memory-extraction output schema.
- [ ] Implement the background LLM extraction worker.
- [ ] Extract durable facts, technical decisions, constraints, and project knowledge.
- [ ] Automatically merge new candidate memories with existing memories.
- [ ] Preserve pre-merge and post-merge versions, along with source metadata.
- [ ] Retain candidate content when conflicts cannot be resolved reliably.

## Acceptance Criteria (ACs)

- LLM output must pass schema validation before entering the merge workflow.
- A successful merge creates a new version, and the previous version remains traceable.
- Merge failures never silently overwrite or discard existing content.
- Concurrent updates are detected through version checks and trigger a retry or conflict-handling workflow.
- The original transcript remains traceable and accessible.

---
See `docs/EchoVault-Implementation-Tasks.md` (cross-task requirements) and `docs/EchoVault_BackEnd_Design.md`.
