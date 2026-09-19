# ADR-002 — Owner-delegated execution: fewer human terminal steps without agent self-authority

Status: `PROPOSED`

Date: 2026-09-18

## Context and forces

Facts observed on 2026-09-18 while taking `TASK-UNITY-RULES-001` (one 21-line file) from contract to `ACCEPTED`:

- The human had to run lease activation, the seal, the commits, three validator runs, and a clock command, each in their own terminal. Progress stopped whenever they were away.
- Hooks fail closed: `git add`, `git commit`, `date`, and every other non-read-only shell command returned `LEASE_REQUIRED` for the agent when no lease was active.
- `CLAUDE.md` and `AGENTS.md` forbid an agent from invoking `activate_lease.py`, `deactivate_lease.py`, and `seal_implementation.py`. ADR-001 PR1 states that no agent self-grants authority.
- The project owner asked on 2026-09-18 that lease, seal, and commit steps no longer need their approval or their commands, and that commits carry only the owner's identity. A conversation instruction ranks below accepted records (`AGENTS.md`, authority level 8) and cannot change hooks; hooks and lease scripts are `CONTROLLED_PATHS` that only the owner can edit.

Forces: cycle time for prototypes, the safety property behind PR1, open debts `DEBT-002`, `DEBT-003`, `DEBT-006`, and the still open key-custody question (ADR-001 D8).

## Decision drivers

1. Authority must originate from the owner, never from an agent's own action (PR1).
2. Routine low-risk work must not depend on the owner being at a terminal.
3. Every grant must be bounded in paths, time, and rigor, revocable, and auditable.
4. The owner must be able to keep the project without lock-in (PR7).

## Options considered

| Option | Benefits | Costs/risks | Migration | Reversibility |
|---|---|---|---|---|
| A. Status quo: owner runs every lease, seal, and commit | Strongest guarantee, no code change | Owner is the bottleneck; work stalls when they are away | None | Not applicable |
| B. Owner pre-signs a standing policy; agents may activate, seal, and commit only inside a valid, unexpired, signed policy | Authority still comes from the owner's signature (PR1 holds); removes routine terminal steps; reuses the existing SSH-signature mechanism (`verify_approval_signature.py`) | Needs new non-interactive code in controlled scripts and hooks; key custody unresolved (D8); a bug here weakens the core control | Owner applies patches to `CONTROLLED_PATHS` files once | Moderate: remove the policy file and revert patches |
| C. Loosen hooks so agents run the scripts directly and drop typed confirmations | Fastest | Violates PR1; an agent could grant itself authority; no audit meaning | Edit hooks | Easy to revert, hard to trust afterwards |
| D. Prototype lane: a long-lived lease bound to a narrow prototype path (for example `Assets/_Prototype/**`), no spec or acceptance receipt, promotion to production paths through the normal process | Cheap; keeps fail-closed behavior; fits ADR-001's D10 fallback; the owner still activates once per session | The owner still starts each session; the lane rules need writing | New rule text and a task template | Easy |
| E. Exempt the prototype path from lease checks entirely | No ceremony in that folder | Removes fail-closed protection there; edits a controlled file | Edit `common.py` path lists | Easy, weaker safety |

## Decision

`PROPOSED`, not accepted until the owner accepts it:

- Adopt D as the near-term change: write the prototype-lane rules and a task template, with the owner activating a session lease.
- Design B as the target for removing routine steps, as a separate R4 task that includes a key-custody decision and its own independent review. Until B exists and is accepted, agents keep asking the owner for lease, seal, and commit steps.
- Reject C. Consider E only if the owner explicitly accepts the weaker safety in writing.

## Owner input (2026-09-19)

The owner asked that lease, seal, and commit steps no longer need their terminal, and chose: lanes for prototype, production Unity code, and rule/settings files; R2 as the highest rigor approved without them; a passphrase-protected SSH key; and an indefinite policy. This selects option B as the target and adds it to the near-term work. The detailed design is `docs/05-production/proposals/OWNER-POLICY-001/DESIGN.md`. Two choices carry flagged risk: R2 conflicts with ADR-001 D4 until the sandbox spike is accepted (the verifier caps at R1 until then), and an indefinite policy needs revocation and audit. This ADR stays `PROPOSED` until the owner accepts the reviewed design.

## Consequences

- Stays human-only in every option: editing `CONTROLLED_PATHS`, key custody, revoking a policy, and push, merge, tag, or history rewrite.
- Under B, commits stay local, carry only the owner's identity (see `docs/05-production/BRANCH-DISCIPLINE.md`), and are limited to paths covered by the active policy.
- Open questions: how hooks tell a policy-covered activation from an uncovered one; policy revocation; audit log content; whether sealing may be automated or only activation; how the policy names its maximum rigor.
- Debts `DEBT-002`, `DEBT-003`, and `DEBT-006` should be fixed before B, because B would multiply their effect.

## Validation and revisit trigger

- Measure cycle time from contract to sealed for a prototype task under D and compare it with the `TASK-UNITY-RULES-001` baseline in this repository; the owner sets the acceptance threshold.
- Revisit this ADR if D does not reduce owner terminal steps, if the key-custody spike finds no workable option, or if repository discovery changes the engine or platform assumptions.

## Supersedes / superseded by

Supersedes nothing. Builds on ADR-001 (PR1, PR6, PR7, D8, D10); it does not change ADR-001.
