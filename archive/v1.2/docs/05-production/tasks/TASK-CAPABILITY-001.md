---
task_id: TASK-CAPABILITY-001
status: READY_FOR_IMPLEMENTATION
authored_by: Claude Sonnet 5 (drafting agent, this session)
approved_by: Claude Sonnet 5 (independent code-reviewer agent, fresh context per review round)
ready_review_receipt: docs/05-production/tasks/READY-TASK-CAPABILITY-001.md
rigor: R1
approval_mode: hash
system_id: SYS-V2-SCHEMAS-001
allowed_paths:
  - schemas/v2/capability-registry.schema.json
  - schemas/v2/fixtures/capability-valid-example.json
  - schemas/v2/fixtures/capability-invalid-missing-required.json
  - schemas/v2/fixtures/capability-invalid-wildcard-path.json
  - schemas/v2/fixtures/capability-invalid-unknown-field.json
allowed_commands:
  - git diff *
---

# Task Contract — TASK-CAPABILITY-001

## Problem and outcome

`schemas/v2/task-contract.schema.json` (from `TASK-SCHEMA-001`, `READY_FOR_IMPLEMENTATION` with an `ACTIVE`/unsealed lease — see Authority inputs below, not yet `IMPLEMENTED`) already has an `allowed_capabilities` field, but it accepts free-form strings with a description explicitly marking it "reserved for the future capability taxonomy... until that schema exists" (`schemas/v2/task-contract.schema.json:111-116`). [ADR-001](../../04-decisions/ADR-001-v2-product-and-threat-specification.md) names "capability-based (not exact-name) MCP mediation" as a benefit of the V2.0 direction (Options table, line 25) but does not itself define a capability taxonomy. Outcome: one new JSON Schema (`schemas/v2/capability-registry.schema.json`) defining the shape of a **capability registry entry** — a named, versioned, closed-vocabulary definition of what a capability authorizes (path patterns, command patterns, network policy, minimum rigor tier, whether it requires human approval) — plus fixtures proving it validates correctly and rejects known-bad shapes. This does not modify `task-contract.schema.json`'s existing free-form `allowed_capabilities` field; wiring the two together is separate, future work, out of scope here.

## Authority inputs

[ADR-001](../../04-decisions/ADR-001-v2-product-and-threat-specification.md) (`ACCEPTED`), [SYS-V2-SCHEMAS-001](../../03-systems/SYS-V2-SCHEMAS-001.md) (`SPECIFIED`, independently reviewed `READY_FOR_IMPLEMENTATION` for task-level work under it), `schemas/v2/task-contract.schema.json` (existing sibling artifact from `TASK-SCHEMA-001`, read for consistency of field-naming conventions, not modified).

**Reconciliation carried forward from `TASK-SCHEMA-001` (`ASSUMPTION_REQUIRES_APPROVAL`, not re-litigated, only re-disclosed per system-level note in `SYS-V2-SCHEMAS-001.md`'s Independent review record):** `ADR-001`'s Consequences section states DEBT-001/RISK-006 and two open spikes block "the next phase (V2-02, contracts/schemas)" from starting cleanly. `SYS-V2-SCHEMAS-001`'s own disclosed position is that this blocks **R2-and-above** execution/sandbox-dependent work at full strength, and applies more narrowly to **R1** static-artifact tasks under this system (evidence-gathering friction, not an unsafe pass-through) — provided every such task still runs `doctor.py --require-claude` and records its actual output. This task is R1, non-executable, and does so below. **This system-level position remains subject to revision by whichever independent reviewer evaluates this specific task — it is not treated as a blanket waiver just because it worked for `TASK-SCHEMA-001`.**

`python scripts/doctor.py --require-claude` re-run for this task's own record, 2026-09-17: result was `RESULT: FAIL` / `"mechanical validator failed"` — **not** DEBT-001's non-ASCII-path error (that check passed silently this run, confirming the `PYTHONUTF8=1` fix from `docs/05-production/HANDOFF-001-session-continuity.md` items 13–14 still holds on this machine). Root cause traced by reading `scripts/doctor.py:102-110`: it internally re-runs `scripts/validate_os.py` and fails if that fails; `validate_os.py` itself currently reports exactly one failure, `"deliverable must not contain an active implementation lease"`, because `TASK-SCHEMA-001`'s lease is still genuinely `ACTIVE` (unsealed) at drafting time — an expected, already-understood, unrelated condition, not a new blocker for this task. Whoever activates this task's eventual lease should re-run `doctor.py --require-claude` fresh rather than trust this note, since by then `TASK-SCHEMA-001` may be sealed and this specific failure gone.

## In scope

- `schemas/v2/capability-registry.schema.json` — one JSON Schema (2020-12) document validating a capability-registry document: a top-level object with a `schema_version` string and a `capabilities` array of capability-entry objects.
- Each capability entry: `capability_id` (pattern `^CAP-[A-Z0-9-]+$`), `name`, `description`, `min_rigor` (closed enum `R0`–`R4`; deliberately **not** named `rigor` — `task-contract.schema.json:49-52`'s `rigor` field means "this task's own declared rigor," while this field means "the minimum rigor tier a referencing task must declare to be allowed to use this capability," a genuinely different property, disclosed here rather than reusing the same name for a different meaning), `requires_human_approval` (boolean), and `mediates` (object: `allowed_path_patterns` array of strings, `allowed_command_patterns` array of strings — named with a `_patterns` suffix, unlike the sibling schema's plain `allowed_paths`/`allowed_commands`, because these entries are always glob-capable match patterns rather than exact paths/commands; `network_policy` enum matching `task-contract.schema.json`'s existing `none`/`local-only`/`remote-allowed` values for consistency).
- Four fixtures: one positive, three negative (missing required field; a path pattern equal to `*`/`**`/`./**`, mirroring `task-contract.schema.json`'s own edge case; an unknown top-level or nested field).

`ASSUMPTION_REQUIRES_APPROVAL` (first-person, this task's own field names, not inherited from any fuller taxonomy brief — flagged explicitly per `AGENTS.md`'s Uncertainty Protocol rather than left implicit by analogy to a sibling document): `capability_id`, `min_rigor`, `mediates`, `requires_human_approval`, `allowed_path_patterns`, `allowed_command_patterns` are this task's own design choices. None are sourced from a fuller capability-taxonomy brief (none exists in this repository beyond `ADR-001`'s one-line mention) and none have been independently reviewed for naming conventions before this contract's own READY review.

## Explicit non-scope

No controller code, no capability-based MCP mediation logic, no change to `task-contract.schema.json`'s existing `allowed_capabilities` field or its description, no change to any `CONTROLLED_PATHS` file, no actual populated capability registry for this repository (this task defines the shape only, not a filled-in taxonomy of this project's real capabilities — that is separate future work once this schema exists and is accepted), no state-transition/evidence-manifest/seal-attestation/review-acceptance-receipt schemas (separate future tasks under this same system).

## Repository reality and relevant existing capability

Confirmed via Glob: `schemas/v2/` currently contains exactly `task-contract.schema.json` and its 4 fixtures (from `TASK-SCHEMA-001`, `READY_FOR_IMPLEMENTATION`, lease `ACTIVE`/unsealed — not yet `IMPLEMENTED`). No capability-registry schema or fixture exists yet. `task-contract.schema.json`'s `allowed_capabilities` property (lines 111-116) is the direct precedent for field-naming and the closest existing artifact, cross-checked against `ADR-001`'s one-line mention of capability-based mediation as the only other source — there is no fuller capability taxonomy brief text available in this repository, so field choices here are this task's own design work, same as `TASK-SCHEMA-001`'s field-naming was flagged `ASSUMPTION_REQUIRES_APPROVAL` for the same reason.

## Expected diff

| Kind | Expected |
|---|---|
| New files | `schemas/v2/capability-registry.schema.json`, `schemas/v2/fixtures/capability-valid-example.json`, `schemas/v2/fixtures/capability-invalid-missing-required.json`, `schemas/v2/fixtures/capability-invalid-wildcard-path.json`, `schemas/v2/fixtures/capability-invalid-unknown-field.json` |
| Modified files | None |
| Removed files | 0 |
| Dependencies | None added to the repository; verification uses any external/ephemeral JSON Schema 2020-12 validator, same as `TASK-SCHEMA-001` |
| Schema/public contract | New — a second, independent schema artifact under `schemas/v2/`; does not alter `task-contract.schema.json`'s existing public shape |

## Blast radius and reversibility

Blast radius: one new schema file plus four new fixture files (one positive, three negative), all under the already-existing `schemas/v2/` directory tree; zero existing files modified. Reversibility: EASY — delete the five new files; nothing yet references them (this system has no consuming controller implementation, per `ADR-001`'s explicit non-authorization of v2.0 implementation).

## Acceptance criteria

| ID | Criterion | Verification | Required evidence |
|---|---|---|---|
| AC-01 | Schema file is valid JSON Schema (2020-12 meta-schema) | Validate the schema file against the JSON Schema meta-schema | Validator output, exit code 0 |
| AC-02 | Schema validates the positive fixture | Run validator: schema + `capability-valid-example.json` | Validator output showing PASS |
| AC-03 | Schema rejects all three negative fixtures with the expected error class each | Run validator against each `capability-invalid-*.json` | Validator output showing FAIL for each, with the violated constraint named |
| AC-04 | No `CONTROLLED_PATHS` file appears in the diff | `git diff --name-only` against `allowed_paths` | Diff output |
| AC-05 | No change to `task-contract.schema.json` or its existing fixtures | `git diff --name-only` shows none of the 5 pre-existing `schemas/v2/` files from `TASK-SCHEMA-001` | Diff output |

## Test and runtime plan

Manual validation using any standard-conformant JSON Schema 2020-12 validator, run externally to this repository (no new dependency added — see Expected diff). No runtime/multiplayer/persistence surface applies — static document task, same class as `TASK-SCHEMA-001`.

## Stop conditions

- Scope expansion beyond the single schema file and its fixtures (in particular: do not start wiring this schema into `task-contract.schema.json`'s `allowed_capabilities` field — that is separate future work).
- Documentation/code drift invalidates this contract (e.g. `ADR-001` or `SYS-V2-SCHEMAS-001` is revised before this task completes).
- Material confidence becomes LOW on any required field's meaning.
- A required dependency/schema/public-interface change beyond `schemas/v2/capability-registry.schema.json` is discovered.
- Lease is absent, expired, or invalid.
- **Do not activate this task's lease while any other task's `.ai-governance/implementation-lease.json` is present and its `state` is `ACTIVE`, unless that other task is already sealed or its lease has been explicitly deactivated first.** `scripts/activate_lease.py` has no guard against overwriting an active lease file — it writes unconditionally — so this is a real, human-enforced precondition, not a cosmetic one. At drafting time, `TASK-SCHEMA-001`'s lease is exactly in this state (`ACTIVE`, unsealed); do not activate `TASK-CAPABILITY-001` until that is resolved.
- `doctor.py --require-claude` returns the DEBT-001 false-positive `FAIL` on the activating machine and the human has not confirmed the `PYTHONUTF8=1` workaround (or the code fix) is in place there — do not assume the workaround transfers machine-to-machine.

## Rollback

Delete the 5 new files listed under Expected diff. No other file depends on them yet.

## Independent ready review

The independent reviewer creates a separate immutable receipt from `READY-REVIEW-RECEIPT-TEMPLATE.md`, bound to this contract's final SHA-256. `approval_mode: hash` applies (R1, not R4).

**Reviewer-independence note (disclosed, same limitation as `TASK-SCHEMA-001`, per `PACKAGE-REPORT.md`):** the reviewer is a separate Agent-tool dispatch, fresh context, no access to this drafting session's reasoning, but runs on the same underlying model family as the author. Final lease activation remains human-only regardless of this receipt's disposition.
