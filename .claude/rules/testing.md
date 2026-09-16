# Testing and evidence rules

- Map every acceptance criterion to at least one verification method.
- Distinguish unit, integration, runtime, end-to-end, playtest, performance, soak, and manual inspection evidence.
- Record command, environment, build/commit, timestamp, outcome, and artifact path.
- Test unhappy paths, partial failure, recovery, order variation, boundaries, and invalid configuration.
- Multiplayer systems require host/client authority, latency, packet loss, join/leave, reconnect, and state-drift coverage.
- Persistent systems require save/load, version mismatch, corruption, interrupted write, and migration coverage.
- Random systems record seeds and relevant state.
- Never weaken an assertion or delete a failing test merely to achieve green status.
- A flaky test is a defect, not a pass.

