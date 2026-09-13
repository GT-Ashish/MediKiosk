# Changelog

## 1.1.0

Safety/functional revision following structured review.

### Fixed

- Added an explicit minute unit and normalization rule for headache
  `time_to_peak`.
- Replaced free-text substring red-flag checks with structured boolean fields.
- Added explicit immune-suppression state.
- Removed free-text dependency for the immune-suppression red flag.
- Renamed the abdominal reproductive context module to
  `reproductive_history_context`.
- Updated fixtures to assert the new structured safety fields.

### Design decision

The content pack remains an interview-history data set,
not a diagnostic or treatment engine.

Red flags route to clinician/triage review only.
