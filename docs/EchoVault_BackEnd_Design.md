# EchoVault Backend Technical Design & API Contract

**Version:** v1.1  
**Scope:** Multi-user and project isolation, memory CRUD, MCP integration, browser extension integration, long-term transcript archiving, and asynchronous memory extraction.

---

## 1. Core Design Decisions

- **Single Source of Truth:** Supabase PostgreSQL.
- **Unified Backend:** FastAPI. REST APIs and MCP tools must share the same business logic and authorization layer.
- **Multi-Tenant Isolation:** Each project must have an explicit owner or membership-based access policy. All read and write operations must enforce project-level authorization.
- **Memory Uniqueness:** Each `topic` must be unique within a project. Different projects may use the same `topic`.
- **Conflict Resolution:** Automatically merge compatible memory updates while preserving all pre-merge versions. If a conflict cannot be resolved reliably, retain the conflicting candidate content rather than silently discarding information.
- **Raw Data Retention:** Archive original transcripts indefinitely by default, enabling extraction results to be traced back to their source conversations.
- **Retrieval Strategy:** Retrieve a lightweight topic index first, then fetch full memory content on demand.
- **Asynchronous Processing:** Once a transcript has been durably persisted and its processing job has been recorded, return a job ID immediately. A background worker extracts candidate memories and updates the memory store asynchronously.

## 2. Core Data Model Requirements

The database schema must support at least the following logical entities.

| Entity | Required Information |
|---|---|
| User | User identity and authentication association |
| Project | Project identifier, ownership relationship, and project name |
| Project Membership | User-to-project membership and permission level |
| Memory | Project, topic, description, tags, Markdown content, version, source, and timestamps |
| Memory Revision | Historical snapshots and pre-merge versions, supporting auditing and restoration |
| Transcript | Original conversation content, source, project, capture timestamp, and unique external identifier |
| Ingestion Job | Job status, retry count, error details, and associated transcript |

### 2.1 Mandatory Data Integrity Constraints

1. Enforce uniqueness on `(project_id, topic)`.
2. Every transcript must have an idempotency identifier. Repeated submissions must not create duplicate transcripts or ingestion jobs for the same logical submission.
3. Memory updates and revision snapshots must be committed atomically. A successful update must never result in a missing historical revision.
4. Transcripts must be retained indefinitely by default and must not be automatically deleted after successful extraction.
5. Memory records, revision history, and transcripts must all enforce project-level access control.
6. Automatic merges must preserve source attribution and change history so that every material update can be traced to its original evidence.

---

## 3. Authentication and Authorization

### 3.1 Authentication Methods

- **Dashboard and Custom Web/Mobile Clients:** Use Supabase Auth or an equivalent OIDC-compatible identity provider. The REST API must validate access tokens before processing requests.
- **Browser Extension and CLI:** Use user-authorized access tokens or revocable, project-scoped API keys with explicitly defined permissions.
- **MCP Clients:** Authenticate using configured client credentials or an appropriate user-delegated authorization flow. Restrict available tools and operations according to the authenticated identity.
- **Background Workers:** Use dedicated service identities. Do not reuse long-lived credentials belonging to ordinary users.

### 3.2 Authorization Rules

- Users may access only projects they own or have been explicitly authorized to access.
- Project access must be checked for all project reads, memory modifications, transcript ingestion, and revision-history operations.
- Read-only and write permissions must be separated.
- API keys must support revocation, scope restrictions, and secure rotation.
- When using a privileged Supabase service-role key, the backend must enforce authorization independently. Never trust a client-supplied `user_id` as proof of identity or permission.
- Cross-project access must be rejected even if the caller knows the target resource ID.
- Resource lookup and authorization behavior must not inadvertently expose the existence of resources in unauthorized projects.

---

## 4. REST API Contract

**Base path:** `/api/v1`

All endpoints use JSON unless explicitly documented otherwise. Errors must follow the unified error response format defined in Section 7.

### 4.1 Project and Memory Management

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/projects` | Create a project |
| `GET` | `/projects` | List projects accessible to the authenticated user |
| `GET` | `/projects/{project_id}/memories` | Retrieve a paginated memory index |
| `POST` | `/projects/{project_id}/memories` | Create a memory |
| `GET` | `/memories/{memory_id}` | Retrieve a complete memory |
| `PATCH` | `/memories/{memory_id}` | Update a memory |
| `DELETE` | `/memories/{memory_id}` | Delete a memory |
| `GET` | `/memories/{memory_id}/revisions` | Retrieve memory revision history |
| `POST` | `/memories/{memory_id}/restore` | Restore a historical revision as a new version |

### 4.2 Create Memory

**Request**

`POST /api/v1/projects/proj_123/memories`

```json
{
  "topic": "database-architecture",
  "description": "Project database architecture and key decisions",
  "tags": ["database", "architecture"],
  "content": "# Database Architecture\n\nPostgreSQL is used as the primary data store.",
  "source": "browser"
}
```

**Successful Response — `201 Created`**

```json
{
  "id": "mem_456",
  "project_id": "proj_123",
  "topic": "database-architecture",
  "description": "Project database architecture and key decisions",
  "tags": ["database", "architecture"],
  "content": "# Database Architecture\n\nPostgreSQL is used as the primary data store.",
  "version": 1,
  "created_at": "2026-10-14T12:00:00Z",
  "updated_at": "2026-10-14T12:00:00Z"
}
```

If the same topic already exists within the project, return `409 Conflict` with error code `TOPIC_ALREADY_EXISTS`. The server must never silently overwrite an existing memory.

### 4.3 Update Memory

**Request**

`PATCH /api/v1/memories/mem_456`

```json
{
  "expected_version": 1,
  "description": "Updated database architecture summary",
  "content": "# Database Architecture\n\nPostgreSQL is the single source of truth."
}
```

**Successful Response — `200 OK`**

Return the complete updated memory with `version: 2`.

The update must preserve the previous version in revision history.

If the current version no longer matches `expected_version`, return `409 Conflict` with error code `VERSION_CONFLICT`. The client must retrieve the latest version and resolve the conflict before retrying.

### 4.4 Memory Index and Full-Content Retrieval

**Retrieve the memory index**

`GET /api/v1/projects/proj_123/memories?limit=50&cursor=...`

The response must include lightweight metadata only:

- Memory ID
- Topic
- Description
- Tags
- Version, when needed
- Pagination metadata

Full Markdown content must not be included in index responses.

**Retrieve a memory by topic**

`GET /api/v1/projects/proj_123/topics/database-architecture`

Return the complete Markdown content and version metadata for the specified topic.

Alternatively, clients may use `GET /api/v1/memories/{memory_id}`. If both access patterns are implemented, their response semantics and authorization rules must remain consistent.

Index queries must support pagination and tag filtering while keeping response payloads small enough for efficient LLM context construction.

### 4.5 Memory Upsert

**Endpoint**

`PUT /api/v1/projects/proj_123/memories/database-architecture`

This endpoint provides idempotent topic-based writes for trusted automation clients.

The request must include `description`, `tags`, and `content`, with `expected_version` optional for creation but required for updates to existing memories.

| Condition | Required Behavior |
|---|---|
| Topic does not exist | Create a new memory |
| Topic exists and version matches | Update the memory and preserve its previous revision |
| Topic exists and version does not match | Return `409 VERSION_CONFLICT` |
| Automatically extracted content is submitted | Route through the automatic merge workflow; never bypass version protection |

The implementation must define how retries are handled so that repeating an identical request does not create duplicate side effects.

---

## 5. Transcript Ingestion and Asynchronous Extraction

### 5.1 Transcript Ingestion Endpoint

**Endpoint**

`POST /api/v1/ingest/transcripts`

**Request**

```json
{
  "project_id": "proj_123",
  "source": "claude-code",
  "transcript_id": "session_789",
  "captured_at": "2026-10-14T11:30:00Z",
  "messages": [
    {
      "role": "user",
      "content": "Discuss the database migration strategy."
    },
    {
      "role": "assistant",
      "content": "A phased migration with rollback support is recommended."
    }
  ]
}
```

**Successful Response — `202 Accepted`**

```json
{
  "transcript_id": "session_789",
  "job_id": "job_001",
  "status": "pending"
}
```

The server must durably persist the original transcript and the corresponding ingestion job before returning a successful response.

The target response latency is **P95 below 100 ms**, subject to load testing and validation under the expected deployment configuration.

If the same transcript is submitted again with the same idempotency identity, return the existing transcript and job information rather than creating duplicate processing work.

### 5.2 Query Ingestion Job Status

**Endpoint**

`GET /api/v1/ingest/jobs/job_001`

**Example Response**

```json
{
  "job_id": "job_001",
  "status": "succeeded",
  "transcript_id": "session_789",
  "created_memories": 1,
  "updated_memories": 0,
  "conflicts": 0
}
```

The job lifecycle must support at least the following states:

- `pending`
- `processing`
- `succeeded`
- `failed`

State transitions must be persisted and observable by clients. The implementation must also prevent concurrent workers from processing the same job in an uncontrolled manner.

### 5.3 Background Processing Workflow

1. Durably archive the original transcript.
2. Persist an ingestion job associated with the transcript.
3. A background worker claims the job and invokes an LLM to extract candidate memories.
4. Validate the extraction output against the expected schema, project ownership, and content-integrity requirements.
5. Merge candidates into existing memories while preserving the pre-merge and post-merge versions.
6. If a conflict cannot be resolved reliably, retain the candidate content and mark the conflict for further review.
7. Update job status and processing statistics.
8. Retry failed operations according to the configured retry policy. After the retry limit is exceeded, mark the job as `failed`, preserve diagnostic information, and allow authorized operators to retry it manually.

The workflow must be recoverable after worker restarts and must avoid duplicate memory updates when jobs are retried.

---

## 6. Automatic Merge and Version Protection

Automatic memory merging must comply with the following rules:

- Every automatic merge must preserve the memory version that existed before the merge.
- The merged result must retain all relevant existing information. New extracted content must not simply replace the entire memory body.
- Memory updates, revision snapshots, and associated merge metadata must be committed atomically or through an equivalent mechanism that guarantees recoverable consistency.
- Concurrent updates must be detected through version checks. If the underlying memory changes during a merge, the worker must reload the latest version and recompute the merge as necessary.
- If the system cannot reliably determine whether two statements conflict, it must preserve the candidate content or flag the conflict for review.
- Manual Dashboard edits must follow the same revision-preservation rules.
- Restoring a historical revision must create a new version containing the restored content. Existing revision history must remain intact.
- Merge records should capture the source transcript, extraction job, affected memory, and relevant version identifiers so that changes remain auditable.
- Repeated processing of the same transcript or job must not produce duplicate logical updates.

---

## 7. Unified Error Contract

All API errors must follow this structure:

```json
{
  "error": {
    "code": "VERSION_CONFLICT",
    "message": "Memory has been updated by another client.",
    "request_id": "req_abc123"
  }
}
```

| HTTP Status | Error Code | Meaning |
|---|---|---|
| `400` | `INVALID_REQUEST` | Invalid request parameters or malformed input |
| `401` | `UNAUTHORIZED` | Missing, invalid, or expired authentication credentials |
| `403` | `PROJECT_ACCESS_DENIED` | The caller lacks permission to access the project |
| `404` | `RESOURCE_NOT_FOUND` | The requested resource does not exist or is intentionally concealed |
| `409` | `VERSION_CONFLICT` | The memory version has changed since it was read |
| `409` | `TOPIC_ALREADY_EXISTS` | A memory with the same topic already exists in the project |
| `413` | `PAYLOAD_TOO_LARGE` | The request exceeds the configured payload limit |
| `422` | `VALIDATION_ERROR` | Content validation or schema validation failed |
| `429` | `RATE_LIMITED` | The caller exceeded the allowed request rate |
| `500` | `INTERNAL_ERROR` | An unexpected server-side error occurred |
| `503` | `SERVICE_UNAVAILABLE` | The service is temporarily unavailable |

The server must not expose stack traces, secrets, internal database details, or unauthorized resource information in client-facing error messages.

Every error response should include a request ID for tracing and debugging.

---

## 8. Minimum Acceptance Test Cases

| ID | Test Scenario | Expected Result |
|---|---|---|
| T01 | A user reads a memory from a project they can access | Request succeeds |
| T02 | A user reads a project they are not authorized to access | Return `403` or a non-disclosing `404` |
| T03 | Two different projects create memories with the same topic | Both operations succeed |
| T04 | The same project creates two memories with the same topic | The second request returns `409` |
| T05 | A client updates a memory using a stale version | Return `409`; the newer version remains unchanged |
| T06 | An automatic memory merge succeeds | A new version is created and the previous version remains accessible |
| T07 | An automatic merge encounters an unresolved conflict | Candidate content is retained; no information is silently discarded |
| T08 | The same transcript is submitted repeatedly | No duplicate transcript processing job or duplicate logical extraction occurs |
| T09 | The service restarts after accepting a job | Persisted jobs remain recoverable and can resume processing |
| T10 | An LLM invocation fails | The job is retried according to policy, and its final status remains queryable |
| T11 | Memory extraction succeeds | The original transcript remains available |
| T12 | A Dashboard user deletes a memory | The memory no longer appears in the normal active index; the audit history is retained |
| T13 | A user restores an older memory revision | A new version is created, and the existing history remains intact |
| T14 | An unauthorized client invokes a write operation or MCP tool | Return `401` or `403`, as appropriate |
| T15 | The transcript ingestion endpoint is load-tested | Validate the P95 latency target and verify durable persistence under load |

---

## 9. Minimum Delivery Requirements

The backend implementation must include:

1. A deployable REST API and MCP service.
2. Database migrations, indexes, uniqueness constraints, and transactional integrity protections.
3. OpenAPI documentation covering the REST API contracts.
4. Authentication, project-level authorization, and optimistic concurrency control.
5. Memory CRUD, paginated index retrieval, tag filtering, and full-content retrieval.
6. Long-term transcript archiving and asynchronous ingestion processing.
7. Automatic merging, revision history, conflict preservation, and failure recovery.
8. Automated unit, integration, authorization, concurrency, and idempotency tests.
9. Deployment configuration, environment-variable documentation, and operational logging.
10. Monitoring for ingestion latency, processing failures, retry counts, merge conflicts, and worker health.

### Definition of Done

The implementation is acceptable only when all of the following conditions are met:

- Project-level isolation is enforced across REST APIs, MCP tools, background workers, and data-access paths.
- Every memory change is traceable, and historical versions can be restored without destroying intervening history.
- Original transcripts remain available after successful extraction and after processing failures.
- Automatic merging never silently overwrites existing knowledge or discards unresolved candidate information.
- Duplicate submissions and retried jobs do not cause duplicate logical processing.
- Unauthorized users cannot access resources across project boundaries.
- The transcript ingestion latency target and persistence guarantees have been validated through automated tests and load testing.

**Non-negotiable acceptance criteria:** Strong project isolation, complete memory traceability, durable preservation of original transcripts, and conflict-safe automatic merging.