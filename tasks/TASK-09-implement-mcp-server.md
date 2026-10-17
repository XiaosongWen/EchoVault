# TASK-09 — Implement MCP Server

**Epic:** Epic 4: Memory Retrieval and MCP  
**Status:** Not started  
**Priority:** P0  
**Depends on:** TASK-03, TASK-06, TASK-08  
**Design refs:** `docs/EchoVault_BackEnd_Design.md` §1, T14  
**Notes:** MCP calls the same services as REST; it must never invoke an LLM itself.

## TODO

- [ ] Use FastMCP to expose the `/mcp` endpoint.
- [ ] Register the `list_topics` and `get_topic_memory` tools.
- [ ] Register memory-writing tools with appropriate permission controls.
- [ ] Reuse the business logic and authorization rules of the REST API.
- [ ] Configure MCP client authentication and tool-level permissions.

## Acceptance Criteria (ACs)

- MCP clients can retrieve the topic index and read full memory content.
- MCP responses are consistent with the corresponding REST API behavior.
- The MCP service does not invoke an LLM directly.
- Unauthorized clients cannot execute write operations.

---
See `docs/EchoVault-Implementation-Tasks.md` (cross-task requirements) and `docs/EchoVault_BackEnd_Design.md`.
