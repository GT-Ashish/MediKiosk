"""
MediKiosk Infrastructure — External Integrations.

Integration modules will be implemented here in Phase 7+ for:

OCR Integration (Phase 7):
    Pluggable OCR provider behind a clean interface.
    Planned providers: Tesseract (open-source), Google Vision, Azure AI Document Intelligence.
    Interface contract: accepts bytes (image/PDF), returns raw_text: str.
    Swapping providers requires only changing the registered implementation.

LLM Integration (Phase 7):
    Pluggable LLM provider for history summarisation and entity extraction.
    Planned providers: Google Gemini, Ollama (local), Azure OpenAI.
    Interface contract: accepts structured prompt + ClinicalHistory, returns StructuredHistorySummary draft.
    All LLM output must be validated against domain schemas before storage.

ABDM Integration (Phase 8+):
    ABDM/ABHA patient identity verification and consent framework.
    Must be reviewed for compliance before implementation begins (AGENTS.md Rule 14).
    Interface contract: accepts ABHA ID, returns PatientIdentifier (hashed).

ASR Integration (Phase 7+):
    Pluggable ASR (Automatic Speech Recognition) provider.
    Current frontend uses Web Speech API. Backend ASR would improve accuracy for
    Indian language support.
    Planned: Whisper (local), Google STT, Bhashini (Indian language ASR).

Current status: Empty — awaiting Phase 7+.
"""
