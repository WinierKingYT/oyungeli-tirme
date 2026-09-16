# Test Strategy

## Evidence ladder

1. Static validation: references, schemas, naming, dependency rules.
2. Unit tests: deterministic local rules and state transitions.
3. Integration tests: real boundaries and ownership interactions.
4. Runtime scenarios: engine/editor behavior in representative maps.
5. E2E voyages: whole-game progression and recovery.
6. Multiplayer: authority, latency, loss, join/leave, reconnect, drift.
7. Persistence: save/load, migration, corruption, interrupted write.
8. Performance: target hardware, explicit workload, regression baseline.
9. Soak: long-session leaks, drift, degradation, crashes.
10. Playtest: comprehension, coordination, pacing, and fun hypotheses.

Each system spec selects the applicable layers. Omitted layers require rationale.

