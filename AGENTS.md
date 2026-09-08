# MediKiosk Development Rules (AGENTS.md)

These rules govern all AI-assisted and human development on this project.

## Project Compliance

1. **Follow the project specification.** The SIH 2026 problem statement is the primary source of truth. Do not invent additional product requirements. If something is not specified, clearly label it as an engineering assumption.

2. **Do not modify unrelated files.** Changes should be scoped to the task at hand.

3. **Do not introduce dependencies without explaining why.** Every new dependency must have a clear justification documented in the PR or commit message.

4. **Never expose API keys or secrets.** All secrets must be stored in environment variables or secret management systems, never in source code or version control.

## Architecture

5. **Keep frontend and backend concerns separate.** The React frontend communicates with the FastAPI backend exclusively through well-defined REST/WebSocket APIs. No backend logic in the frontend; no frontend rendering in the backend.

6. **Keep AI services modular.** Each AI capability (ASR, LLM dialogue, OCR, summarization) must be an independent, swappable module behind a clean interface. Do not tightly couple AI providers to business logic.

7. **Do not make architectural changes without explaining them.** Any change to the project structure, technology stack, or system design must be discussed and justified before implementation.

## Clinical Safety

8. **Validate all AI-generated structured data.** Every output from AI services (extracted entities, structured history, flagged values) must pass validation before being stored or displayed.

9. **AI-generated clinical summaries must always be treated as drafts requiring physician review.** The UI and API must enforce that summaries are explicitly marked as drafts and require physician confirmation before becoming part of the medical record.

10. **Never allow the system to autonomously diagnose a patient.** MediKiosk assists with history elicitation and document digitization. It does not diagnose, prescribe, or make autonomous clinical decisions.

## Quality Assurance

11. **Write tests for backend functionality.** All API endpoints, services, and AI pipelines must have corresponding test coverage.

12. **Run tests after implementing features.** No feature is considered complete until its tests pass.

13. **Verify frontend changes in the browser.** UI changes must be visually verified before being considered complete.

## Integration

14. **Do not implement ABDM integration until the integration architecture has been finalized.** ABDM/ABHA/FHIR integration is a critical, compliance-sensitive module. Its architecture must be reviewed and approved before any implementation begins.
