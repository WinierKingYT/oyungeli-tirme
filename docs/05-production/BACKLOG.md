# Backlog

| Priority | ID | Item | Type | Dependency | Exit condition |
|---:|---|---|---|---|---|
| P0 | DISCOVERY-001 | Inspect the real project repository | Research | G0 | Discovery report independently reviewed |
| P0 | OWNER-INPUT-001 | Owner supplies game documents (`docs/01-design/inputs/`) and answers: Unity version, render pipeline, 2D or 3D, single or multiplayer | Input | None | Documents present; answers recorded |
| P1 | GOV-001 | Ratify project constitution | Governance | DISCOVERY-001 | Human approval recorded |
| P1 | GOV-002 | Accept or reject `ADR-002` (prototype lane, owner-delegated execution) | Governance | None | Owner decision recorded in `ADR-INDEX.md` |
| P1 | GOV-003 | Record the G0 exit-criterion exception: `doctor.py`/`validate_os.py` pass only in a clean copy until `DEBT-006` is fixed | Governance | DEBT-006 | Owner-accepted note in `CURRENT-MILESTONE.md` |
| P1 | ADR-003 | Unity version, render pipeline, project layout | ADR | OWNER-INPUT-001 | Accepted ADR |
| P1 | UNITY-SETUP-001 | Create the Unity project at the repository root using `UNITY-REPO-HYGIENE.md` | Task | ADR-003, `unity.md` accepted | Independent acceptance receipt |
| P1 | PROTO-LANE-001 | Draft and review `TASK-PROTO-LANE-001` per `PROTOTYPE-LANE.md` | Task | GOV-002, UNITY-SETUP-001 | Contract `READY_FOR_IMPLEMENTATION` |
| P1 | DEBT-FIX-001 | Prepare, review, and apply the human-only fix bundle for `DEBT-002`, `DEBT-003`, `DEBT-006` | Bug fix | None | Owner applies patches; validators pass. Status 2026-09-19: proposal revision 3 in `docs/05-production/proposals/DEBT-FIX-001/`, two independent static reviews `READY` for the owner's dry run; not applied, nothing executed |
| P2 | DEBT-005 | Retarget Unreal-shaped rules and docs for Unity | Cleanup | UNITY-SETUP-001 | `TECH-DEBT.md` entry closed |
| P1 | ARCH-001 | Build system and ownership map | Architecture | DISCOVERY-001 | Accepted map and unknowns closed |
| P1 | DESIGN-001 | Validate core-loop hypotheses | Design/playtest | Discovery | Hypothesis decisions linked to evidence |
| P2 | SPIKE-SANDBOX-001 | Confirm Windows Sandbox works end-to-end on the target machine (edition/virtualization check + hand-tested launch/script/teardown cycle) | Spike | ADR-001 (D4) | Hands-on test recorded; D4 mechanism selection finalized |
| P2 | DEBT-001 | Fix `doctor.py --require-claude` non-ASCII path comparison bug | Bug fix | None | `encoding="utf-8"` added; validated on this repository's own path. Status 2026-09-18: fix applied (`f8ca3bc`), `doctor.py` and `validate_os.py` pass in a clean copy; independent patch review and a live agent-write check under a lease remain open (see `TECH-DEBT.md`) |

