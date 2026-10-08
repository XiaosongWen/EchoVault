Product Requirements Document (PRD)
MemoVault: Centralized Cross-Device Memory Hub
1. Overview & Problem Statement
1.1 Executive Summary
The MemoVault is a stateless middleware and persistent storage layer designed to share project-level context, architecture decisions, and session conclusions across multiple development devices (PC, Mac, mobile) and agent clients (Claude Code, CLI tools, custom web interfaces).
1.2 Problem Statement
Developers working across diverse environments face severe state fragmentation:

Git-backed memory (MEMORY.md) failure: Incurs high synchronization friction (checkout/pull/commit/push), lacks sub-document query APIs (forcing full-file loading that pollutes token budgets), and risks committing sensitive environment data.
Context Loss Across Devices: Sessions in Claude Code on desktop do not inform tasks executed on laptop CLI tools or mobile web interfaces.
Token Inefficiency: Blindly dumping all historical sessions or full documentation files into prompts consumes excessive context window tokens and degrades LLM reasoning performance.
1.3 Goals & Success Metrics
Zero-Friction Cross-Device Sync: Memories created on any device/client are immediately accessible globally.
Token Efficiency: Topic exploration consumes less than 1,000 tokens for index queries across 100+ documents via a two-stage retrieval protocol.
Low Latency: Write acknowledgments to agent clients are instantaneous (<200ms) with background asynchronous persistence.
Client Agnostic: Unified backend supporting both standard REST API (for web/mobile custom agents) and Model Context Protocol (MCP) HTTP transports (for Claude Code and IDEs).
2. User Personas & Core Use Cases
Full-Stack Developer using Claude Code / IDE: Needs instant access to past architecture decisions, preferred stacks, and environment configurations without manual prompting.
Multi-Device Power User: Switches between desktop, laptop, and mobile web clients while maintaining a continuous train of context on active engineering tasks.
Autonomous / Custom Agents: Applications needing programmatic pre-retrieval before prompt dispatch and silent post-session summary generation.
3. Architecture & System Topology
[Phone / Web / Custom Agent] (REST API) ─────────────────┐

                                                         ├──► [FastAPI Gateway on Cloud Run] ──► [Supabase PostgreSQL]

[Claude Code / Agy / IDE] (Remote MCP HTTP / Webhook) ─┘        ├─ REST Routes (/api/memory/...)
                                                                ├─ Raw Transcript Route (/api/ingest/transcript)
                                                      └─ FastMCP Mount (/mcp)
3.1 System Topology & Gateway-Side Ingestion Flow
                                                                └─ FastMCP Mount (/mcp)
Client Boundary: Shell commands, local diffs, file modifications, and direct model calls stay 100% on the local client machine.
Gateway Boundary: Authenticates requests, performs two-stage metadata indexing, and proxies atomic database operations.
Storage Boundary: Enforces relational consistency, unique composite constraints, and durable ACID storage.
Ingestion & Extraction Boundary: The FastAPI Gateway accepts raw session transcripts via server-side endpoints and session-end webhooks/middleware, executing background LLM extraction pipelines asynchronously without requiring client-side LLM overhead.
4. Functional Requirements
4.1 Data Layer Schema
Field Name
Type
Key / Constraint
Description
id
 uuid
 Primary Key
Unique record identifier generated automatically.
project_id
 text
 Indexed
Scopes memories to specific workspaces, repositories, or domains.
topic
 text
 Composite Unique
Unique identifier for the memory entry (e.g., auth-architecture).
description
 text
 —
Concise single-sentence summary used for index-level scanning.
tags
 text[]
 —
Array of labels for deterministic categorization and filtering.
content
 text
 —
Full Markdown content containing distilled facts and decisions.
updated_at
 timestamptz
 Auto-update
Timestamp updated automatically on each upsert operation.


Composite Constraint: Unique index on (project_id, topic) ensuring deterministic, atomic updates across all client access layers.
4.2 Two-Stage Dynamic Retrieval (Token Optimization)
To avoid maintaining stale static files while guarding context windows during active LLM sessions:

Stage 1 (list_topics):
Accepts project_id.
Returns array of { topic, description, tags, updated_at } without the main content.
Payload footprint: <1,000 tokens for 100 entries.
Stage 2 (get_topic_memory):
Accepts project_id and topic.
Returns the full Markdown content strictly when an agent decides deep context is necessary.
4.3 Server-Side Raw Transcript Ingestion & Automated Memory Pipeline
Raw Transcript Payload: Gateway exposes POST /api/ingest/transcript accepting raw uncompressed session logs, conversation messages, or shell command streams alongside project_id and session metadata.
Session-End Webhook Interception: Supports webhooks and client middleware triggers (e.g., IDE session-close, CLI exit hooks) that automatically dispatch raw transcripts upon session termination.
Gateway-Side Asynchronous Extraction: The gateway acknowledges ingestion immediately (<100ms) and queues background extraction tasks using lightweight LLM summarization workers to distill facts, decisions, and architecture changes into standardized memory entries.
Automated Upsert Processing: Extracted memory items are parsed and merged into project_memories via automated atomic upsert calls (upsert_topic_memory), maintaining up-to-date project context without manual developer or agent intervention.
4.4 Service & Gateway Layer (FastAPI)
Deployment: Containerized service hosted on Google Cloud Run with asynchronous background processing capabilities.
REST Endpoints:
GET /api/memory/{project_id}: Stage 1 index retrieval.
GET /api/memory/{project_id}/{topic}: Stage 2 deep context retrieval.
POST /api/memory: Direct atomic upsert of structured memory entries.
POST /api/ingest/transcript: Server-side raw transcript ingestion and webhook interceptor route.
MCP Endpoint:
Auto-mounted via FastMCP at /mcp over standard HTTP transport.
Exposes tools: list_topics, get_topic_memory, upsert_topic_memory.
Security & Authentication:
Unified Bearer Token verification on both /api/... and /mcp routes.
5. Client Integration Protocols
5.1 Third-Party CLI Agents (Claude Code, Agy)
Connection & Hook Configuration:
Remote MCP HTTP transport for interactive tools:
claude mcp add --transport http memory-hub https://<backend-domain>/mcp --header "Authorization: Bearer <TOKEN>"
Session-end webhook middleware configured in agent lifecycle hooks to post raw session logs directly to /api/ingest/transcript upon command completion or session exit.
Agent Instructions (CLAUDE.md):
On task start: Model calls list_topics to identify relevant decisions; selectively queries get_topic_memory.
On session exit / milestone completion: Webhooks automatically stream the full raw session transcript to the gateway for zero-touch background extraction.
5.2 Custom Agents (Web & Mobile Frontends)
Implicit Pre-Retrieval: On user query submission, backend performs background REST query to fetch top relevant memory topics and injects into system prompt before LLM dispatch.
Silent Server-Side Webhook / Middleware Interception: When a web/mobile session closes, a lightweight middleware interceptor sends the raw conversation transcript to /api/ingest/transcript, offloading context distillation entirely to the FastAPI background extraction pipeline.
6. Non-Functional Requirements
Performance & Latency: API response time for list_topics under 150ms; memory retrieval under 100ms; raw transcript ingestion acknowledgement under 100ms with non-blocking async processing.
Availability: 99.9% uptime powered by serverless Cloud Run scaling to zero and managed Supabase Postgres.
Security: Data encrypted at rest and in transit (HTTPS/TLS 1.3). No API keys or agent credentials logged.
Auditability: Complete revision histories trackable via updated_at timestamps and database audit logs.
7. Phased Implementation Roadmap
Phase 1: MVP & Core Infrastructure
Provision Supabase project_memories table with composite unique index.
Build FastAPI hub with REST retrieval routes, raw transcript ingestion endpoint (/api/ingest/transcript), background worker pipeline, and FastMCP mount.
Deploy to Cloud Run with Bearer authentication.
Integrate Claude Code and custom agents via remote MCP HTTP transport and session-end webhook interceptors.
Phase 2: Custom Agent & Scale Enhancements
Wire custom web/mobile frontend middleware for automated transcript submission and background memory extraction.
Introduce full-text search (tsvector) and evaluate optional pgvector hybrid search once document volume exceeds hundreds of entries.

