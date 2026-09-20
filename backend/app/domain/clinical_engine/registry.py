"""
Clinical Template Registry — Clinical Engine.

Central registry for loaded and validated clinical templates.
Provides version-pinned retrieval, general-module resolution,
and bulk validation.

The registry is populated at application startup from the YAML
content directory and is read-only at runtime.
"""

from __future__ import annotations

from pathlib import Path

from app.domain.clinical_engine.loader import (
    load_general_module,
    load_template,
    load_trigger_registry,
)
from app.domain.clinical_engine.template_schema import (
    ClinicalTemplate,
    GeneralHistoryModule,
    SlotDefinition,
)
from app.domain.clinical_engine.validator import (
    ValidationResult,
    validate_template,
    validate_template_set,
)
from app.utils.errors import TemplateNotFoundError, TemplateValidationError


# ── Content directory layout ─────────────────────────────────────────────────

_CONTENT_DIR = Path(__file__).parent / "content"
_TEMPLATES_DIR = _CONTENT_DIR / "templates"
_TRIGGERS_FILE = _CONTENT_DIR / "triggers.yaml"

# Template file stems that are full ClinicalTemplates (not modules)
_COMPLAINT_TEMPLATES = [
    "chest_pain",
    "fever",
    "cough",
    "abdominal_pain",
    "headache",
]

# Known general-history module
_GENERAL_MODULE_ID = "general_history"


class TemplateRegistry:
    """
    Registry of validated clinical templates with version-pinned retrieval.

    Usage::

        registry = TemplateRegistry()
        registry.load_content_directory()
        template = registry.get("chest_pain", "1.0.0")
    """

    def __init__(self) -> None:
        # (template_id, version) → ClinicalTemplate
        self._templates: dict[tuple[str, str], ClinicalTemplate] = {}
        # template_id → latest version string
        self._latest: dict[str, str] = {}
        # module_id → GeneralHistoryModule
        self._general_modules: dict[str, GeneralHistoryModule] = {}
        # template_id → list[trigger_id]
        self._trigger_registry: dict[str, list[str]] = {}

    # ── Registration ─────────────────────────────────────────────────────

    def register(self, template: ClinicalTemplate) -> None:
        """
        Register a validated template.

        Raises:
            TemplateValidationError: If a template with the same
                (template_id, version) is already registered.
        """
        key = (template.template_id, template.version)
        if key in self._templates:
            raise TemplateValidationError(
                template_id=template.template_id,
                errors=[
                    f"Template '{template.template_id}' version "
                    f"'{template.version}' is already registered."
                ],
            )
        self._templates[key] = template
        # Update latest tracker
        current_latest = self._latest.get(template.template_id)
        if current_latest is None or template.version > current_latest:
            self._latest[template.template_id] = template.version

    def register_general_module(self, module: GeneralHistoryModule) -> None:
        """Register a reusable general-history module."""
        self._general_modules[module.template_id] = module

    # ── Retrieval ────────────────────────────────────────────────────────

    def get(self, template_id: str, version: str) -> ClinicalTemplate:
        """
        Retrieve a specific template by ID and version.

        Raises:
            TemplateNotFoundError: If the template/version is not registered.
        """
        key = (template_id, version)
        template = self._templates.get(key)
        if template is None:
            raise TemplateNotFoundError(
                template_id=template_id,
                version=version,
            )
        return template

    def get_latest(self, template_id: str) -> ClinicalTemplate:
        """
        Retrieve the latest version of a template.

        Raises:
            TemplateNotFoundError: If no versions are registered.
        """
        version = self._latest.get(template_id)
        if version is None:
            raise TemplateNotFoundError(template_id=template_id)
        return self.get(template_id, version)

    def list_available(self) -> list[tuple[str, str]]:
        """Return a list of (template_id, version) pairs."""
        return sorted(self._templates.keys())

    # ── Validation ───────────────────────────────────────────────────────

    def validate_all(self) -> ValidationResult:
        """
        Validate all registered templates as a set.

        Returns a structured ``ValidationResult``.
        """
        templates = list(self._templates.values())
        return validate_template_set(
            templates,
            trigger_registry=self._trigger_registry,
            general_modules=self._general_modules,
        )

    # ── General module resolution ────────────────────────────────────────

    def resolve_general_modules(
        self, template: ClinicalTemplate,
    ) -> list[SlotDefinition]:
        """
        Resolve the general modules referenced by a template.

        Returns a flat list of ``SlotDefinition`` objects from all
        referenced general modules.

        Raises:
            TemplateNotFoundError: If a referenced module is not registered.
        """
        resolved_slots: list[SlotDefinition] = []
        for mod_id in template.general_modules:
            module = self._general_modules.get(mod_id)
            if module is None:
                raise TemplateNotFoundError(template_id=mod_id)
            resolved_slots.extend(module.slots)
        return resolved_slots

    # ── Bulk loading ─────────────────────────────────────────────────────

    def load_content_directory(
        self,
        content_dir: Path | None = None,
    ) -> ValidationResult:
        """
        Discover and load all templates from the content directory.

        1. Loads the trigger registry
        2. Loads the general-history module
        3. Loads all complaint templates
        4. Validates the full set
        5. Registers everything if validation passes

        Returns the ``ValidationResult``.

        Raises:
            TemplateValidationError: If any template has validation errors.
        """
        base = content_dir or _CONTENT_DIR
        templates_dir = base / "templates"
        triggers_file = base / "triggers.yaml"

        # 1. Load trigger registry
        if triggers_file.is_file():
            self._trigger_registry = load_trigger_registry(triggers_file)

        # 2. Load general-history module
        general_path = templates_dir / f"{_GENERAL_MODULE_ID}.yaml"
        if general_path.is_file():
            module = load_general_module(general_path)
            self._general_modules[module.template_id] = module

        # 3. Load complaint templates
        loaded_templates: list[ClinicalTemplate] = []
        for stem in _COMPLAINT_TEMPLATES:
            tmpl_path = templates_dir / f"{stem}.yaml"
            if tmpl_path.is_file():
                template = load_template(tmpl_path)
                loaded_templates.append(template)

        # 4. Validate the full set
        result = validate_template_set(
            loaded_templates,
            trigger_registry=self._trigger_registry,
            general_modules=self._general_modules,
        )

        if not result.is_valid:
            error_messages = [str(i) for i in result.issues if i.severity == "error"]
            raise TemplateValidationError(
                template_id="<registry>",
                errors=error_messages,
            )

        # 5. Register everything
        for template in loaded_templates:
            key = (template.template_id, template.version)
            self._templates[key] = template
            current_latest = self._latest.get(template.template_id)
            if current_latest is None or template.version > current_latest:
                self._latest[template.template_id] = template.version

        return result

    # ── Properties ───────────────────────────────────────────────────────

    @property
    def trigger_registry(self) -> dict[str, list[str]]:
        """The loaded trigger vocabulary."""
        return dict(self._trigger_registry)

    @property
    def general_modules(self) -> dict[str, GeneralHistoryModule]:
        """The loaded general modules."""
        return dict(self._general_modules)
