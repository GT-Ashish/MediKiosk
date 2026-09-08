# MediKiosk Database

PostgreSQL database schemas, migrations, and seed data.

## Status

Not yet initialized. Database design will begin after core data models are defined.

## Planned Structure

```
database/
├── migrations/         # Database migration scripts
├── schemas/            # SQL schema definitions
├── seeds/              # Seed data for development/testing
└── README.md           # This file
```

## Key Entities (Preliminary)

These are engineering assumptions based on the SIH problem statement and will be refined during database design:

- **Patients** — ABHA ID, demographics, language preference
- **Sessions** — Kiosk interaction sessions with consent records
- **ClinicalHistory** — Structured history data (chief complaint, HPI, past history, etc.)
- **Documents** — Uploaded medical documents with OCR results
- **Summaries** — Generated clinical summaries with physician review status
- **AyushHistory** — Dashavidha Pariksha data for AYUSH OPDs
