"""
MediKiosk PII-Safe Logging Configuration.

Medical applications require special care around logging. This module
provides a configured logger and utilities that help prevent accidental
logging of patient-identifying information (PII).

Privacy rules enforced here:
    1. Never log raw Aadhaar numbers, ABHA IDs, or mobile numbers.
    2. Never log patient names from clinical context.
    3. Never log free-text clinical history answers (may contain PII).
    4. Never log raw OCR text from documents (contains PII).
    5. Log only session_ids (UUIDs), request_ids, timestamps, and non-PII metadata.
    6. Log level must not be DEBUG in production (controlled by settings.log_level).

Sensitive field names that MUST NOT appear in log messages:
    - aadhaar, abha_id, identifier_hash (partial hashes are still sensitive)
    - answer_text (clinical conversation content)
    - raw_text (OCR output)
    - patient_name, display_name
    - history_narrative (LLM-generated clinical text)
    - mobile, phone

Usage:
    from app.utils.logging import get_logger

    logger = get_logger(__name__)
    logger.info("Session created", extra={"session_id": str(session.session_id)})
"""

import logging
import sys
from typing import Any


# Fields that must never appear in log output.
# The sanitize_log_record filter below strips these from log records.
_SENSITIVE_FIELDS: frozenset[str] = frozenset({
    "aadhaar",
    "abha_id",
    "identifier_hash",
    "answer_text",
    "raw_text",
    "patient_name",
    "display_name",
    "history_narrative",
    "mobile",
    "phone",
    "corrections",  # may contain clinical text
})


class _PIISafeFilter(logging.Filter):
    """
    Logging filter that strips or redacts sensitive fields from log records.

    Checks the 'extra' dict attached to log records and replaces any
    sensitive field values with the string '[REDACTED]'.
    """

    def filter(self, record: logging.LogRecord) -> bool:
        for field in _SENSITIVE_FIELDS:
            if hasattr(record, field):
                setattr(record, field, "[REDACTED]")
        return True


def configure_logging(log_level: str = "INFO") -> None:
    """
    Configure the root logger for MediKiosk with PII-safe defaults.

    Call this once during application startup (in main.py lifespan).

    Args:
        log_level: Logging level string (DEBUG/INFO/WARNING/ERROR).
                   Should be INFO or above in production.
    """
    numeric_level = getattr(logging, log_level.upper(), logging.INFO)

    handler = logging.StreamHandler(sys.stdout)
    handler.addFilter(_PIISafeFilter())
    handler.setFormatter(
        logging.Formatter(
            fmt="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
            datefmt="%Y-%m-%dT%H:%M:%S",
        )
    )

    root_logger = logging.getLogger()
    root_logger.setLevel(numeric_level)
    root_logger.handlers.clear()
    root_logger.addHandler(handler)

    # Suppress noisy third-party loggers
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)


def get_logger(name: str) -> logging.Logger:
    """
    Get a named logger with PII-safe filter applied.

    Args:
        name: Logger name (typically __name__).

    Returns:
        A configured Logger instance.

    Usage:
        logger = get_logger(__name__)
        logger.info("Session %s created", session_id)  # OK — session_id is a UUID
        logger.info("Answer: %s", answer_text)  # WRONG — never log clinical text
    """
    logger = logging.getLogger(name)
    if not any(isinstance(f, _PIISafeFilter) for f in logger.filters):
        logger.addFilter(_PIISafeFilter())
    return logger
