"""
PatientIdentifier — Domain Schema.

A minimal, privacy-preserving reference to a patient.

Privacy architecture:
    - Raw Aadhaar numbers are NEVER stored.
    - If ABHA ID is used, only a SHA-256 hash of the ID is retained.
    - The display_name is optional and populated only from non-sensitive sources
      (e.g., ABHA profile fetch, not from raw ID).
    - ANONYMOUS type is valid for walk-in patients with no digital identity.

ABDM integration note:
    Full ABHA/ABDM identity verification is deferred to Phase 8+.
    This schema defines the contract that ABDM integration will populate.
"""

from enum import Enum

from pydantic import BaseModel, Field


class IdentifierType(str, Enum):
    """
    The type of patient identifier being used.

    ABHA_ID   — Ayushman Bharat Health Account ID (identifier_hash = SHA-256 of ABHA ID)
    MOBILE    — Mobile number (identifier_hash = SHA-256 of mobile number)
    HOSPITAL_ID — Hospital's own patient ID (e.g., OPD number)
    ANONYMOUS — No identifier; walk-in patient
    """

    ABHA_ID = "abha_id"
    MOBILE = "mobile"
    HOSPITAL_ID = "hospital_id"
    ANONYMOUS = "anonymous"


class PatientIdentifier(BaseModel):
    """
    Privacy-preserving patient reference.

    Stores only hashed identifiers — never raw Aadhaar, mobile, or ABHA numbers.
    The display_name is populated only from explicitly consented, non-sensitive sources.
    """

    identifier_type: IdentifierType = Field(
        description="The type of identifier used to reference this patient.",
    )
    identifier_hash: str | None = Field(
        default=None,
        description=(
            "SHA-256 hash of the raw identifier. "
            "NEVER store the raw Aadhaar/ABHA/mobile number. "
            "Must be None for ANONYMOUS type."
        ),
    )
    display_name: str | None = Field(
        default=None,
        description=(
            "Optional display name fetched from a consented source. "
            "Never derived from raw Aadhaar. May be None."
        ),
    )
