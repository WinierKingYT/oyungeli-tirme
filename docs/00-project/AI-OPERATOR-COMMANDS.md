# AI Operator Commands

These are short user prompts because the detailed procedure already lives in skills and project authority.

## First session in the real repository

Run outside Claude first:

```bash
python scripts/doctor.py --require-claude
```

Do not continue if this reports `FAIL`.

> `/project-discovery` — Inspect the repository and prepare the discovery report. Documentation only. Do not modify production code or assets.

## Start a new system

> `/new-system cargo` — Use current repository reality and accepted authority. Produce a proposed system specification, risk/rigor classification, acceptance criteria, and test plan. Do not implement.

## Ask for readiness review

> Use the `gameplay-architect` output as input and invoke `/ready-review SYS-CARGO-001`. The reviewer must be independent, may not repair the proposal, and must create a separate receipt bound to the final task SHA-256.

## Prepare an implementation task

> Create one bounded task contract from the accepted system spec. Include exact allowed paths, allowed commands, expected diff, stop conditions, rollback, and evidence plan. Keep status `DRAFT` until independent review.

## Activate implementation

Do not ask Claude to do this. Review the contract yourself, then run outside Claude:

```bash
python scripts/activate_lease.py docs/05-production/tasks/TASK-CARGO-001.md
```

Then tell Claude:

> `/implement-system TASK-CARGO-001` — Verify the active lease and implement only the approved scope. Stop on drift or expansion. Do not self-accept.

The repository must be clean before activation. The lease is bound to the current Git HEAD and branch; switching either invalidates it.

## Seal implementation

When implementation and task-scoped tests are complete, run outside Claude:

```bash
python scripts/seal_implementation.py
```

This records the exact diff digest, rejects changed paths outside the lease, and closes further agent writes. Give the seal to verification and acceptance reviewers.

## Verify

> `/verify-system TASK-CARGO-001` — Build the evidence pack at the exact revision. Separate pre-existing failures and do not claim final acceptance.

## Independent acceptance

> Invoke `acceptance-reviewer` for TASK-CARGO-001. Read-only review. Return only ACCEPT, FIX_FIRST, or BLOCKED. Create a separate acceptance receipt bound to the exact implementation revision, implementation seal/diff hashes, and evidence-pack SHA-256.

## Close

> `/close-system SYS-CARGO-001` — Close only if independent acceptance, evidence, docs, P0/P1 zero, and canonical revision are complete.

## When something looks wrong

> `/drift-audit` — Compare repository, docs, lifecycle, and evidence. Do not repair during audit.

## Milestone gate

> `/milestone-review G4-VERTICAL-SLICE` — Evaluate only against evidence-driven exit and abort criteria.
