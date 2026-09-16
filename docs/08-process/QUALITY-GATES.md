# Quality Gates

## Discovery gate

Repository reality, unknowns, confidence, and drift are explicit.

## Ready gate

Scope, non-scope, ownership, dependencies, interfaces, lifecycle, risks, quality attributes, acceptance criteria, tests, expected diff, allowed paths, rollback, and stop conditions are complete. An independent receipt binds READY to the final task SHA-256.

## Verification gate

Every applicable criterion maps to inspectable evidence at a known revision and environment.

## Acceptance gate

Independent review, P0/P1 zero, documentation consistency, actual-vs-expected diff reconciliation, independently checked implementation seal/diff hashes, no hidden critical limitations, and an acceptance receipt bound to implementation revision plus evidence SHA-256.

## Freeze gate

Canonical revision, public contracts, migration/rollback, evidence retention, and change-control rule recorded.
