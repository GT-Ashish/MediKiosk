# MediKiosk

**AI-Powered Clinical History Software Platform**

> Smart India Hackathon (SIH) 2026 Project

---

## Overview

MediKiosk is an AI-powered clinical history software platform designed for Indian hospitals. It enables patients to independently record a comprehensive medical history through natural spoken conversation and guided touchscreen interaction, scan and digitize existing physical medical documents, and generate a structured, physician-ready clinical history summary — all completed before the consultation begins.

### Core Modules

| Module | Description |
|--------|-------------|
| **Module A** — Conversational History Engine | Adaptive voice + touch clinical history interview in Indian languages |
| **Module B** — Document Digitization & Intelligence | OCR and AI extraction from prescriptions, lab reports, discharge summaries |
| **Module C** — Summary Generator | Structured, physician-ready clinical history summary in standard format |
| **Module D** — Consent, Privacy & ABDM Integration | ABHA linkage, DPDP Act 2023 compliance, FHIR interoperability |

### Patient Journey

1. **Identify** — Patient authenticates via ABHA ID / Aadhaar, selects language, grants consent
2. **Converse** — AI conducts adaptive voice + touch history interview
3. **Scan** — Patient uploads prior medical documents; AI digitizes and structures them
4. **Summarize & Route** — AI generates structured summary, pushes to HIS, links to ABHA
5. **Consult** — Physician reviews complete history in seconds, edits/confirms

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | React, Vite, Tailwind CSS |
| Backend | Python, FastAPI |
| Database | PostgreSQL |
| AI Services | Python-based (LLM, ASR, OCR — to be integrated) |
| Version Control | Git + GitHub |

---

## Project Structure

```
MediKiosk/
├── frontend/          # React + Vite + Tailwind CSS application
├── backend/           # FastAPI Python backend
├── ai/                # AI service modules (ASR, LLM, OCR, Summarization)
├── database/          # Database schemas, migrations, seed data
├── tests/             # Test suites (backend, AI, integration)
├── docs/              # Project documentation
├── scripts/           # Utility and setup scripts
├── .gitignore         # Git ignore rules
├── README.md          # This file
└── AGENTS.md          # Development rules for AI-assisted coding
```

---

## Development Status

> **Phase: Project Scaffolding** (Initial Setup)

- [x] Repository initialized
- [x] Project structure created
- [x] Development rules established (AGENTS.md)
- [ ] Frontend initialized (React + Vite + Tailwind CSS)
- [ ] Backend initialized (FastAPI)
- [ ] Database schema designed
- [ ] AI service interfaces defined
- [ ] Module A — Conversational History Engine
- [ ] Module B — Document Digitization
- [ ] Module C — Summary Generator
- [ ] Module D — ABDM Integration

---

## Getting Started

> Setup instructions will be added as the frontend and backend are initialized.

---

## License

TBD

---

## Team

SIH 2026 Team — Details TBD
