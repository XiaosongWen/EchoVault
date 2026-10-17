# EchoVault Implementation Tasks

**Project:** EchoVault  
**Document Type:** Engineering Task Backlog  
**Priority Legend:** P0 = Core launch requirement; P1 = Post-core launch requirement  
**Format:** TODO items and Acceptance Criteria (ACs)

---

## Epic 1: Project Initialization and Infrastructure

### TASK-01 — Initialize Backend Project

**Priority:** P0

#### TODO

- [ ] Initialize the FastAPI project and module structure.
- [ ] Configure development, testing, and production environments.
- [ ] Set up environment-variable management and dependency management.
- [ ] Add structured logging, centralized exception handling, and request IDs.
- [ ] Implement `/health` and `/ready` endpoints.

#### Acceptance Criteria (ACs)

- The project can start locally and serve API requests.
- Environment configuration and secrets are not hardcoded in the repository.
- Unhandled exceptions return the standardized error response format.
- Health checks distinguish service liveness from dependency readiness.

### TASK-02 — Set Up Supabase and Database Migrations

**Priority:** P0

#### TODO

- [ ] Configure the Supabase PostgreSQL connection.
- [ ] Establish the logical entities: User, Project, Membership, Memory, Memory Revision, Transcript, and Ingestion Job.
- [ ] Add required uniqueness constraints and query indexes.
- [ ] Configure database migrations and test-environment initialization.
- [ ] Define the permitted use and security boundaries of privileged database credentials.

#### Acceptance Criteria (ACs)

- Database migrations can be applied and upgraded according to the project's migration standards.
- A unique constraint exists on `(project_id, topic)`.
- Duplicate topics are rejected within the same project, while identical topics are allowed in different projects.
- Database connection failures are reported clearly by the service.

---

## Epic 2: Authentication and Multi-User Project Isolation

### TASK-03 — Implement Authentication

**Priority:** P0

#### TODO

- [ ] Integrate Supabase Auth or an equivalent OIDC authentication provider.
- [ ] Implement access-token validation.
- [ ] Define controlled credential-based access for the browser extension, CLI, and MCP clients.
- [ ] Implement API key revocation and rotation.

#### Acceptance Criteria (ACs)

- Valid access tokens can access protected endpoints.
- Missing, invalid, or expired tokens return `401 UNAUTHORIZED`.
- API keys grant only the permissions within their authorized scopes.
- Logs and error responses never expose authentication credentials.

### TASK-04 — Implement Project-Level Authorization

**Priority:** P0

#### TODO

- [ ] Implement project creation and project-list retrieval.
- [ ] Implement project membership management and permission checks.
- [ ] Enforce project-level authorization across all memory, revision-history, and transcript endpoints.
- [ ] Define permission rules for project owners, read-only members, and members with write access.

#### Acceptance Criteria (ACs)

- Users can access only projects they own or are explicitly authorized to access.
- Cross-project read and write operations are rejected.
- Knowing a resource ID cannot bypass authorization checks.
- Every write operation performs server-side authorization.

---

## Epic 3: Memory Core API

### TASK-05 — Implement Memory CRUD APIs

**Priority:** P0

#### TODO

- [ ] Implement memory creation: `POST /projects/{project_id}/memories`.
- [ ] Implement memory listing: `GET /projects/{project_id}/memories`.
- [ ] Implement memory detail retrieval: `GET /memories/{memory_id}`.
- [ ] Implement memory updates: `PATCH /memories/{memory_id}`.
- [ ] Implement memory deletion: `DELETE /memories/{memory_id}`.
- [ ] Support pagination, tag filtering, and keyword search.
- [ ] Standardize request validation and error responses.

#### Acceptance Criteria (ACs)

- All CRUD operations enforce project-level authorization.
- Creating a duplicate topic returns `409 TOPIC_ALREADY_EXISTS`.
- List endpoints support pagination and do not return full memory content by default.
- After deletion, the memory no longer appears in normal list or retrieval responses.
- Invalid requests return identifiable error codes.

### TASK-06 — Implement Idempotent Upsert

**Priority:** P0

#### TODO

- [ ] Implement memory upsert using `(project_id, topic)` as the lookup key.
- [ ] Support `expected_version`.
- [ ] Handle duplicate requests and concurrent writes.
- [ ] Distinguish direct user writes from AI-generated extraction writes.

#### Acceptance Criteria (ACs)

- The same project and topic cannot produce duplicate memory records.
- Retrying the same idempotent request does not create duplicate memories.
- Version mismatches return `409 VERSION_CONFLICT`.
- Automated extraction cannot bypass the automatic merge workflow or version protection.

### TASK-07 — Implement Memory Revisions and Restore

**Priority:** P0

#### TODO

- [ ] Record the previous memory version before each update.
- [ ] Implement the revision-history listing endpoint.
- [ ] Implement the historical revision restore endpoint.
- [ ] Ensure content updates and revision snapshots are committed atomically.

#### Acceptance Criteria (ACs)

- Every successful update preserves a traceable previous version.
- Revision history is accessible only to users authorized to access the project.
- Restoring a historical revision creates a new version without deleting existing history.
- Failed updates do not leave inconsistent revision records.

---

## Epic 4: Memory Retrieval and MCP

### TASK-08 — Implement Two-Stage Memory Retrieval

**Priority:** P0

#### TODO

- [ ] Implement topic-index retrieval.
- [ ] Implement full-content retrieval by topic.
- [ ] Ensure the index returns only topics, descriptions, tags, and required pagination metadata.
- [ ] Support pagination, tag filtering, and keyword search.
- [ ] Implement a token-budget limit for index responses.

#### Acceptance Criteria (ACs)

- Index responses do not include Markdown memory bodies.
- Full-content retrieval returns only the requested topic within the authorized project.
- A nonexistent topic returns `404 RESOURCE_NOT_FOUND`.
- Normal index responses target a maximum of 1,000 tokens; larger result sets can be paginated.

### TASK-09 — Implement MCP Server

**Priority:** P0

#### TODO

- [ ] Use FastMCP to expose the `/mcp` endpoint.
- [ ] Register the `list_topics` and `get_topic_memory` tools.
- [ ] Register memory-writing tools with appropriate permission controls.
- [ ] Reuse the business logic and authorization rules of the REST API.
- [ ] Configure MCP client authentication and tool-level permissions.

#### Acceptance Criteria (ACs)

- MCP clients can retrieve the topic index and read full memory content.
- MCP responses are consistent with the corresponding REST API behavior.
- The MCP service does not invoke an LLM directly.
- Unauthorized clients cannot execute write operations.

---

## Epic 5: Browser Extension and Dashboard

### TASK-10 — Integrate Browser Extension Write API

**Priority:** P0

#### TODO

- [ ] Provide a memory-creation API for the browser extension.
- [ ] Support `project_id`, `topic`, `description`, `tags`, and `content`.
- [ ] Validate project permissions and request formats.
- [ ] Define conflict handling for duplicate topics.
- [ ] Provide API documentation for browser-extension developers.

#### Acceptance Criteria (ACs)

- The browser extension can write memories through the REST API.
- A successful response confirms that the memory has been durably persisted.
- Unauthorized access, invalid parameters, and duplicate topics return clear errors.
- Newly written memories are available through the Dashboard and MCP.

### TASK-11 — Implement Dashboard Backend Support

**Priority:** P0

#### TODO

- [ ] Ensure CRUD APIs return all fields required by the Dashboard.
- [ ] Support pagination, search, tag filtering, and sorting by update time.
- [ ] Support Markdown content retrieval and editing.
- [ ] Provide clear conflict, deletion, and save-result feedback through API responses.
- [ ] Provide revision-history retrieval and restore endpoints.

#### Acceptance Criteria (ACs)

- The Dashboard can list, view, create, edit, and delete memories.
- After a successful update, other clients can retrieve the latest version.
- Concurrent edits never silently overwrite another client's changes.
- Deletion requires authorization and produces the necessary audit records.

---

## Epic 6: Transcript Archiving and Asynchronous Extraction

### TASK-12 — Implement Transcript Ingestion and Archiving

**Priority:** P1

#### TODO

- [ ] Implement `POST /ingest/transcripts`.
- [ ] Archive original conversation content and source metadata for long-term retention.
- [ ] Support external transcript IDs and idempotent requests.
- [ ] Use a reliable consistency mechanism for transcript archival and job creation.
- [ ] Enforce project-level authorization and access controls for raw data.

#### Acceptance Criteria (ACs)

- Successfully ingested transcripts can be retrieved and traced to their original content.
- Duplicate submissions do not create duplicate ingestion jobs.
- Service restarts do not lose data whose acceptance has already been confirmed.
- Unauthorized users cannot access original conversations.
- Original transcripts are not automatically deleted after successful extraction.

### TASK-13 — Implement Persistent Ingestion Jobs

**Priority:** P1

#### TODO

- [ ] Implement a persistent task queue or database-backed job table.
- [ ] Define the `pending`, `processing`, `succeeded`, and `failed` states.
- [ ] Implement job claiming, retries, and error recording.
- [ ] Provide `GET /ingest/jobs/{job_id}`.
- [ ] Prevent concurrent workers from processing the same job in an uncontrolled manner.

#### Acceptance Criteria (ACs)

- Return `202 Accepted` only after the transcript and its ingestion job have been durably persisted.
- Incomplete jobs can resume after a service restart.
- Job status and failure reasons are queryable.
- Retries are idempotent and do not write the same extraction results more than once.

### TASK-14 — Implement LLM Extraction and Memory Merging

**Priority:** P1

#### TODO

- [ ] Define the memory-extraction output schema.
- [ ] Implement the background LLM extraction worker.
- [ ] Extract durable facts, technical decisions, constraints, and project knowledge.
- [ ] Automatically merge new candidate memories with existing memories.
- [ ] Preserve pre-merge and post-merge versions, along with source metadata.
- [ ] Retain candidate content when conflicts cannot be resolved reliably.

#### Acceptance Criteria (ACs)

- LLM output must pass schema validation before entering the merge workflow.
- A successful merge creates a new version, and the previous version remains traceable.
- Merge failures never silently overwrite or discard existing content.
- Concurrent updates are detected through version checks and trigger a retry or conflict-handling workflow.
- The original transcript remains traceable and accessible.

---

## Epic 7: Quality Assurance and Release

### TASK-15 — Implement Automated Tests

**Priority:** P0

#### TODO

- [ ] Write tests for authentication and project isolation.
- [ ] Write tests for CRUD, upsert, and version control.
- [ ] Write tests for MCP and topic-index retrieval.
- [ ] Write tests for transcript idempotency, archival, and job retries.
- [ ] Write tests for automatic merging and historical revision restoration.

#### Acceptance Criteria (ACs)

- All core P0 tests pass.
- Cross-project access tests demonstrate effective data isolation.
- Concurrent-write tests demonstrate that updates are never silently overwritten.
- Duplicate-request and job-retry tests demonstrate idempotency.
- Asynchronous job failure and service-restart scenarios are verified.

### TASK-16 — Document APIs and Configure Deployment

**Priority:** P0

#### TODO

- [ ] Publish complete OpenAPI documentation.
- [ ] Document authentication methods, request and response examples, and error codes.
- [ ] Configure deployment environments, secrets, and database migration procedures.
- [ ] Configure logging, monitoring, and alerting.
- [ ] Verify health checks and critical APIs after deployment.

#### Acceptance Criteria (ACs)

- Developers can independently integrate with the API using the documentation.
- Testing and production environments use separate configurations.
- Health checks work correctly after deployment.
- Critical errors can be traced using request IDs in logs.
- No production secrets are committed to the repository.

---

## Cross-Task Engineering Requirements

The following requirements apply across the relevant tasks:

- **Project isolation:** Enforce authorization across REST APIs, MCP tools, background workers, and database-access paths.
- **Version integrity:** Commit memory updates and revision snapshots atomically.
- **Transcript durability:** Retain original transcripts after extraction succeeds or fails.
- **Conflict safety:** Preserve candidate content when an automatic merge cannot reliably resolve a conflict.
- **Idempotency:** Ensure repeated transcript submissions and job retries do not create duplicate logical processing or memory updates.
- **Observability:** Include request IDs, structured logs, job status, retry information, and actionable error details.
- **Security:** Never trust client-supplied user identifiers as proof of identity or authorization, and never expose secrets in logs or API responses.
