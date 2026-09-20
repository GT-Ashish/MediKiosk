"""
MediKiosk Domain Error Types.

Centralised error hierarchy for the MediKiosk backend.

Design principles:
    1. All domain errors inherit from MediKioskError.
    2. Each error carries a human-readable message and an optional detail.
    3. HTTP status codes are NOT assigned here — that is the API layer's concern.
       The API layer maps these domain errors to appropriate HTTP responses.
    4. Internal details (stack traces, DB errors) are NEVER exposed to clients.
    5. Error messages must not contain PII (patient names, Aadhaar, mobile numbers).

Error → HTTP mapping (reference for API layer):
    SessionNotFoundError      → 404 Not Found
    ConsentRequiredError      → 403 Forbidden
    ValidationError           → 422 Unprocessable Entity
    DocumentProcessingError   → 500 Internal Server Error
    AIProcessingError         → 502 Bad Gateway (upstream AI failure)
    UnsupportedOperationError → 501 Not Implemented
    MediKioskError (base)     → 500 Internal Server Error
"""


class MediKioskError(Exception):
    """
    Base exception for all MediKiosk domain errors.

    All application-level exceptions should inherit from this class
    so that the global exception handler can catch and handle them
    consistently.
    """

    def __init__(self, message: str, detail: str | None = None) -> None:
        super().__init__(message)
        self.message = message
        self.detail = detail

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(message={self.message!r})"


class SessionNotFoundError(MediKioskError):
    """
    Raised when a requested kiosk session does not exist.

    This typically happens when:
    - An expired session ID is used
    - A session ID is fabricated or invalid
    - The in-memory store has been cleared (e.g., server restart)
    """

    def __init__(self, session_id: object) -> None:
        super().__init__(
            message=f"Session not found: {session_id}",
            detail="The requested session does not exist or has expired.",
        )
        self.session_id = session_id


class ConsentRequiredError(MediKioskError):
    """
    Raised when an operation requires patient consent that has not been given.

    Operations that require consent:
    - Recording clinical history answers
    - Uploading documents
    - Generating AI summaries
    """

    def __init__(self, session_id: object | None = None) -> None:
        super().__init__(
            message="Patient consent is required before proceeding.",
            detail=(
                "The patient must provide informed consent (data use and AI processing) "
                "before clinical data can be collected."
            ),
        )
        self.session_id = session_id


class MediKioskValidationError(MediKioskError):
    """
    Raised when domain-level validation fails beyond Pydantic's model validation.

    Examples:
    - Severity score outside 1–10 after Pydantic parsing
    - Both acknowledgements not confirmed for consent
    - Invalid session state transition (e.g., completing an already-abandoned session)
    """

    def __init__(self, message: str, field: str | None = None) -> None:
        super().__init__(
            message=message,
            detail=f"Validation failed for field: {field}" if field else None,
        )
        self.field = field


class DocumentProcessingError(MediKioskError):
    """
    Raised when document OCR or entity extraction fails.

    The document is marked as FAILED and the error is recorded.
    Details are logged server-side but NOT returned to the client.
    """

    def __init__(self, document_id: object, reason: str | None = None) -> None:
        super().__init__(
            message=f"Document processing failed for document: {document_id}",
            # reason is logged server-side only — never exposed to client
            detail=reason,
        )
        self.document_id = document_id


class AIProcessingError(MediKioskError):
    """
    Raised when an AI service call fails (LLM, ASR, etc.).

    This is a transient error — the operation may be retried.
    Details are logged server-side but NOT returned to the client.
    The client receives a generic "AI service temporarily unavailable" message.
    """

    def __init__(self, service: str, reason: str | None = None) -> None:
        super().__init__(
            message=f"AI service error: {service}",
            detail=reason,
        )
        self.service = service


class UnsupportedOperationError(MediKioskError):
    """
    Raised when a requested operation is not yet implemented.

    Used during Phase 5–6 to clearly signal that an endpoint exists
    architecturally but does not yet have a concrete implementation.
    Maps to HTTP 501 Not Implemented.
    """

    def __init__(self, operation: str) -> None:
        super().__init__(
            message=f"Operation not yet implemented: {operation}",
            detail=(
                "This feature is defined in the MediKiosk architecture "
                "but is pending implementation in a future phase."
            ),
        )
        self.operation = operation


# ── Phase 7: Clinical Engine Errors ───────────────────────────────────────────


class ClinicalEngineError(MediKioskError):
    """
    Base exception for the Phase 7 clinical history engine.

    All clinical-engine-specific errors inherit from this class
    so they can be caught as a group while still being part of
    the top-level MediKioskError hierarchy.
    """

    def __init__(self, message: str, detail: str | None = None) -> None:
        super().__init__(message=message, detail=detail)


class InvalidSlotTransitionError(ClinicalEngineError):
    """
    Raised when a slot state transition violates the allowed
    transition rules (e.g. DECLINED → KNOWN).

    Carries the current and target statuses for diagnostics.
    """

    def __init__(
        self,
        current_status: object,
        target_status: object,
        reason: str | None = None,
    ) -> None:
        detail = reason or (
            f"Transition from {current_status!r} to {target_status!r} "
            f"is not allowed."
        )
        super().__init__(
            message=(
                f"Invalid slot transition: "
                f"{current_status!r} → {target_status!r}"
            ),
            detail=detail,
        )
        self.current_status = current_status
        self.target_status = target_status


class TemplateValidationError(ClinicalEngineError):
    """
    Raised when a clinical template fails structural validation.

    Carries the template ID and a list of validation error messages.
    """

    def __init__(
        self,
        template_id: str,
        errors: list[str] | None = None,
    ) -> None:
        error_summary = "; ".join(errors) if errors else "Unknown validation error"
        super().__init__(
            message=f"Template validation failed: {template_id}",
            detail=error_summary,
        )
        self.template_id = template_id
        self.validation_errors = errors or []


class TemplateNotFoundError(ClinicalEngineError):
    """
    Raised when a requested template is not found in the registry.
    """

    def __init__(
        self,
        template_id: str,
        version: str | None = None,
    ) -> None:
        version_part = f" version '{version}'" if version else ""
        super().__init__(
            message=f"Template not found: '{template_id}'{version_part}",
            detail=(
                f"The requested template '{template_id}'{version_part} "
                f"is not registered."
            ),
        )
        self.template_id = template_id
        self.version = version
