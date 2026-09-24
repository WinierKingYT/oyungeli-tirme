---
name: close-system
description: Close and optionally freeze a system only after independent acceptance and complete evidence.
disable-model-invocation: true
allowed-tools: Read Grep Glob
---

For `$ARGUMENTS`, verify an independent acceptance receipt bound to the exact implementation revision, repository-bound seal/diff hashes, and evidence-pack SHA-256, P0/P1 zero, complete evidence, reconciled docs, accepted ADRs, no open blockers, versioned interfaces, rollback/migration notes, and a recorded canonical revision.

If complete, prepare closure records and update indexes to `ACCEPTED`. Use `FROZEN` only when change-control rules and a freeze rationale are recorded.

Otherwise return `EVIDENCE_MISSING`, `FIX_FIRST`, or `BLOCKED` without changing the lifecycle label.
