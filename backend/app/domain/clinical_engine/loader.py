"""
Clinical Template Loader — Clinical Engine.

Generic YAML loading functions for the Phase 7 clinical content pack.
All functions read from the filesystem using PyYAML and return
Pydantic model instances or plain dicts as appropriate.

This module does NOT validate cross-references (trigger vocabulary,
red-flag slot references, etc.) — that is the validator's job.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml
from pydantic import ValidationError as PydanticValidationError

from app.domain.clinical_engine.template_schema import (
    ClinicalTemplate,
    GeneralHistoryModule,
)
from app.utils.errors import ClinicalEngineError


# ── Generic YAML loading ────────────────────────────────────────────────────


def load_yaml_file(path: Path | str) -> dict[str, Any]:
    """
    Load a YAML file and return its contents as a dict.

    Raises:
        ClinicalEngineError: If the file cannot be read or parsed.
    """
    path = Path(path)
    if not path.is_file():
        raise ClinicalEngineError(
            message=f"YAML file not found: {path}",
            detail=str(path),
        )
    try:
        with path.open("r", encoding="utf-8") as fh:
            data = yaml.safe_load(fh)
    except yaml.YAMLError as exc:
        raise ClinicalEngineError(
            message=f"Failed to parse YAML: {path.name}",
            detail=str(exc),
        ) from exc

    if not isinstance(data, dict):
        raise ClinicalEngineError(
            message=f"YAML root must be a mapping: {path.name}",
            detail=f"Got {type(data).__name__}",
        )
    return data


# ── Template loading ─────────────────────────────────────────────────────────


def load_template(path: Path | str) -> ClinicalTemplate:
    """
    Load a clinical complaint template from a YAML file.

    Returns a fully parsed ``ClinicalTemplate`` Pydantic model.

    Raises:
        ClinicalEngineError: If the file is missing or YAML is invalid.
        pydantic.ValidationError: If the parsed data does not match
            the ClinicalTemplate schema.
    """
    data = load_yaml_file(path)
    return ClinicalTemplate(**data)


def load_general_module(path: Path | str) -> GeneralHistoryModule:
    """
    Load a reusable general-history module from a YAML file.

    Returns a ``GeneralHistoryModule`` — NOT a full ClinicalTemplate.

    Raises:
        ClinicalEngineError: If the file is missing or YAML is invalid.
        pydantic.ValidationError: If the parsed data does not match
            the GeneralHistoryModule schema.
    """
    data = load_yaml_file(path)
    return GeneralHistoryModule(**data)


# ── Trigger registry loading ────────────────────────────────────────────────


def load_trigger_registry(path: Path | str) -> dict[str, list[str]]:
    """
    Load the closed trigger vocabulary from triggers.yaml.

    Returns a mapping of ``template_id → list[trigger_id]``.

    The top-level keys ``version`` and ``status`` are metadata and
    are stripped from the result.

    Raises:
        ClinicalEngineError: If the file is missing or malformed.
    """
    data = load_yaml_file(path)
    triggers_section = data.get("triggers")
    if not isinstance(triggers_section, dict):
        raise ClinicalEngineError(
            message="triggers.yaml must contain a 'triggers' mapping.",
            detail=str(path),
        )
    # Validate structure: each value must be a list of strings
    result: dict[str, list[str]] = {}
    for template_id, trigger_ids in triggers_section.items():
        if not isinstance(trigger_ids, list):
            raise ClinicalEngineError(
                message=(
                    f"Trigger list for '{template_id}' must be a list, "
                    f"got {type(trigger_ids).__name__}."
                ),
            )
        result[template_id] = [str(tid) for tid in trigger_ids]
    return result


# ── Red-flag rules loading ──────────────────────────────────────────────────


def load_red_flag_rules(path: Path | str) -> dict[str, Any]:
    """
    Load global red-flag rules from red_flags.yaml.

    Returns the parsed YAML dict.  This is data loading only —
    rules are NOT evaluated.

    Raises:
        ClinicalEngineError: If the file is missing or malformed.
    """
    return load_yaml_file(path)
