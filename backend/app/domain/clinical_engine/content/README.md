# MediKiosk Phase 7 Clinical Content Pack v1.1

STATUS: DEMO / NON-PRODUCTION CLINICAL CONTENT

This is the content layer for the Phase 7 adaptive history engine. It is intentionally
data-driven: the engine decides WHAT to ask; the LLM may extract values and phrase
approved requests, but must not invent slots, select the next slot, invent red flags,
or diagnose.

Initial complaint templates:
1. chest_pain
2. fever
3. cough
4. abdominal_pain
5. headache

Safety:
red flags are clinician/triage routing signals only, never diagnoses or treatment advice.
This pack is not a clinical protocol and must be clinically reviewed before real-world use.

Sources used:
- AAFP chest-pain guidance
- AAFP cough guidance
- AAFP acute-abdominal-pain guidance
- AAFP acute-headache/SNNOOP10 guidance
- Merck Manual Professional fever guidance
- Merck Manual Professional abdominal-pain guidance
- American Heart Association heart-attack warning signs
- CDC respiratory/infectious symptom guidance
- NCBI MedGen / BioPortal SNOMED CT references

## v1.1 safety corrections

### Thunderclap headache
`headache.time_to_peak` now has:
- canonical unit: minutes
- bounded range: 0–1440 minutes

Extraction must normalize phrases such as:
- "30 seconds" → 0.5 minutes
- "1 minute" → 1 minute
- "5 minutes" → 5 minutes

The deterministic red-flag engine must compare the normalized numeric value.

### Structured safety fields
Safety predicates must not depend on substring matching in free-text slots.

Explicit structured boolean fields are used for:
- confusion
- severe neck stiffness
- breathing difficulty
- inability to keep fluids down
- immune suppression
- bowel obstruction symptoms
- persistent vomiting / inability to keep fluids down
- new neurologic deficit
- fever
- neck stiffness
- severe eye symptoms

### Reproductive context
The abdominal-pain context module is named:
`reproductive_history_context`

This avoids a collision with base slot naming.

## Schema naming authority

For Phase 7 v1.1 implementation, this content pack is the concrete naming authority.

Use:

- `question_budget.min_questions`
- `question_budget.max_questions`
- `general_modules`
- template-level `triggers`
- `red_flags[].when`
- `context_modules[].triggers`

Do not silently translate these names back into the older architecture draft.

## Clinical boundary

This system is a history-taking and routing-support tool.

It does NOT:
- diagnose disease
- recommend treatment
- prescribe medication
- calculate clinical risk scores
- replace physician assessment
- infer physical examination findings

The kiosk cannot reliably assess findings such as:
- papilledema
- abdominal guarding
- rebound tenderness
- vital-sign instability
- oxygen saturation
- formal neurologic examination

unless a future validated device/workflow explicitly provides that information.

Red flags create clinician/triage review events only.
