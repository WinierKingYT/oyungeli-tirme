# Independent Review Standard

The READY reviewer must differ from the task author. The acceptance reviewer must not be the task implementer. Neither reviewer changes production code during review.

Each finding records ID, severity, confidence, exact evidence, violated requirement, impact, and correction condition. Review ends with one disposition:

- `ACCEPT`: all required evidence supports the claims.
- `FIX_FIRST`: correctable blocking findings remain.
- `BLOCKED`: responsible evaluation is impossible with current evidence/environment.

Suggestions that do not block acceptance are explicitly separated from findings. A missing mandatory check is a finding, not a suggestion.

READY review produces a receipt bound to the exact task-contract SHA-256; R4 additionally requires a trusted SSH signature. Acceptance review produces a receipt bound to the exact implementation revision, repository-bound seal/diff hashes, and evidence-pack SHA-256. A changed task, implementation, seal, or evidence pack invalidates the corresponding receipt.
