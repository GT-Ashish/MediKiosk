# Phase 7 Schema Reconciliation — v1.1

The clinical content pack is the concrete data contract for the first implementation.

## Naming

| Pack v1.1 | Meaning |
|---|---|
| `question_budget.min_questions` | Minimum interview question budget |
| `question_budget.max_questions` | Hard maximum interview question budget |
| `general_modules: [general_history]` | Reference to reusable module content |
| `triggers` | Registered trigger definitions within the template |
| `red_flags[].when` | Deterministic condition tree |
| `context_modules[].triggers` | Trigger IDs that activate the module |
| explicit boolean slots | Safety predicates compare structured values, not free-text substrings |
| `time_to_peak.unit: minutes` | Canonical normalized unit for headache onset-to-peak |

## Required engine interpretation

1. The LLM proposes `slot_updates` only for registered slots.
2. Boolean safety slots resolve to affirmative / negative / unknown.
3. Uncertainty becomes `UNCLEAR`, not `true`.
4. Duration extraction normalizes to the slot's declared canonical unit before
   question selection or red-flag evaluation.
5. Red flags evaluate structured state only.
6. No substring matching is permitted in the deterministic safety engine.
7. Trigger proposals use a closed vocabulary and are backend validated.
8. Template versions are pinned to the session for auditability.

## Clinical boundary

The kiosk cannot reliably assess physical-examination findings such as:
- papilledema
- neck-flexion limitation
- abdominal guarding
- rebound tenderness
- vital-sign instability
- oxygen saturation
- formal neurologic examination

Those remain clinician/triage inputs unless a deployment explicitly adds validated
devices or workflows.
