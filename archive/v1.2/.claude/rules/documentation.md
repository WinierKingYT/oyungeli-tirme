---
paths:
  - "docs/**/*.md"
  - "*.md"
---

# Documentation rules

- Use lifecycle labels defined in `docs/08-process/SYSTEM-LIFECYCLE.md`.
- Separate fact, decision, hypothesis, proposal, and unknown.
- Every accepted claim must link to inspectable evidence.
- Do not mark a system `ACCEPTED` without an independent review record.
- Keep IDs stable: `SYS-*`, `TASK-*`, `ADR-*`, `RISK-*`, `BUG-*`, `EVID-*`.
- State dates in ISO 8601 and revisions as immutable commit SHAs when available.
- A document may describe intended behavior only when clearly labeled `PROPOSED`.
- Update authority indexes when adding an accepted ADR, system, milestone, or evidence pack.

