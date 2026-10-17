from fastapi import APIRouter, status
from fastapi.responses import JSONResponse

from echovault.config import get_settings
from echovault.db.readiness import check_database_connection

router = APIRouter(tags=["Health"])


@router.get("/health", summary="Liveness probe")
async def health() -> dict[str, str]:
    """Liveness probe.

    Returns 200 OK as long as the service process is alive and responsive.
    """
    return {"status": "ok"}


@router.get("/ready", summary="Readiness probe")
async def ready() -> JSONResponse:
    """Readiness probe.

    Distinguishes service liveness from dependency readiness.
    Validates that backing dependencies (e.g. database) are ready to accept traffic.
    """
    settings = get_settings()
    checks: dict[str, str] = {}
    is_ready = True

    db_ok, db_msg = await check_database_connection(settings)
    checks["database"] = db_msg
    if not db_ok:
        is_ready = False

    status_str = "ready" if is_ready else "not_ready"
    status_code = status.HTTP_200_OK if is_ready else status.HTTP_503_SERVICE_UNAVAILABLE

    return JSONResponse(
        status_code=status_code,
        content={
            "status": status_str,
            "checks": checks,
        },
    )
