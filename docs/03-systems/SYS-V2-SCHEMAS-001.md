# SYS-V2-SCHEMAS-001 — V2.0 machine-readable contracts and policy schemas

Status: `SPECIFIED`

## Problem, outcome, users, and design intent

v1.2's task contracts, READY receipts, and leases are human-readable Markdown with a restricted YAML frontmatter subset (`.claude/hooks/common.py: parse_frontmatter()`), validated by ad-hoc Python checks scattered across `scripts/activate_lease.py`. [ADR-001](../04-decisions/ADR-001-v2-product-and-threat-specification.md) accepted the V2.0 direction of a controller-mediated architecture (brief §6.2, "Machine-readable task contracts"): enforcement should rely on a versioned schema rather than growing more ad-hoc Python checks. Outcome: a small set of JSON Schema documents that make the task-contract shape machine-validatable, independent of any specific hook implementation. Users: the future V2.0 controller (schema consumer), and any human or agent authoring a task contract (schema as documentation).

## Scope / non-scope

In scope: a JSON Schema for the task-contract document's structured fields (the frontmatter-equivalent fields listed in the brief's §6.2 minimum field list). Non-scope (deferred to future tasks under this system, each requiring its own task contract): capability schema/registry, state-transition schema, evidence-manifest schema, seal/attestation schemas, review/acceptance receipt schemas, migration/versioning rules. Non-scope (permanently, per ADR-001): no controller code, no hook changes, no changes to any `CONTROLLED_PATHS` file, no changes to v1.2's actual Markdown-frontmatter task contract format — this schema does not replace or modify v1.2's existing mechanism, it specifies a separate, additive artifact for the future V2.0 controller.

## Repository reality and existing capability search

No existing JSON Schema files exist in this repository (confirmed by Glob search for `*.schema.json` — zero results before this task). The closest existing artifact is `docs/templates/TASK-CONTRACT-TEMPLATE.md`'s frontmatter block, which this schema formalizes without altering.

## Functional requirements

FR-1: The schema validates the minimum field set from the accepted V2.0 spec (brief §6.2): task and system identity; rigor/risk classification; base repository and exact revision; author and approval identities; scope and explicit non-scope; allowed and denied paths; allowed capabilities; network policy; expected diff envelope; dependency/schema/public-interface constraints; functional and non-functional acceptance criteria; required evidence classes; stop conditions; rollback strategy; expiry and invalidation rules.
FR-2: The schema rejects unknown top-level fields (`additionalProperties: false`) so a future controller fails closed on typos or unauthorized field injection, per brief §6.2 ("reject unknown security-sensitive fields").
FR-3: Enum fields (e.g. rigor tier, approval mode) are closed enums, not free-text strings.

## Quality attributes and non-functional requirements

Testability: the schema must be independently validatable with a standard JSON Schema validator (no custom tooling required). Maintainability: single file, versioned, under 200 lines. Security: `additionalProperties: false` at every object level that represents a security-relevant boundary (allowed_paths, allowed_commands/capabilities).

## Canonical state and ownership

| State | Owner | Writers | Readers | Persistence | Replication |
|---|---|---|---|---|---|
| Schema file content | This system (SYS-V2-SCHEMAS-001) | Task author under an active lease | Future V2.0 controller; task authors; reviewers | Git-tracked file | N/A (single repo) |

## Lifecycle and state machine

Follows `docs/08-process/SYSTEM-LIFECYCLE.md` unchanged, per ADR-001 (no competing lifecycle vocabulary accepted).

## Interfaces, commands, events, queries

None — this is a static schema document, not a running service. It is consumed by future tooling (out of scope here) via standard JSON Schema validation libraries.

## Dependencies and dependency direction

Depends on: ADR-001 (accepted direction). Depended on by: any future V2.0 controller task-contract-loading code (not yet scoped, not yet authorized — ADR-001 explicitly withholds v2.0 controller implementation authorization).

## Multiplayer authority and failure behavior

Not applicable — this is a build-time/authoring-time schema artifact, not a runtime game or networking system.

## Save/version/migration behavior

The schema file itself is versioned via a `$id`/`title` field including a version string (`v2.0-draft-1`), so future incompatible revisions are distinguishable. No migration tooling is in scope for this first task.

## Observability and reproducibility

Any JSON Schema validator (e.g. `ajv`, `jsonschema` Python package) run against a sample document and this schema produces a deterministic, reproducible pass/fail — no hidden state.

## Performance/content budgets

Not applicable — static document, no runtime performance surface.

## Edge cases, failure injection, and recovery

Edge cases the schema must reject: an `allowed_paths` entry equal to `"*"`, `"**"`, or `"./**"` (mirrors `activate_lease.py:128`'s existing v1.2 rule, carried forward as a documented constraint even though this schema does not itself enforce it at runtime); a task contract missing `rigor`; an `approval_mode` value outside `{hash, ssh-signature}`.

## Acceptance criteria and evidence plan

| ID | Criterion | Verification | Required evidence |
|---|---|---|---|
| AC-01 | Schema file is valid JSON Schema (draft 2020-12) | Run a standard JSON Schema meta-schema validation | Validator output (exit code + no errors) |
| AC-02 | Schema validates a hand-written positive fixture (a well-formed example task contract in schema form) | Run schema validator against the fixture | Validator output showing PASS |
| AC-03 | Schema rejects at least 3 hand-written negative fixtures (missing required field; wildcard `allowed_paths`; unknown extra field) | Run schema validator against each negative fixture | Validator output showing FAIL for each, with the expected error |
| AC-04 | No `CONTROLLED_PATHS` file is touched | `git diff --name-only` against the task's `allowed_paths` | Diff output |

## Risk, rigor, reversibility, blast radius, and kill criteria

Rigor: R1 (new, self-contained, non-executable artifact; no existing behavior is modified; fully reversible by deleting the new file). Blast radius: one new file under a new `schemas/v2/` directory; zero existing files modified. Kill criteria: if drafting the schema surfaces a field whose meaning is still genuinely undecided (e.g. exact capability taxonomy wording), stop and mark that field `UNKNOWN`/`PROPOSED` rather than inventing a decision.

## Unknowns, assumptions, confidence, and required spikes

`UNKNOWN`: exact JSON Schema draft version the future controller tooling will target (assumed 2020-12 as the current stable draft; revisit if a controller implementation phase picks a validator library with different constraints). `ASSUMPTION_REQUIRES_APPROVAL`: this schema's field names are drawn directly from the brief's prose list (§6.2) and have not been independently reviewed for naming conventions — flagged for the independent reviewer below. Confidence: MEDIUM — the field *list* is well-sourced (ADR-001/brief), but exact JSON Schema field typing/structure choices are this task's own design work and have not been validated against any real controller implementation (none exists yet).

## Independent review record

Reviewed independently (fresh-context agent, separate from this document's author) against the Ready gate on 2026-09-16: `READY_FOR_IMPLEMENTATION` — system scope, ownership, dependencies, and risk classification found complete; the one open interpretive question (ADR-001's V2-02 blocker vs. this system's R1-tier work) found correctly disclosed as `ASSUMPTION_REQUIRES_APPROVAL` rather than self-resolved. This authorizes task-level work to be proposed and leased under this system; it does not itself claim `ACCEPTED`/`FROZEN` status, which requires accepted task implementations under it per `docs/08-process/SYSTEM-LIFECYCLE.md`.

`ASSUMPTION_REQUIRES_APPROVAL` (added after independent system-level READY review, finding F1): [ADR-001](../04-decisions/ADR-001-v2-product-and-threat-specification.md)'s Consequences section states DEBT-001/RISK-006 and the two open spikes block "the next phase (V2-02, contracts/schemas)" from starting cleanly. This system takes the position that the blocker applies at full strength to **R2-and-above** work under V2-02 (execution/sandbox/preflight-dependent work), and applies in a narrower, evidence-documented way to **R1** static-artifact tasks under this system: DEBT-001 is confirmed a fail-closed **false positive** (`doctor.py --require-claude` reports `FAIL: package must be installed at the Git repository root` on this repository's actual non-ASCII path even though the repository is correctly installed — reproduced directly, exit code 1, 2026-09-16), not a false negative, so its residual risk for a non-executable R1 task is unreliable/blocked *evidence-gathering*, not an unsafe pass-through. Every task under this system must still run `doctor.py --require-claude` and record its actual output (including this known false-positive) as part of its own evidence — never silently skip the check. This system-level position is itself subject to revision by whoever performs each task's own independent review; it is not a blanket waiver.
