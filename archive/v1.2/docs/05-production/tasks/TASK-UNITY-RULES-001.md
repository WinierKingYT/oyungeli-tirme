---
task_id: TASK-UNITY-RULES-001
status: READY_FOR_IMPLEMENTATION
authored_by: Claude Sonnet 5 (drafting agent, this session)
approved_by: Claude Sonnet 5 (independent code-reviewer agent, fresh context per review round)
ready_review_receipt: docs/05-production/tasks/READY-TASK-UNITY-RULES-001.md
rigor: R1
approval_mode: hash
system_id: UNSET
allowed_paths:
  - .claude/rules/unity.md
allowed_commands:
  - git diff *
---

# Task Contract — TASK-UNITY-RULES-001

## Problem and outcome

The project owner stated on 2026-09-18 that the engine will be Unity. `docs/00-project/PROJECT-STATUS.md` now records `PROPOSED: UNITY`, but the only engine rule file is `.claude/rules/unreal.md`, whose path triggers (`Source/**`, `Content/**`, `Plugins/**`) never match a Unity project. Outcome: one new path-scoped rule file, `.claude/rules/unity.md`, giving agents the same kind of guardrails for Unity paths, clearly labelled as a proposed profile that is not repository-verified.

## Authority inputs

- [ADR-001](../../04-decisions/ADR-001-v2-product-and-threat-specification.md) (`ACCEPTED`): PR5 "engine claims require engine evidence".
- `docs/00-project/PROJECT-STATUS.md`: engine profile `PROPOSED: UNITY`, not repository-verified.
- `docs/00-project/RIGOR-RISK-MODEL.md`: R1 = local low-risk behavior, bounded task plus automated test.
- `.claude/rules/unreal.md`: structural template for a path-scoped engine rule file.

`ASSUMPTION_REQUIRES_APPROVAL`: `system_id` is `UNSET` because no accepted system owns engine profiles. `scripts/activate_lease.py` does not require it. The independent reviewer judged in round 2 that no system record is needed for a single dormant R1 rule file and records that judgment in the receipt; the human confirms or overrules it at activation.

## In scope

Create exactly one file, `.claude/rules/unity.md`, with the content in "Proposed file content" below.

## Explicit non-scope

- No deletion or edit of `.claude/rules/unreal.md`. It stays dormant.
- No Unity project creation, no `Assets/`, `Packages/`, or `ProjectSettings/` directories.
- No change to `.claude/settings.json`, hooks, scripts, or any `CONTROLLED_PATHS` file.
- No claim that a Unity version, render pipeline, package, or networking stack is chosen; those remain facts to discover.
- No edit to `PROJECT-STATUS.md` inside the lease window (see "Follow-up after seal"), and no edit to the other known Unreal remnants: `docs/02-architecture/TECHNICAL-ARCHITECTURE.md:26`, `docs/templates/TASK-CONTRACT-TEMPLATE.md:15`, and `.claude/rules/multiplayer.md:3-6` (its `Source/**` and `Plugins/**` triggers are Unreal-shaped and dormant for Unity). These are separate drift items.

## Repository reality and relevant existing capability

- `.claude/rules/unreal.md` exists (20 lines, path-scoped frontmatter) and is the closest capability; nothing else covers Unity.
- `.claude/rules/assets.md` already matches `Assets/**/*` but carries no Unity serialization or GUID guidance, so it does not duplicate this task.
- No Unity project exists in the repository, so the new rule loads for no current path and is dormant until Unity work begins.
- `.claude/rules/**` is not in `CONTROLLED_PATHS` (`.claude/hooks/common.py:16-30`); a write there was denied only with `LEASE_REQUIRED`, which this task addresses.
- Rule content is derived from general Unity practice, not from this repository. It is unverified and is labelled `PROPOSED` in the file itself.

## Proposed file content

The implemented file must match this block exactly (fence lines excluded), with LF line endings and a single trailing newline.

```markdown
---
paths:
  - "Assets/**/*"
  - "Packages/manifest.json"
  - "Packages/packages-lock.json"
  - "ProjectSettings/**/*"
---

# Unity engine profile (PROPOSED, not repository-verified)

- Treat Unity version, render pipeline, installed packages, scripting backend, target platforms, networking stack, and save strategy as repository facts to discover.
- Do not create a new subsystem when an accepted owner already exists.
- Avoid unbounded per-frame callbacks, systems, or jobs; prefer events, timers, or bounded scheduled work. In GameObject-based code, keep per-frame allocations, `GetComponent`, and `Find*` calls out of hot paths.
- Keep gameplay rules out of UI and presentation-only components.
- ScriptableObjects or accepted project configuration own tunable gameplay data; avoid magic constants.
- Prefer the editor or an approved Unity CLI path over text edits to `.unity`, `.prefab`, `.asset`, and `.meta` files. Never move, rename, or delete an asset without its `.meta`, because GUID references break.
- Never commit generated folders (`Library/`, `Temp/`, `Logs/`, `obj/`, `UserSettings/`) or conventional build output folders such as `Builds/`.
- Renaming a serialized field loses data; use `FormerlySerializedAs` and record the migration.
- Respect assembly-definition dependency direction; circular asmdef references are prohibited.
- Replicate authoritative state, not cosmetic consequences. Define ownership, RPC direction, validation, and late-join behavior for the chosen networking stack.
- Compilation success does not prove Edit Mode or Play Mode tests, multiplayer, player builds, or target-platform behavior.
```

## Expected diff

| Kind | Expected |
|---|---|
| New files | `.claude/rules/unity.md` |
| Modified files | None |
| Removed files | 0 |
| Dependencies | None |
| Schema/public contract | None |

## Blast radius and reversibility

One new, self-contained Markdown file that only influences agent behavior when a Unity path is edited; no such path exists today. Reversibility class `EASY`: delete the file or revert its commit.

## Acceptance criteria

| ID | Criterion | Verification | Required evidence |
|---|---|---|---|
| AC-01 | `.claude/rules/unity.md` exists and its content equals the "Proposed file content" block (LF endings, single trailing newline) | Manual comparison against this contract; record the file's SHA-256 | Reviewer note plus the recorded SHA-256 |
| AC-02 | The file states `PROPOSED` and asserts no chosen Unity version, pipeline, package, or networking stack | Manual inspection | Reviewer note |
| AC-03 | The diff contains exactly one new file and no other change; `unreal.md` is unchanged | `git status --short` and `git diff --stat` | Command output |
| AC-04 | Repository validator still passes | `python scripts/validate_os.py` (result `PASS`) | Command output, date, commit |
| AC-05 | Preflight still passes | `python scripts/doctor.py` (result `PASS`) | Command output |
| AC-06 | The frontmatter is well formed: one `---` delimited block with a `paths:` list of exactly four entries | Manual inspection of the first lines | Reviewer note |

## Test and runtime plan

Evidence classes: manual inspection (AC-01, AC-02, AC-03) and the repository's mechanical validator and preflight (AC-04, AC-05). There is no automated test that the rule loads for Unity paths, because no Unity path exists; this is a stated limitation, not a pass. `validate_os.py` and `doctor.py` never reference `.claude/rules`, so AC-04 and AC-05 are regression guards only; R1's automated-test control is met by proxy, and AC-01, AC-02, AC-03 and AC-06 rest on manual inspection. Record command, environment, commit, timestamp, and outcome for each run.

## Stop conditions

- Scope expansion.
- Documentation/code drift invalidates the contract.
- Material confidence becomes LOW.
- Required dependency/schema/public interface change is discovered.
- Lease is absent, expired, or invalid.
- `validate_os.py` counts or requires rule files in a way that this addition breaks (round-1 review found it does not; kept as a guard; report `DRIFT_DETECTED`).

## Rollback

Delete `.claude/rules/unity.md` or revert its commit. No other state changes.

## Follow-up after seal (not part of this lease)

`PROJECT-STATUS.md:10` currently says the Unity path rules "are not written yet". Once `unity.md` exists and is sealed, update that row in a separate docs-only change made after sealing. `seal_implementation.py:43-45` rejects a seal when any changed path lies outside `allowed_paths`, so no docs edit (status, evidence, or debt records) may be made while the lease is active. Evidence for AC-01 to AC-05 is recorded after the seal.

## Operator preconditions (human-only, outside the agent's scope)

- `activate_lease.py` requires a clean worktree (`git_worktree_clean`, `.claude/hooks/common.py`) and a task contract plus READY receipt that are tracked in the base commit. Currently `schemas/` and `TASK-STATE-TRANSITION-001.md` are untracked, which blocks activation; the workaround is in `docs/05-production/TECH-DEBT.md` `DEBT-003`.
- Only the human runs `activate_lease.py`, `deactivate_lease.py`, and `seal_implementation.py`.

## Approval sequencing

The task digest covers the whole file, including frontmatter. Before the digest is computed, set `status: READY_FOR_IMPLEMENTATION`, `approved_by` (which must equal the receipt's `reviewer` exactly and differ from `authored_by`), and `ready_review_receipt: docs/05-production/tasks/READY-TASK-UNITY-RULES-001.md`. Then compute the digest, then issue the receipt bound to it. Author and approver run on the same underlying model, so independence is procedural, not cryptographic, as with `TASK-SCHEMA-001`; the human must accept or reject that limit at activation. The `system_id` handling is the one recorded under "Authority inputs".

Steps, in order: (1) edit frontmatter only (`status`, `approved_by`, `ready_review_receipt`); the receipt states that the delta from the reviewed draft is frontmatter only; (2) compute the digest; (3) issue the receipt bound to it; (4) the human commits the contract and the receipt and confirms a clean worktree (`git status --short` empty, using the `DEBT-003` workaround for untracked files if needed); (5) the human activates the lease.

## Independent ready review

The independent reviewer creates a separate immutable receipt from `READY-REVIEW-RECEIPT-TEMPLATE.md`. The receipt binds its disposition to the final SHA-256 of this task contract. After that digest is recorded, changing this task invalidates the review.

Use `approval_mode: hash` for R0–R3. R4 requires `approval_mode: ssh-signature` and a trusted reviewer signature.
