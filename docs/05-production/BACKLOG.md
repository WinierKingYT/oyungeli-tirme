# Backlog

| Priority | ID | Item | Type | Dependency | Exit condition |
|---:|---|---|---|---|---|
| P0 | DISCOVERY-001 | Inspect the real project repository | Research | G0 | Discovery report independently reviewed |
| P1 | GOV-001 | Ratify project constitution | Governance | DISCOVERY-001 | Human approval recorded |
| P1 | ARCH-001 | Build system and ownership map | Architecture | DISCOVERY-001 | Accepted map and unknowns closed |
| P1 | DESIGN-001 | Validate core-loop hypotheses | Design/playtest | Discovery | Hypothesis decisions linked to evidence |
| P2 | SPIKE-SANDBOX-001 | Confirm Windows Sandbox works end-to-end on the target machine (edition/virtualization check + hand-tested launch/script/teardown cycle) | Spike | ADR-001 (D4) | Hands-on test recorded; D4 mechanism selection finalized |
| P2 | DEBT-001 | Fix `doctor.py --require-claude` non-ASCII path comparison bug | Bug fix | None | `encoding="utf-8"` added; validated on this repository's own path |

