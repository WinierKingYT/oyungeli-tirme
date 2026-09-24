---
task_id: TASK-STATE-TRANSITION-001
status: SPECIFIED
authored_by: Claude Sonnet 5 (drafting agent, this session)
approved_by: UNSET
ready_review_receipt: UNSET
rigor: R1
approval_mode: hash
system_id: SYS-V2-SCHEMAS-001
allowed_paths:
  - schemas/v2/state-transition.schema.json
  - schemas/v2/fixtures/state-transition-valid-example.json
  - schemas/v2/fixtures/state-transition-invalid-missing-required.json
  - schemas/v2/fixtures/state-transition-invalid-bad-state.json
  - schemas/v2/fixtures/state-transition-invalid-unknown-field.json
allowed_commands:
  - git diff *
---

# Task Contract — TASK-STATE-TRANSITION-001

## Problem and outcome

[ADR-001](../../04-decisions/ADR-001-v2-product-and-threat-specification.md)'s decision drivers include PR3: "every state transition auditable." Today, a task's or system's lifecycle state lives only as a single mutable `status:`/`Status:` field in that document's own frontmatter/heading (e.g. `docs/05-production/tasks/TASK-SCHEMA-001.md:3`) — the *history* of how it got there (which state it moved from, when, on whose authority, backed by which evidence) is not itself a structured, machine-checkable record anywhere in this repository. `.ai-governance/audit.log` (confirmed by direct read) only logs tool-permission decisions (`allow`/`deny` for Bash/Write/MCP calls) — a different concern, not a lifecycle-state audit trail. Outcome: one new JSON Schema (`schemas/v2/state-transition.schema.json`) defining the shape of a single **state-transition record** — one entity's move from one `docs/08-process/SYSTEM-LIFECYCLE.md` state to another, with who/what authorized it and what evidence backs it — plus fixtures. This does not build a transition *log/ledger* mechanism, a controller, or any code that writes these records automatically; it defines the record shape only, so that future work (out of scope here) can start emitting/consuming them.

## Authority inputs

[ADR-001](../../04-decisions/ADR-001-v2-product-and-threat-specification.md) (`ACCEPTED`, PR3 "every state transition auditable" is the direct driver), [SYS-V2-SCHEMAS-001](../../03-systems/SYS-V2-SCHEMAS-001.md) (`SPECIFIED`, independently reviewed `READY_FOR_IMPLEMENTATION` for task-level work under it, names "state-transition schema" explicitly in its own deferred non-scope list), `docs/08-process/SYSTEM-LIFECYCLE.md` (the canonical lifecycle vocabulary: 9 states plus the 4 disposition labels, 13 values in all), `schemas/v2/task-contract.schema.json` (sibling artifact whose `status` enum — those 13 values plus the disclosed task-instance-level extension `DRAFT`, 14 in all — this schema copies; the copy is a disclosed duplication, not an avoidance of one, see In scope and Known limitation).

**Reconciliation carried forward from `TASK-SCHEMA-001`/`TASK-CAPABILITY-001` (`ASSUMPTION_REQUIRES_APPROVAL`, not re-litigated, only re-disclosed per system-level note in `SYS-V2-SCHEMAS-001.md`'s Independent review record):** `ADR-001`'s Consequences section states DEBT-001/RISK-006 and two open spikes block "the next phase (V2-02, contracts/schemas)" from starting cleanly. `SYS-V2-SCHEMAS-001`'s own disclosed position is that this blocks **R2-and-above** execution/sandbox-dependent work at full strength, and applies more narrowly to **R1** static-artifact tasks under this system. This task is R1, non-executable. **This system-level position remains subject to revision by whichever independent reviewer evaluates this specific task.**

`python scripts/doctor.py --require-claude` status at drafting time, 2026-09-18: not re-run for this specific task's own record — the last known result (`TASK-CAPABILITY-001.md`'s own Authority inputs section) was `RESULT: FAIL` / `"mechanical validator failed"`, cascading from `validate_os.py`'s check that no lease file exists (`scripts/validate_os.py:115` tests only for the file's presence, not its expiry) while `TASK-SCHEMA-001`'s lease file was still on disk — not DEBT-001's own non-ASCII-path check, which continued to pass silently. Since then (observed directly, same day, by Glob of `.ai-governance/*`), that lease file has been removed by the human (no `implementation-lease.json` exists at time of writing), so the cascading cause may already be gone. Whoever activates this task's eventual lease must re-run `doctor.py --require-claude` fresh rather than trust this note.

## In scope

- `schemas/v2/state-transition.schema.json` — one JSON Schema (2020-12) document validating a single state-transition record: `entity_type` (closed enum: `task`, `system`, `adr`), `entity_id` (string, pattern `^(TASK|SYS|ADR)-[A-Z0-9-]+$`), `from_state` and `to_state` (both the **exact same enum** already defined at `schemas/v2/task-contract.schema.json:43-47` — `DRAFT`, `DISCOVERY`, `SPECIFIED`, `READY_REVIEW`, `READY_FOR_IMPLEMENTATION`, `IMPLEMENTED`, `VERIFIED`, `INDEPENDENT_REVIEW`, `ACCEPTED`, `FROZEN`, `FIX_FIRST`, `BLOCKED`, `CANCELED`, `SUPERSEDED` — copied verbatim from that file's enum, in the same order, so the two vocabularies start identical; **this is a textual copy, not a `$ref`**: the sibling's enum is inlined on its `status` property rather than extracted into a shared `$defs` node, and extracting it would require editing `task-contract.schema.json`, which is out of scope here. Byte-for-byte identity is therefore verified once at this task's acceptance (AC-06) and is **not** enforced by any schema-level or automated mechanism afterward — see the Known limitation below), `transitioned_at` (string, `date-time` format), `authority` (object: `kind` closed enum `human_decision`/`independent_reviewer`/`project_owner_approval`, `identity` string), `evidence_ref` (string, non-empty — a repository-relative path to the receipt/document backing this transition, e.g. a `READY-TASK-*.md` or `ACCEPTANCE-RECEIPT`).
- **Normative shape (so AC-03's negative fixtures have objective referents):** root object `required` = `entity_type`, `entity_id`, `from_state`, `to_state`, `transitioned_at`, `authority`, `evidence_ref`, all seven mandatory; `additionalProperties: false` at the root and on `authority`; `authority.required` = `kind`, `identity`; `authority.identity` and `evidence_ref` both `minLength: 1`. `format: date-time` is an annotation in JSON Schema 2020-12 unless a validator enables format assertion, so no fixture may rely on it to fail. **Deliberate non-goals, disclosed rather than silent:** the schema does not check that `entity_type` agrees with `entity_id`'s prefix, does not check that `from_state` → `to_state` is a legal move under `SYSTEM-LIFECYCLE.md` (a `DISCOVERY` → `FROZEN` record would validate), and has no representation for an entity's very first state (there is no prior `from_state` to record; creating an entity is not modelled as a transition here). Enforcing any of these is future work.
- Four fixtures: one positive, three negative (missing required field; `from_state`/`to_state` set to a value outside the closed enum, i.e. an invented/misspelled state — this schema's direct equivalent of the sibling schemas' wildcard-path edge case, since the actual security-relevant boundary here is the closed lifecycle vocabulary, not a path pattern; an unknown top-level or nested field).

`ASSUMPTION_REQUIRES_APPROVAL` (first-person, this task's own design choices, not inherited from any fuller brief): `entity_type`'s three-way split (`task`/`system`/`adr`) is this task's own read of what things in this repository actually carry a `SYSTEM-LIFECYCLE.md` state (confirmed via Grep: task contracts and system specs both use these states directly; `ADR-001` uses only `ACCEPTED`/none from the same table, a narrower subset — included anyway since `docs/04-decisions/ADR-INDEX.md`'s own status column uses the identical word `ACCEPTED`). `RISK-*`, `BUG-*`, and `EVID-*` — the other ID families named in `.claude/rules/documentation.md` — were checked and deliberately excluded: `docs/05-production/RISK-REGISTER.md` and `docs/05-production/TECH-DEBT.md` use a `State` column with their own `Open`-style values, and `docs/templates/BUG-TEMPLATE.md` uses `State: NEW`, none of which are `SYSTEM-LIFECYCLE.md` states; no real `BUG-*`/`EVID-*` instances exist yet, only templates. If any of those families later adopts the `SYSTEM-LIFECYCLE.md` vocabulary, `entity_type` will need a follow-up revision. Whether a further entity type (e.g. a milestone) will eventually need this is left `UNKNOWN`, not decided here. `authority.kind`'s three-way enum is drawn from patterns actually observed this session (a human's direct decision on `ADR-001`; an independent-reviewer agent's disposition on `TASK-SCHEMA-001`/`TASK-CAPABILITY-001`; the project owner's own approval per `ADR-001`'s Independent review record) — not from any documented exhaustive list, since none exists.

`ASSUMPTION_REQUIRES_APPROVAL` (`DRAFT` in the state enum): `DRAFT` is **not** defined by `docs/08-process/SYSTEM-LIFECYCLE.md`. It is inherited from `task-contract.schema.json`'s disclosed task-contract-level extension (`docs/templates/TASK-CONTRACT-TEMPLATE.md:3`, `TASK-CARGO-001-DRAFT.md:3`). This schema keeps it valid for **all three** `entity_type` values, including `system` and `adr`, where no document currently uses it — a deliberate simplification (one shared vocabulary rather than per-entity enums), flagged for the reviewer rather than decided silently. Restricting `DRAFT` to `entity_type: task` would need conditional (`if`/`then`) schema logic, out of scope for this R1 task.

**Known limitation (disclosed, not solved):** the lifecycle vocabulary now exists in three places — `SYSTEM-LIFECYCLE.md` (13 values), `task-contract.schema.json`'s `status` enum (14 values, i.e. those plus `DRAFT`) and this schema's `from_state`/`to_state` (a copy of the second). The two schemas share no `$ref`, so a future revision of any one of them (for example a future ADR adding the `MERGED` state `ADR-001` floats as a possibility) can silently drift from the others; the `DRAFT` difference between the lifecycle document and the schemas is already a live example. AC-06 compares only the two schema files, at acceptance time. Recommended, explicitly out-of-scope follow-up: a separate task extracting the lifecycle-state enum into one shared `$defs` file both schemas reference.

## Explicit non-scope

No controller code, no automatic transition-recording mechanism (nothing in this repository currently writes these records; that remains manual/future work), no change to any existing document's own `status:` frontmatter field or how it's parsed (`.claude/hooks/common.py:parse_frontmatter()` is untouched), no change to `schemas/v2/task-contract.schema.json`'s existing `status` enum (this task reuses it by citation, not by editing the sibling file), no change to any `CONTROLLED_PATHS` file, no capability-registry/evidence-manifest/seal-attestation/review-acceptance-receipt schemas (separate tasks under this same system — capability-registry already drafted as `TASK-CAPABILITY-001`).

## Repository reality and relevant existing capability

Confirmed via Glob (re-run 2026-09-18 after commit `b8ad499`): `schemas/v2/` currently contains exactly `task-contract.schema.json` + its 4 fixtures under `schemas/v2/fixtures/` — the output of `TASK-SCHEMA-001` (contract `READY_FOR_IMPLEMENTATION`; files written but not yet sealed, so not yet `IMPLEMENTED` per `SYSTEM-LIFECYCLE.md`; see `HANDOFF-001` for current status). `schemas/v2/capability-registry.schema.json` and its fixtures do **not** exist on disk: `TASK-CAPABILITY-001` is a contract only (`READY_FOR_IMPLEMENTATION`; its Stop Conditions forbid activating its lease while `TASK-SCHEMA-001`'s lease is unresolved — i.e. still `ACTIVE`/unsealed and not explicitly deactivated), so nothing has been written for it yet. No state-transition schema or fixture exists yet. `.ai-governance/audit.log` was directly read this drafting session and confirmed to be a tool-permission decision log (`{"at", "tool", "subject", "decision", "reason", "task_id"}`), not a lifecycle-state transition log — no duplication risk. `docs/08-process/SYSTEM-LIFECYCLE.md`'s state table is the canonical source for 13 of the 14 vocabulary values this schema carries; the fourteenth, `DRAFT`, comes from the sibling schema's disclosed extension (see the `DRAFT` assumption above).

## Expected diff

| Kind | Expected |
|---|---|
| New files | `schemas/v2/state-transition.schema.json`, `schemas/v2/fixtures/state-transition-valid-example.json`, `schemas/v2/fixtures/state-transition-invalid-missing-required.json`, `schemas/v2/fixtures/state-transition-invalid-bad-state.json`, `schemas/v2/fixtures/state-transition-invalid-unknown-field.json` |
| Modified files | None |
| Removed files | 0 |
| Dependencies | None added to the repository; verification uses any external/ephemeral JSON Schema 2020-12 validator, same as `TASK-SCHEMA-001`/`TASK-CAPABILITY-001` |
| Schema/public contract | New — an independent schema artifact under `schemas/v2/` (a sibling to `task-contract.schema.json`, and to `capability-registry.schema.json` once `TASK-CAPABILITY-001` is implemented); does not alter any sibling schema's existing public shape |

## Blast radius and reversibility

Blast radius: one new schema file plus four new fixture files (one positive, three negative), all under the already-existing `schemas/v2/` directory tree; zero existing files modified. Reversibility: EASY — delete the five new files; nothing yet references them (no consuming controller/recording mechanism exists, per Explicit non-scope).

## Acceptance criteria

| ID | Criterion | Verification | Required evidence |
|---|---|---|---|
| AC-01 | Schema file is valid JSON Schema (2020-12 meta-schema) | Validate the schema file against the JSON Schema meta-schema | Validator output, exit code 0 |
| AC-02 | Schema validates the positive fixture | Run validator: schema + `state-transition-valid-example.json` | Validator output showing PASS |
| AC-03 | Schema rejects all three negative fixtures with the expected error class each | Run validator against each `state-transition-invalid-*.json` | Validator output showing FAIL for each, with the violated constraint named |
| AC-04 | No `CONTROLLED_PATHS` file appears in the diff | `git diff --name-only` against `allowed_paths` | Diff output |
| AC-05 | No change to any pre-existing `schemas/v2/` file: at minimum `task-contract.schema.json` and its 4 fixtures (5 files, present on disk at drafting time), plus `capability-registry.schema.json` and its 4 fixtures if `TASK-CAPABILITY-001` has been implemented by the time this task is | `git diff --name-only` shows none of those files | Diff output |
| AC-06 | At acceptance time, `from_state`/`to_state` enums are byte-for-byte identical (same values, same order) to `task-contract.schema.json`'s `status` enum. This is a point-in-time check only; it does not prevent later drift (see Known limitation) | Direct comparison of the three enum arrays | Diff/comparison output |

## Test and runtime plan

Manual validation using any standard-conformant JSON Schema 2020-12 validator, run externally to this repository (no new dependency added — see Expected diff). No runtime/multiplayer/persistence surface applies — static document task, same class as the two sibling schema tasks.

## Stop conditions

- Scope expansion beyond the single schema file and its fixtures (in particular: do not start building an actual transition-recording mechanism or wiring this into any hook — that is separate future work, and would require controller-code authorization `ADR-001` explicitly withholds).
- Documentation/code drift invalidates this contract (e.g. `ADR-001`, `SYS-V2-SCHEMAS-001`, or `SYSTEM-LIFECYCLE.md` is revised before this task completes).
- Material confidence becomes LOW on any required field's meaning.
- A required dependency/schema/public-interface change beyond `schemas/v2/state-transition.schema.json` is discovered.
- Lease is absent, expired, or invalid.
- **Do not activate this task's lease while any other task's `.ai-governance/implementation-lease.json` is present and its `state` is `ACTIVE`, unless that other task is already sealed or its lease has been explicitly deactivated first** — the same risk `TASK-CAPABILITY-001`'s Stop Conditions already names for `TASK-SCHEMA-001`. This is a live-state check, not a settled snapshot: at the time of the last direct check (2026-09-18) no `implementation-lease.json` existed at all (the human had deactivated `TASK-SCHEMA-001`'s lease) and no `.ai-governance/implementation-seals/` directory existed, so the competing-lease risk was momentarily absent — whoever activates this lease must re-check both fresh, not trust this note. Note also that `scripts/activate_lease.py:176-178` refuses to activate at all unless `git status --porcelain --untracked-files=all` is empty (`.claude/hooks/common.py:165-177`), so any not-yet-committed or untracked file anywhere in the worktree — including another task's not-yet-committed implementation files — blocks activation; see `TECH-DEBT.md` `DEBT-003`.
- `doctor.py --require-claude` returns the DEBT-001 false-positive `FAIL` on the activating machine and the human has not confirmed the `PYTHONUTF8=1` workaround (or the code fix) is in place there — do not assume the workaround transfers machine-to-machine.

## Rollback

Delete the 5 new files listed under Expected diff. No other file depends on them yet.

## Independent ready review

The independent reviewer creates a separate immutable receipt from `READY-REVIEW-RECEIPT-TEMPLATE.md`, bound to this contract's final SHA-256. `approval_mode: hash` applies (R1, not R4).

**Reviewer-independence note (disclosed, same limitation as the two sibling tasks, per `PACKAGE-REPORT.md`):** the reviewer is a separate Agent-tool dispatch, fresh context, no access to this drafting session's reasoning, but runs on the same underlying model family as the author. Final lease activation remains human-only regardless of this receipt's disposition.
