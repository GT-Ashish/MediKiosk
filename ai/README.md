# MediKiosk AI Services

Python-based AI service modules.

## Status

Not yet initialized. AI integrations (LLM, ASR, OCR) will be added as modular services.

## Planned Modules

| Module | Purpose | Status |
|--------|---------|--------|
| `asr/` | Automatic Speech Recognition — Indian language voice capture | Not started |
| `llm/` | LLM-powered conversational history elicitation & dialogue management | Not started |
| `ocr/` | Medical document OCR — handwritten and printed, multilingual | Not started |
| `summarizer/` | Clinical history summary generation in standard format | Not started |
| `red_flag/` | Emergency symptom detection and triage alerting | Not started |
| `ayush/` | AYUSH/Ayurvedic history mode (Dashavidha Pariksha) | Not started |

## Planned Structure

```
ai/
├── __init__.py
├── asr/                # Speech recognition service
│   ├── __init__.py
│   └── service.py
├── llm/                # LLM dialogue engine
│   ├── __init__.py
│   └── service.py
├── ocr/                # Document OCR and extraction
│   ├── __init__.py
│   └── service.py
├── summarizer/         # Clinical summary generation
│   ├── __init__.py
│   └── service.py
├── red_flag/           # Emergency symptom detection
│   ├── __init__.py
│   └── service.py
├── ayush/              # AYUSH history mode
│   ├── __init__.py
│   └── service.py
└── models/             # Shared model files (gitignored large binaries)
```

## Design Principles

- Each AI module exposes a clean Python interface (abstract base class)
- Provider implementations are swappable (e.g., swap ASR providers without changing business logic)
- All AI outputs are validated before being passed to the backend
- Clinical summaries are always marked as drafts requiring physician review
