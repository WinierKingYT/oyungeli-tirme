# AI Governance

## Permission levels

| Level | Purpose | Production writes |
|---|---|---|
| L1 Research | Inspect and report reality | No |
| L2 Design | Create proposals and documentation | No |
| L3 Implementation | Execute one approved task | Lease-scoped only |
| L4 Acceptance | Independently judge evidence | No |

An agent may hold one role for a task. The implementer cannot become its acceptance reviewer.

## Confidence gate

Before implementation report `HIGH`, `MEDIUM`, or `LOW` for requirements, repository understanding, architecture, engine behavior, networking, persistence, and validation environment. Any material `LOW` produces `SPIKE_REQUIRED` or `BLOCKED`.

## Assumption register

Agents must not convert an assumption into production truth. Each material assumption has an owner, validation method, deadline/exit condition, and impact if false.

## Scope sentry

Any needed change outside task scope becomes a separate dependency task. The current task stops; it does not absorb the expansion.

