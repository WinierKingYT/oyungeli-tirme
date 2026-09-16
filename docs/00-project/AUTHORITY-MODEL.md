# Authority Model

| Rank | Authority | Can override lower ranks? | Change mechanism |
|---:|---|---|---|
| 1 | Project Constitution | Yes | Constitution amendment + human approval |
| 2 | Accepted ADRs | Yes | Superseding ADR |
| 3 | Accepted/frozen system specs | Yes | Change request + ADR when architectural |
| 4 | Active task contract and repository-bound lease | Only inside approved system scope | Independent ready review + clean-base human lease |
| 5 | Current milestone | No architectural override | Milestone review |
| 6 | GDD and design docs | No technical override | Design change record |
| 7 | Backlog and risk records | No | Routine update |
| 8 | Conversation | No | Must be promoted into an authority artifact |
| 9 | Agent assumption | No | Must be resolved or approved |

Conflicts stop affected work. The correct response is `AUTHORITY_CONFLICT`, not an implicit choice.

## State authority

- Document lifecycle state: `PROJECT-STATUS.md` and indexed evidence.
- Architecture decisions: accepted ADRs.
- System behavior: accepted system specification plus implementation at its recorded revision.
- Current implementation authority: active lease generated from one task contract and bound to exact Git base/branch.
- Release truth: release candidate record plus reproducible artifact and evidence.
