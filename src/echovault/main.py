from fastapi import FastAPI

from echovault.api.health import router as health_router
from echovault.api.v1.router import api_router
from echovault.config import Settings, get_settings
from echovault.core.handlers import register_exception_handlers
from echovault.core.logging import setup_logging
from echovault.core.middleware import RequestIdMiddleware


def create_app(settings: Settings | None = None) -> FastAPI:
    if settings is None:
        settings = get_settings()

    setup_logging(settings)

    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        docs_url="/docs" if not settings.is_production else None,
        redoc_url="/redoc" if not settings.is_production else None,
    )

    app.add_middleware(RequestIdMiddleware, header_name=settings.request_id_header)
    register_exception_handlers(app)

    app.include_router(health_router)
    app.include_router(api_router)

    return app


app = create_app()
