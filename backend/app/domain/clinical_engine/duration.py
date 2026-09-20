"""
Duration Value Model — Clinical Engine.

Represents a duration measurement with a numeric value and unit.
Used by clinical template slots of type ``duration`` (e.g. time_to_peak
in the headache template).

Supports normalization to a canonical unit (e.g. seconds → minutes)
for slots that declare a required unit.  This is deliberately
minimal — not a general-purpose units library.
"""

from __future__ import annotations

from pydantic import BaseModel, Field, model_validator


# ── Conversion table ──────────────────────────────────────────────────────────
# Mapping: (from_unit, to_unit) → multiplier
# Only the conversions actually needed by the clinical content pack.

_CONVERSION_FACTORS: dict[tuple[str, str], float] = {
    ("seconds", "minutes"): 1.0 / 60.0,
    ("minutes", "minutes"): 1.0,
    ("hours", "minutes"): 60.0,
}


class DurationValue(BaseModel):
    """
    A duration measurement with numeric value and unit.

    Attributes:
        numeric_value: The numeric magnitude (must be ≥ 0).
        unit: The unit of the duration (e.g. 'minutes', 'seconds', 'hours').
    """

    numeric_value: float = Field(
        ...,
        ge=0,
        description="Numeric magnitude of the duration (non-negative).",
    )
    unit: str = Field(
        ...,
        min_length=1,
        description="Unit of the duration (e.g. 'minutes', 'seconds').",
    )

    @model_validator(mode="after")
    def _validate_unit_not_blank(self) -> DurationValue:
        """Reject whitespace-only units."""
        if not self.unit.strip():
            raise ValueError("Duration unit must not be blank.")
        return self

    # ── Normalization ──────────────────────────────────────────────────────

    def normalize_to(self, canonical_unit: str) -> DurationValue:
        """
        Return a new DurationValue converted to *canonical_unit*.

        Raises:
            ValueError: If the conversion from self.unit → canonical_unit
                is not supported.
        """
        if self.unit == canonical_unit:
            return self.model_copy()

        key = (self.unit, canonical_unit)
        factor = _CONVERSION_FACTORS.get(key)
        if factor is None:
            raise ValueError(
                f"Unsupported duration conversion: "
                f"{self.unit!r} → {canonical_unit!r}"
            )
        return DurationValue(
            numeric_value=round(self.numeric_value * factor, 6),
            unit=canonical_unit,
        )
