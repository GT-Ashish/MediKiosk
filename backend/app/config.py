"""
MediKiosk Backend Configuration.

Loads application settings from environment variables with sensible defaults
for local development. Uses pydantic-settings for type-safe configuration.

Configuration groups:
    Application   — app name, version, environment, debug
    Server        — host, port
    CORS          — allowed frontend origins
    Session       — session lifecycle settings
    Documents     — document upload limits
    AI            — AI feature flags (disabled by default)
    Logging       — log level and PII-safe logging config
"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # ── Application ────────────────────────────────────────────────────────────
    app_name: str = "MediKiosk"
    app_version: str = "0.1.0"
    app_env: str = "development"
    debug: bool = True

    # ── Server ─────────────────────────────────────────────────────────────────
    host: str = "0.0.0.0"
    port: int = 8000

    # ── CORS ───────────────────────────────────────────────────────────────────
    cors_origins: str = "http://localhost:5173,http://127.0.0.1:5173"

    @property
    def cors_origins_list(self) -> list[str]:
        """Parse CORS_ORIGINS comma-separated string into a list."""
        return [origin.strip() for origin in self.cors_origins.split(",")]

    # ── Session ────────────────────────────────────────────────────────────────
    session_ttl_minutes: int = 60
    """
    How long an ACTIVE kiosk session is valid before it is automatically
    abandoned (minutes). Prevents orphaned sessions from accumulating
    in memory/database.
    Env var: SESSION_TTL_MINUTES
    """

    # ── Documents ──────────────────────────────────────────────────────────────
    max_documents_per_session: int = 10
    """
    Maximum number of documents a patient can upload per session.
    Prevents resource exhaustion from overly large uploads.
    Env var: MAX_DOCUMENTS_PER_SESSION
    """

    # ── AI Feature Flags ───────────────────────────────────────────────────────
    ai_enabled: bool = False
    """
    Master switch for AI-assisted features (LLM summarisation, NER extraction).
    When False, the summary service returns template-based stubs instead of
    calling an LLM. Set to True only when an LLM integration is configured.
    Env var: AI_ENABLED
    """

    # ── Logging ────────────────────────────────────────────────────────────────
    log_level: str = "INFO"
    """
    Logging level for the application. Must be one of:
    DEBUG, INFO, WARNING, ERROR, CRITICAL.
    Do NOT use DEBUG in production — debug logs may capture request bodies
    that contain patient data.
    Env var: LOG_LEVEL
    """


def get_settings() -> Settings:
    """Create and return a Settings instance."""
    return Settings()
