---
task_id: TASK-SCHEMA-001
status: READY_FOR_IMPLEMENTATION
authored_by: Claude Sonnet 5 (drafting agent, this session)
approved_by: Claude Sonnet 5 (independent code-reviewer agent, fresh context per review round)
ready_review_receipt: docs/05-production/tasks/READY-TASK-SCHEMA-001.md
rigor: R1
approval_mode: hash
system_id: SYS-V2-SCHEMAS-001
allowed_paths:
  - schemas/v2/task-contract.schema.json
  - schemas/v2/fixtures/valid-example.json
  - schemas/v2/fixtures/invalid-missing-required.json
  - schemas/v2/fixtures/invalid-wildcard-path.json
  - schemas/v2/fixtures/invalid-unknown-field.json
allowed_commands:
  - git diff *
---

# Task Contract — TASK-SCHEMA-001

## Problem and outcome

v1.2 has no machine-readable schema for its task-contract shape; validation lives as scattered Python checks in `scripts/activate_lease.py` (a `CONTROLLED_PATH` this task never touches). [ADR-001](../../04-decisions/ADR-001-v2-product-and-threat-specification.md) accepted moving toward schema-driven contracts for V2.0. Outcome: one new JSON Schema file (`schemas/v2/task-contract.schema.json`) formalizing the field list from the accepted V2.0 spec, plus a small set of fixture files proving it validates correctly and rejects known-bad shapes.

## Authority inputs

[ADR-001](../../04-decisions/ADR-001-v2-product-and-threat-specification.md) (`ACCEPTED`), [SYS-V2-SCHEMAS-001](../../03-systems/SYS-V2-SCHEMAS-001.md) (`SPECIFIED`, pending its own independent READY review before this task may be leased), `docs/templates/TASK-CONTRACT-TEMPLATE.md` (existing field shape to formalize).

**AUTHORITY_CONFLICT reconciliation (raised by independent task-level review F1, revised after independent system-level review F2 found the first version factually wrong):** ADR-001's Consequences section states "the next phase (V2-02, contracts/schemas)" is blocked pending `DEBT-001`/`RISK-006` and the two open sandbox/usability spikes. An earlier draft of this paragraph claimed DEBT-001/RISK-006 have "no bearing" on this task — that claim was independently reviewed and rejected: `DEBT-001`'s own remediation trigger explicitly names "a real R1+ task on a non-ASCII path" (`docs/05-production/TECH-DEBT.md`), and this repository's actual path (`oyungeliştirme`) **is** non-ASCII, so the bug directly applies here, not hypothetically.

`ASSUMPTION_REQUIRES_APPROVAL` (per `AGENTS.md`'s Uncertainty Protocol — this is disclosed as unresolved, not asserted as settled; a prior draft of this paragraph incorrectly presented it as "the corrected position," which a second independent review correctly rejected as self-waiving a documented trigger): DEBT-001 was confirmed, by directly re-running `python scripts/doctor.py --require-claude` on 2026-09-16, to be a fail-**closed** false positive — `RESULT: FAIL` / `"package must be installed at the Git repository root"` — even though the repository is in fact correctly installed at its Git root (verified separately via `git rev-parse --show-toplevel` matching the project root). `docs/05-production/TECH-DEBT.md`'s own remediation trigger for DEBT-001 is "Fix before strict preflight is relied on for a real R1+ task on a non-ASCII path" — this task **is** that exact trigger condition (R1, this repository's non-ASCII path, and it does rely on `doctor.py --require-claude` at lease-activation time). This task contract does **not** have the authority to waive that trigger itself — `scripts/doctor.py` is a `CONTROLLED_PATHS` file no agent, lease or not, can ever modify, so this cannot be resolved by adding more agent work.

**This is therefore an explicit, named human decision blocking lease activation, not a documentation gap:** before running `scripts/activate_lease.py` for this task, the human operator must choose one of:
1. Fix `DEBT-001` directly (human-edited, since no agent can touch `scripts/doctor.py`), then re-run `doctor.py --require-claude` and confirm `RESULT: PASS`; or
2. Explicitly waive the DEBT-001 trigger for this specific task — accepting the known false-positive `FAIL` as expected and non-blocking — and record that waiver decision in this task's READY-review receipt or as a dated note added directly to this file before typing `ACTIVATE`.

Neither this task contract nor its independent reviewer may make that waiver on the human operator's behalf.

**Waiver recorded, 2026-09-16:** the project owner explicitly chose to waive the DEBT-001 trigger for this task rather than fix it first, having been told the waiver is not mechanically required by `scripts/activate_lease.py` (confirmed by inspection: `activate_lease.py` does not invoke `doctor.py`) but is a recorded due-diligence decision per this contract's own Stop Conditions. DEBT-001/RISK-006 remain open in the backlog for future remediation; this waiver applies only to `TASK-SCHEMA-001` and does not close either entry. The open sandbox spike (`SPIKE-SANDBOX-001`) concerns mandatory OS-level isolation for rigor tier **R2 and above** (ADR-001, D4); this task is **R1**, requires no sandboxed execution, and D4 does not apply to it — this part of the reconciliation was not disputed by either independent review.

## In scope

- `schemas/v2/task-contract.schema.json` — one JSON Schema (2020-12) document.
- `schemas/v2/fixtures/valid-example.json` — one positive fixture.
- `schemas/v2/fixtures/invalid-*.json` — at least three negative fixtures (missing required field; wildcard `allowed_paths`; unknown extra field).

## Explicit non-scope

No controller code. No changes to any `CONTROLLED_PATHS` file (`.ai-governance/**`, `.claude/hooks/**`, `.claude/settings.json`, any `scripts/*.py` listed in `common.py:16-30`, `tests/governance_attack_corpus.json`, `.github/workflows/aigdo-validation.yml`). No change to v1.2's actual Markdown-frontmatter task-contract mechanism — this schema is a separate, additive artifact, not a replacement. No capability/state-transition/evidence-manifest/seal/receipt schemas (separate future tasks under SYS-V2-SCHEMAS-001).

## Repository reality and relevant existing capability

Confirmed via Glob: zero `*.schema.json` files exist anywhere in this repository before this task. `docs/templates/TASK-CONTRACT-TEMPLATE.md`'s frontmatter block is the closest existing artifact and is the direct source for this schema's field list, cross-checked against the brief §6.2 field list already accepted in ADR-001.

## Expected diff

| Kind | Expected |
|---|---|
| New files | `schemas/v2/task-contract.schema.json`, `schemas/v2/fixtures/valid-example.json`, `schemas/v2/fixtures/invalid-missing-required.json`, `schemas/v2/fixtures/invalid-wildcard-path.json`, `schemas/v2/fixtures/invalid-unknown-field.json` |
| Modified files | None |
| Removed files | 0 |
| Dependencies | None added to the repository (no manifest exists; none is introduced). Acceptance verification (AC-01–AC-03) uses any standard-conformant, external/ephemeral JSON Schema 2020-12 validator of the verifier's choice — not committed to or installed into this repository. |
| Schema/public contract | New — this task *is* the introduction of a new schema, tracked as its own artifact under `schemas/v2/`, not a change to any existing public contract |

## Blast radius and reversibility

Blast radius: one new directory (`schemas/v2/`), five new files, zero existing files modified. Reversibility: EASY — delete the new directory; nothing else in the repository references these files yet (this is the first task under a `SPECIFIED`, not-yet-consumed system).

## Acceptance criteria

| ID | Criterion | Verification | Required evidence |
|---|---|---|---|
| AC-01 | Schema file is valid JSON Schema (2020-12 meta-schema) | Validate the schema file against the JSON Schema meta-schema | Validator output, exit code 0 |
| AC-02 | Schema validates the positive fixture | Run validator: schema + `valid-example.json` | Validator output showing PASS |
| AC-03 | Schema rejects all three negative fixtures with the expected error class each | Run validator against each `invalid-*.json` | Validator output showing FAIL for each, with the violated constraint named |
| AC-04 | No `CONTROLLED_PATHS` file appears in the diff | `git diff --name-only` against `allowed_paths` | Diff output |

## Test and runtime plan

Manual validation using any standard-conformant JSON Schema 2020-12 validator, run externally to this repository (no new dependency is added to the repository itself — see Expected diff). No runtime/multiplayer/persistence surface applies — this is a static document task.

## Stop conditions

- Scope expansion beyond the single schema file and its fixtures.
- Documentation/code drift invalidates this contract (e.g. ADR-001 is revised before this task completes).
- Material confidence becomes LOW on any required field's meaning.
- A required dependency/schema/public-interface change beyond `schemas/v2/task-contract.schema.json` is discovered.
- Lease is absent, expired, or invalid.
- DEBT-001's fix-or-waiver decision (see Authority inputs above) has not been made and recorded by the human operator before lease activation.

## Rollback

Delete `schemas/v2/` entirely. No other file depends on it yet (system is `SPECIFIED`, not consumed by any accepted implementation).

## Independent ready review

The independent reviewer creates a separate immutable receipt from `READY-REVIEW-RECEIPT-TEMPLATE.md`, bound to this contract's final SHA-256. `approval_mode: hash` applies (R1, not R4).

**Reviewer-independence note (disclosed, matching this project's own documented limitation, `PACKAGE-REPORT.md`: "R0–R3 reviewer names are not cryptographic identities"):** the reviewer for this task is a separate Agent-tool dispatch (fresh context, no access to this drafting session's reasoning, independently re-reading the repository) but runs on the same underlying model family as the author. This is disclosed, not concealed, and is why final lease activation remains a human-only act regardless of this receipt's disposition.
