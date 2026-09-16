# System Lifecycle

| State | Meaning | Entry requirement | Exit authority |
|---|---|---|---|
| DISCOVERY | Reality and problem are being investigated | Bounded question | Research review |
| SPECIFIED | Proposed contract exists | Discovery evidence | Ready reviewer |
| READY_REVIEW | Spec and task await independent gate | Complete readiness package | Independent reviewer |
| READY_FOR_IMPLEMENTATION | Bounded, testable task approved | `READY` record | Human lease activation |
| IMPLEMENTED | Approved diff exists and human seal closes write authority | Implementation report + repository-bound seal | Verification |
| VERIFIED | Applicable checks have evidence | Evidence pack | Acceptance reviewer |
| INDEPENDENT_REVIEW | Separate authority evaluates | Complete pack | Acceptance reviewer |
| ACCEPTED | All required claims supported | `ACCEPT`, P0/P1 zero | Project authority |
| FROZEN | Accepted baseline protected | Freeze record/revision | Change control |

Rejected or paused work uses `FIX_FIRST`, `BLOCKED`, `CANCELED`, or `SUPERSEDED`; these are dispositions, not success states.
