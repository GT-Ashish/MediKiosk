# Clinical-content source notes

## Chest pain

History emphasizes:
- onset/acuity
- severity
- location
- radiation
- exertional relationship
- dyspnea
- associated symptoms

Sources:
- AAFP chest-pain evaluation
- American Heart Association warning signs

## Fever

History emphasizes:
- duration/pattern
- measured temperature when available
- localizing symptoms
- exposures/travel
- medications
- immune-risk context
- hydration

Sources:
- Merck Manual Professional fever
- CDC respiratory/infectious symptom guidance

## Cough

History emphasizes:
- onset
- duration
- course
- dry vs productive cough
- sputum
- hemoptysis
- dyspnea
- chest pain
- fever
- wheeze
- upper-respiratory symptoms
- smoking/environmental exposure
- respiratory history

Sources:
- AAFP chronic-cough evaluation
- CDC respiratory symptom guidance

## Abdominal pain

History emphasizes:
- onset
- location
- migration
- character
- severity
- aggravating/relieving factors
- vomiting
- bowel changes
- urinary symptoms
- GI bleeding
- fever
- jaundice
- surgery
- reproductive context

Sources:
- AAFP acute abdominal pain
- Merck Manual Professional acute abdominal pain

## Headache

History emphasizes:
- onset
- time-to-peak
- course
- location
- character
- severity
- episode duration
- aggravating factors
- nausea
- sensory sensitivity
- neurologic symptoms
- fever/neck stiffness
- eye symptoms
- trauma
- previous pattern

Sources:
- AAFP acute headache
- AAFP/SNNOOP10 discussion

## SNOMED CT identifiers

Public references were used to cross-check the top-level complaint identifiers:

- Chest pain: 29857009
- Fever: 386661006
- Cough: 49727002
- Abdominal pain: 21522001
- Headache: 25064002

Do not treat this pack as a production terminology authority or clinical protocol.

## v1.1 targeted verification

- AAFP's acute-headache review describes headaches peaking within seconds
  to minutes as requiring prompt evaluation; `time_to_peak` therefore uses
  minutes as its canonical numeric unit.
- CDC lists fever, headache, stiff neck and altered mental status among
  important meningococcal disease symptoms; explicit boolean slots are used
  so the engine does not depend on English keyword matching.
- AAFP notes acute eye pain/red eye/halos as concerning features in headache
  evaluation; the pack therefore uses a dedicated
  `severe_eye_symptom_present` field instead of matching free-text phrases.

These references explain the structural changes; they do not make this
demo pack a production clinical protocol.
