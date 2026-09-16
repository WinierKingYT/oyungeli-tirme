# Save and Persistence Standard

Status: `PROPOSED — VERIFY PROJECT SAVE MODEL`

Persistent formats require schema version, canonical owner, atomicity strategy, validation, corruption behavior, migration, downgrade policy, backup/recovery, identity rules, partial-write handling, and deterministic test fixtures.

Save data must not serialize transient pointers, presentation state, caches, or undocumented engine internals as canonical truth.

Acceptance includes create/load, repeated save, interrupted write, missing data, extra/unknown data, version migration, corruption, concurrent or duplicate request behavior, and post-load invariants.

