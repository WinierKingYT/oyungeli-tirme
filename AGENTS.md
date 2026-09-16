# Project Operating Contract

## Mission

Produce small, traceable, verified game-development changes while preserving design authority, architecture, project state, and evidence quality. Speed does not outrank correctness.

## Authority order

Use project truth in this order:

1. `docs/00-project/PROJECT-CONSTITUTION.md`
2. Accepted ADRs in `docs/04-decisions/`
3. Accepted system specifications in `docs/03-systems/`
4. Active implementation lease and its task contract
5. `docs/05-production/CURRENT-MILESTONE.md`
6. `docs/01-design/GDD.md`
7. Backlog and risk register
8. Current conversation
9. Agent assumptions

Never silently resolve contradictions between authority levels. Report `AUTHORITY_CONFLICT` and stop the affected work.

## Fundamental gate

No production implementation is authorized without an active, unexpired implementation lease whose task-contract hash and independent READY-review receipt hash both match, whose clean base Git HEAD and branch still match, and whose `allowed_paths` contain every proposed write.

A request to discuss, research, design, plan, review, document, or improve a system does not authorize production code or asset changes.

## Required lifecycle

Every material system follows:

`DISCOVERY -> SPECIFIED -> READY_REVIEW -> READY_FOR_IMPLEMENTATION -> IMPLEMENTED -> VERIFIED -> INDEPENDENT_REVIEW -> ACCEPTED -> FROZEN`

Skipping a state is a process failure. A state label is valid only when its required evidence exists.

## Before implementation

1. Inspect repository reality.
2. Read relevant authority documents.
3. Search for existing capabilities and duplicate mechanisms.
4. Report code/documentation drift.
5. Define purpose, scope, and explicit non-scope.
6. Define ownership, dependencies, interfaces, events, and lifecycle.
7. Define networking authority and persistence implications when applicable.
8. Record uncertainty, assumptions, risks, reversibility, and blast radius.
9. Define functional and non-functional acceptance criteria.
10. Define tests, runtime evidence, performance budgets, and failure injection.
11. Predict the expected diff.
12. Obtain an independent `READY` disposition.
13. Bind the independent READY receipt to the final task-contract SHA-256.

## Implementation rules

- Implement only the active task contract.
- Prefer the smallest coherent change.
- Do not perform unrelated refactors.
- Do not add dependencies, schemas, or public interfaces outside approved scope.
- Reuse an existing capability before creating a new abstraction.
- Do not duplicate canonical state or ownership.
- Do not modify frozen systems without an approved change request.
- Do not weaken tests, validators, hooks, permissions, or evidence requirements.
- Do not edit the implementation lease or invoke its activation scripts.
- Do not invoke the implementation seal script; only the human operator may freeze the diff and close authority.
- Do not author your own READY or acceptance receipt.
- Do not auto-approve compound, piped, redirected, substituted, or nested-shell commands.
- If scope must expand, stop and report `SCOPE_EXPANSION`.
- If repo reality invalidates the task, stop and report `DRIFT_DETECTED`.

## Uncertainty protocol

Unknown information is never permission to invent. Material uncertainty must be classified as one of:

- `UNRESOLVED`
- `ASSUMPTION_REQUIRES_APPROVAL`
- `BLOCKER`
- `SPIKE_REQUIRED`

Low confidence in requirements, repository understanding, architecture, engine behavior, networking, persistence, or performance blocks implementation in that area.

## Completion rules

Code written is not done. Compilation is not acceptance. Tests passing alone are not acceptance.

A task can be accepted only when all applicable evidence exists:

- approved scope implemented;
- actual diff reconciled against expected diff;
- build and automated tests pass;
- runtime acceptance criteria pass;
- multiplayer, persistence, failure, and performance checks pass where applicable;
- independent reviewer returns `ACCEPT`;
- documentation matches implementation;
- P0 and P1 defects are zero;
- known limitations are explicit;
- a repository-bound implementation seal covers the exact changed paths and diff;
- an independent acceptance receipt is bound to the exact implementation revision, seal/diff hashes, and evidence-pack SHA-256.

## Independent review

The task author cannot be its READY approval authority. The implementer cannot be the acceptance authority. Reviewers do not repair production code during review. They return exactly one disposition: `ACCEPT`, `FIX_FIRST`, or `BLOCKED`.

## Control-plane health

Run `python scripts/doctor.py` before the first agent session on each environment and after changing Claude Code, Python, settings, hooks, or governance scripts. A missing interpreter, hook timeout, or hook startup failure is not assumed safe.

## Reporting contract

Before implementation report:

- confidence matrix;
- repository reality findings;
- blast radius;
- reversibility class;
- expected diff;
- validation plan;
- stop conditions.

After implementation report:

- actual diff;
- test and runtime evidence;
- acceptance-criteria matrix;
- deviations and limitations;
- unresolved risks;
- reviewer disposition.
