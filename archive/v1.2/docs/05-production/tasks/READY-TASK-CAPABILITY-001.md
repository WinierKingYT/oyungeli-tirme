---
review_id: REVIEW-TASK-CAPABILITY-001-R5
task_id: TASK-CAPABILITY-001
disposition: READY_FOR_IMPLEMENTATION
reviewer: Claude Sonnet 5 (independent code-reviewer agent, fresh context per review round)
task_sha256: 292569699a928e49314919c41056dba9f61f0e096bf677a3f596ef9eef43e903
reviewed_at: 2026-09-18T00:00:00Z
approval_mode: hash
signature_file: UNSET
allowed_signers_file: UNSET
---

# Independent Ready Review Receipt — TASK-CAPABILITY-001

## Scope reviewed

`docs/05-production/tasks/TASK-CAPABILITY-001.md` in its final state (digest above), together with `docs/03-systems/SYS-V2-SCHEMAS-001.md`, `docs/04-decisions/ADR-001-v2-product-and-threat-specification.md`, `docs/08-process/SYSTEM-LIFECYCLE.md`, `schemas/v2/task-contract.schema.json` and its fixtures, `.claude/hooks/common.py` (`CONTROLLED_PATHS`), `scripts/activate_lease.py`, `scripts/doctor.py`, `.ai-governance/implementation-lease.json` (live state), and the sibling `docs/05-production/tasks/TASK-SCHEMA-001.md`/`READY-TASK-SCHEMA-001.md` pair this task follows the exact pattern of.

## Repository and authority evidence

`ADR-001` (`ACCEPTED`), `SYS-V2-SCHEMAS-001` (`SPECIFIED`, independently reviewed `READY_FOR_IMPLEMENTATION` for task-level work under it), `python scripts/task_digest.py` output for the final contract SHA-256 (recomputed after the frontmatter status/approval fields were updated post-review — the pre-update digest was discarded, not reused, per this project's own recorded lesson in `HANDOFF-001` about digest invalidation on edit).

## Findings — iteration history (disclosed for evidence-trail honesty; this receipt is the final, binding one)

| ID | Severity | Evidence | Required correction | Status |
|---|---|---|---|---|
| F1 | HIGH | `scripts/activate_lease.py:227-228` writes the lease file unconditionally, no check for an existing `ACTIVE` lease; contract disclosed `TASK-SCHEMA-001`'s lease was still active in prose but not in its Stop Conditions checklist | Add explicit stop condition naming the competing-active-lease risk | Fixed round 2; recorded separately as `TECH-DEBT.md` `DEBT-002` |
| F2 | MEDIUM | `risk_tier` field duplicated the sibling schema's existing `rigor` field/enum with no disclosed distinction | Rename to `min_rigor`, disclose the distinct semantic (capability's minimum required rigor vs. a task's own self-declared rigor) | Fixed round 2 |
| F3 | LOW-MEDIUM | Field-naming uncertainty only implied by analogy to a sibling document, not classified first-person per `AGENTS.md`'s Uncertainty Protocol | Add explicit first-person `ASSUMPTION_REQUIRES_APPROVAL` tag naming the specific fields | Fixed round 2 |
| F4 | LOW | `allowed_path_patterns`/`allowed_command_patterns` diverged from the sibling schema's `allowed_paths`/`allowed_commands` naming, undisclosed | Disclose the `_patterns` suffix rationale (glob-capable match patterns vs. exact paths) | Fixed round 2 |
| F5 | LOW | Citation `task-contract.schema.json:46-52` for the `rigor` field was off by three lines (actual property is at lines 49-52) | Correct the line-range citation | Fixed round 3 |
| F6 | LOW | Blast Radius section's file-count phrasing ("two new files plus three new fixture files") didn't match the 1-schema/4-fixture breakdown used consistently everywhere else in the document | Reword to match the rest of the document | Fixed round 4 |
| F7 | MEDIUM-HIGH | Lines 24 and 48 incorrectly stated `TASK-SCHEMA-001` was `IMPLEMENTED`, contradicting lines 32/85 in the same document (and `TASK-SCHEMA-001.md`'s own frontmatter, the live lease file, and `HANDOFF-001`) which correctly stated its lease is still `ACTIVE`/unsealed, i.e. still `READY_FOR_IMPLEMENTATION` per `SYSTEM-LIFECYCLE.md` | Correct both instances to accurately state the sibling task's real current state | Fixed round 5 |

## Readiness matrix

| Area | Result | Evidence |
|---|---|---|
| Scope/non-scope | PASS | No duplication of `schemas/v2/task-contract.schema.json` or its `allowed_capabilities` field; confirmed via direct diff of `allowed_paths` against existing `schemas/v2/` inventory |
| Ownership/interfaces/lifecycle | PASS | Correctly scoped under `SYS-V2-SCHEMAS-001`'s own declared non-scope/future-task list; no competing lifecycle vocabulary introduced |
| Risk/reversibility/blast radius | PASS | R1, fully reversible by deleting 5 new files, blast radius confined to `schemas/v2/` |
| Networking/persistence/performance | PASS (N/A) | Correctly marked not applicable — static document task |
| Acceptance/tests/runtime evidence plan | PASS | AC-01–AC-05 concrete; validator scoped as external, no repo dependency added |
| Expected diff/allowed paths/commands | PASS | No wildcard `allowed_paths` entries; `allowed_commands` limited to `git diff *`, consistent with the sibling task's already-cleared bar |
| Rollback/stop conditions | PASS | Competing-active-lease risk now present in the canonical Stop Conditions checklist, not only in prose |
| Internal factual consistency | PASS (as of round 5) | All citations and cross-document factual claims independently re-verified against live repository state; no remaining contradiction found |

## Disposition rationale

Seven findings across five review rounds, all resolved in the final document state (digest above) — comparable rigor to `TASK-SCHEMA-001`'s own four-round, seven-finding history. Two of the seven (F1, F7) were genuine substantive defects (a real governance gap now separately tracked as `TECH-DEBT.md` `DEBT-002`, and a real factual contradiction about a dependency's lifecycle state); the remainder were citation/wording precision issues, caught by holding this task to the same bar the sibling task's own review history already established. `READY_FOR_IMPLEMENTATION` is valid for `task_sha256` above; any further edit to the task contract invalidates this receipt.

**Note on scope relative to `TASK-SCHEMA-001`'s lease state:** this task's own Stop Conditions (F1's fix) explicitly forbid activating its lease while `TASK-SCHEMA-001`'s lease remains `ACTIVE`/unsealed. As of this receipt, that condition still holds — `TASK-SCHEMA-001` has not yet been sealed. This task is contract-complete and technically `READY_FOR_IMPLEMENTATION`, but its lease cannot be responsibly activated until `TASK-SCHEMA-001` is sealed or its lease explicitly deactivated first, independent of DEBT-001's own (currently operationally resolved) status.
