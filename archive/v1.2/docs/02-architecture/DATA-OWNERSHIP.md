# Data Ownership Register

Status: `EMPTY — DISCOVERY REQUIRED`

| State | Canonical owner | Writers | Readers | Persistence | Replication | Recovery |
|---|---|---|---|---|---|---|
| — | — | — | — | — | — | — |

Rules:

- One row per mutable domain fact or aggregate.
- Cache, projection, UI copy, animation state, and replicated mirror are labeled derived.
- Multiple writers require a single serialization/authority contract.
- Unknown ownership blocks implementation that would write the state.

