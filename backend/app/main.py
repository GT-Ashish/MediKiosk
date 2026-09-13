"""
MediKiosk Backend — FastAPI Application Entry Point.

Creates and configures the FastAPI application instance with:
- CORS middleware for frontend communication
- API router mounting
- Database lifecycle management
- Global exception handling for domain errors
"""

from contextlib import asynccontextmanager
from collections.abc import AsyncIterator

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.config import get_settings
from app.api.router import api_router
from app.infrastructure.database import init_db, close_db, create_all_tables
from app.utils.errors import (
    MediKioskError,
    SessionNotFoundError,
    ConsentRequiredError,
    MediKioskValidationError,
    UnsupportedOperationError,
)


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    # Read settings fresh each time create_app is called
    # (important for testing where env vars may be overridden)
    settings = get_settings()

    @asynccontextmanager
    async def lifespan(app: FastAPI) -> AsyncIterator[None]:
        """Application lifespan handler for startup/shutdown events."""
        # Re-read settings in lifespan context (env vars may have changed)
        current_settings = get_settings()

        # Startup
        print(f"[STARTUP] {current_settings.app_name} v{current_settings.app_version} starting...")
        print(f"   Environment: {current_settings.app_env}")
        print(f"   Debug: {current_settings.debug}")
        db_display = current_settings.database_url
        if "@" in db_display:
            db_display = db_display.split("@")[-1]
        print(f"   Database: {db_display}")

        # Initialise database
        await init_db(
            database_url=current_settings.database_url,
            echo=current_settings.debug and current_settings.app_env == "development",
        )

        # In development, auto-create tables (production uses Alembic migrations)
        if current_settings.app_env == "development":
            # Import models to register them with Base.metadata
            import app.domain.models  # noqa: F401
            await create_all_tables()
            print("   [DB] Tables created/verified (development mode)")

        yield

        # Shutdown
        await close_db()
        print(f"[SHUTDOWN] {current_settings.app_name} shutting down...")

    app = FastAPI(
        title=settings.app_name,
        description="AI-Powered Clinical History Software Platform",
        version=settings.app_version,
        docs_url="/docs" if settings.debug else None,
        redoc_url="/redoc" if settings.debug else None,
        lifespan=lifespan,
    )

    # CORS middleware — allows the React frontend to communicate with the API
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # ── Domain Error Handlers ─────────────────────────────────────────────────
    # Map domain errors to appropriate HTTP responses.
    # Internal details are never exposed to clients.

    @app.exception_handler(SessionNotFoundError)
    async def session_not_found_handler(request: Request, exc: SessionNotFoundError) -> JSONResponse:
        return JSONResponse(
            status_code=404,
            content={"error": "Session not found.", "detail": exc.detail},
        )

    @app.exception_handler(ConsentRequiredError)
    async def consent_required_handler(request: Request, exc: ConsentRequiredError) -> JSONResponse:
        return JSONResponse(
            status_code=403,
            content={"error": "Consent required.", "detail": exc.detail},
        )

    @app.exception_handler(MediKioskValidationError)
    async def validation_error_handler(request: Request, exc: MediKioskValidationError) -> JSONResponse:
        return JSONResponse(
            status_code=422,
            content={"error": exc.message, "detail": exc.detail},
        )

    @app.exception_handler(UnsupportedOperationError)
    async def unsupported_handler(request: Request, exc: UnsupportedOperationError) -> JSONResponse:
        return JSONResponse(
            status_code=501,
            content={"error": exc.message, "detail": exc.detail},
        )

    @app.exception_handler(MediKioskError)
    async def medikiosk_error_handler(request: Request, exc: MediKioskError) -> JSONResponse:
        return JSONResponse(
            status_code=500,
            content={"error": "Internal server error.", "detail": None},
        )

    @app.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
        return JSONResponse(
            status_code=exc.status_code,
            content={"error": exc.detail, "status_code": exc.status_code},
        )

    @app.exception_handler(Exception)
    async def generic_exception_handler(request: Request, exc: Exception) -> JSONResponse:
        return JSONResponse(
            status_code=500,
            content={
                "error": "Internal Server Error",
                "detail": str(exc) if settings.debug else "An unexpected error occurred.",
            },
        )

    # Mount API routes
    app.include_router(api_router, prefix="/api")

    return app


app = create_app()
