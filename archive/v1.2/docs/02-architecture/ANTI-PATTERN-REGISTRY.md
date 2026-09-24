# Known Bad Patterns Registry

| ID | Pattern | Detection signal | Required response |
|---|---|---|---|
| AP-001 | Global God Manager | unrelated state and orchestration accumulate in one owner | split by canonical responsibility |
| AP-002 | Duplicated canonical state | two mutable truths require synchronization | choose one owner; derive the other |
| AP-003 | Gameplay logic in UI | widget mutation changes domain outcome | move logic behind domain contract |
| AP-004 | Unbounded Tick | cost grows with actors/content every frame | event, timer, batching, or budget |
| AP-005 | Direct subsystem cross-coupling | hidden calls bypass public contract | accepted interface/event |
| AP-006 | Speculative abstraction | no current second use or pain | remove until demonstrated |
| AP-007 | Magic gameplay constants | tuning value embedded in behavior | accepted configuration authority |
| AP-008 | Silent fallback | invalid state becomes plausible behavior | fail visibly and observably |
| AP-009 | Boolean lifecycle soup | combinations encode undocumented states | explicit state machine |
| AP-010 | Test-shaped implementation | passes narrow tests but violates system contract | review behavior and architecture |
| AP-011 | Reviewer repair | reviewer edits code while judging it | return finding to implementer |
| AP-012 | Evidence by assertion | report claims a run without artifact/log | mark evidence missing |

