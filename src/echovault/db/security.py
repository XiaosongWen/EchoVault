"""Security Boundaries & Privileged Credentials Policy.

This module defines and documents the security model for database access and credentials
within EchoVault, adhering to TASK-02 and Backend Technical Design §3.

Key Principles:
1. Backend-Only Credentials:
   - `DATABASE_URL` (direct PostgreSQL connection) and `SUPABASE_SERVICE_ROLE_KEY` (service role)
     are privileged secrets strictly restricted to backend services (FastAPI, background workers).
   - Privileged credentials must NEVER be exposed to clients (dashboard, browser extension,
     CLI, curl callers, MCP clients).
   - In logs and error responses, credentials and secrets are automatically masked or stripped.

2. Application-Enforced Authorization:
   - EchoVault does NOT rely solely on database-level RLS to enforce project boundaries.
   - Every read and write operation must perform independent, application-level authorization
     checks against project ownership or `project_memberships`.
   - Never trust client-supplied user identifiers or assumed DB privileges.

3. Bearer Token Authentication (Supabase Auth):
   - External callers (curl, dashboard, CLI) supply user-delegated Bearer tokens (JWTs)
     issued by Supabase Auth (`Authorization: Bearer <token>`).
   - The backend validates the JWT, extracts the caller's identity (`sub`), and executes
     queries scoped to that user's authorized projects.

4. Shared Database Isolation:
   - EchoVault resides in a dedicated PostgreSQL schema (`echovault`), isolated from other
     applications sharing the same PostgreSQL instance.
   - Cross-application schema access is strictly prohibited.
"""

from typing import Final

PRIVILEGED_CREDENTIAL_NAMES: Final[tuple[str, ...]] = (
    "DATABASE_URL",
    "SUPABASE_SERVICE_ROLE_KEY",
    "SUPABASE_JWT_SECRET",
    "LLM_API_KEY",
)


def is_privileged_credential(name: str) -> bool:
    """Return True if the given credential key is classified as privileged."""
    return name.upper() in PRIVILEGED_CREDENTIAL_NAMES
