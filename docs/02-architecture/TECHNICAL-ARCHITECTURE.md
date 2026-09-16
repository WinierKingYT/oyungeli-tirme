# Technical Architecture Standard

Status: `PROPOSED — REPOSITORY DISCOVERY REQUIRED`

## Required architecture views

1. Module/context map and dependency directions.
2. Canonical state ownership matrix.
3. Command, event, query, and replication contracts.
4. Runtime lifecycle and failure recovery.
5. Save/version/migration model.
6. Network authority and late-join model.
7. Asset/content dependency graph.
8. Build, test, packaging, and release topology.

## Design constraints

- Canonical state is explicit and singular.
- Presentation consumes domain state; it does not secretly own gameplay truth.
- Cross-system communication uses accepted contracts.
- Background/tick work is bounded and observable.
- Persistent formats are versioned before production use.
- Multiplayer authority is declared per state transition.
- External dependencies have failure behavior and ownership.

The actual Unreal modules and subsystem types must be derived from the repository; this document does not preselect them.

