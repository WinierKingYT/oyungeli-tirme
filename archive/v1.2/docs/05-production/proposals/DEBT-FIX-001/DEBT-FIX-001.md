# DEBT-FIX-001 — Patch proposal for DEBT-002, DEBT-003, DEBT-006

Status: `PROPOSED`, revision 3 (after two rounds of independent review, both `FIX_FIRST`). Not applied. Nothing here changes behavior until the owner runs the applier.

## Why a proposal and not a change

The affected files are `CONTROLLED_PATHS`; no agent can edit them. The proposal is one applier script the owner runs once. It edits only five listed files, checks that every snippet still matches exactly once, checks that the patched Python compiles, and only then writes; `--apply` needs an interactive terminal.

Not tested by the author or the reviewers: none of them could run Python scripts. The new tests in `validate_os.py` are the first real test of this code, so the owner's first run is the real verification. Revision 3 must still get a final review.

## What changes

| Debt | Change | Files |
|---|---|---|
| `DEBT-003` | New explicit flag `activate_lease.py --inherit-dirty`. Without it, any dirty file still blocks activation, exactly as today. With it, dirty files that already sit inside the task's own `allowed_paths` are accepted (an unsealed implementation whose lease expired can be re-leased and sealed), up to 50 paths. Never inheritable, flag or not: the task contract, READY receipt, signature and allowed-signers files, and anything matching `CONTROLLED_PATHS`; those must be committed and unmodified. Changes outside `allowed_paths` always block, with up to five offending paths named. Paths are printed with `ascii()`. The inherited list and count appear on the review screen, and per-file SHA-256 values are stored in the lease (`inherited_paths`) and copied into the seal. The seal now also lists changed paths with `--no-renames`, so a rename shows both its old and new path. | `common.py` (new `git_dirty_paths`), `activate_lease.py`, `seal_implementation.py` |
| `DEBT-002` | Activation refuses when an unexpired `ACTIVE` lease exists, and refuses a lease file that is unreadable, has a naive expiry, has a non-string state, or has any state other than `ACTIVE` or `SEALED`, all before any prompt. After the owner types `ACTIVATE`, the prior lease is copied byte for byte to `.ai-governance/implementation-seals/PRIOR-<task>-<state>-<time>.json` (created exclusively, task id sanitized and length-capped) before the new lease is written. | `activate_lease.py` |
| `DEBT-006` | `validate_os.py --working-repository` skips the two package-only checks (no lease file, no seals) but adds one: a lease or seal tracked by Git, or a failing `git ls-files`, fails. Default behavior and the CI workflow are unchanged. `doctor.py --working-repository` passes the flag through. Both temporary repository copies inside `validate_os.py` (attestation and R4 signature tests) now exclude the lease, the seals, and `scheduled_tasks.lock`. | `validate_os.py`, `doctor.py` |

## Authority analysis

- No agent gains any ability. Activation and sealing stay human-run with typed confirmations; hooks are not touched.
- The default activation behavior is unchanged. Inheriting dirty files needs an explicit flag chosen by the owner at the terminal, and the owner sees the list and count before typing `ACTIVATE`.
- The old guarantee that the approved contract, receipt, and signature files equal committed bytes is kept. Dirty controlled governance files are never inherited.
- `DEBT-002` only adds refusals and an audit archive. `DEBT-006` weakens a check only when the flag is passed, and adds a tracked-file check.
- Residual risk: a contract with broad `allowed_paths` (for example `docs/**`) can inherit other unreviewed dirty files when the owner passes `--inherit-dirty`. The list, the count, and the stored hashes are mitigation and audit, not prevention; the stored hashes do not preserve the inherited content itself. `activate_lease.py` already accepts `**/*`, and `matches_any` lets `*` cross `/`; both are pre-existing. Inherited paths whose name cannot be read as UTF-8 or that are not regular files are recorded as `ABSENT`.

## Tests added to `validate_os.py`

1. A dirty file inside `allowed_paths` is refused without `--inherit-dirty`, naming the flag.
2. The same file is accepted and listed with `--inherit-dirty`.
3. A dirty file outside `allowed_paths` still blocks, and the rejection names the file.
4. A second activation while an unexpired `ACTIVE` lease exists is refused with that reason.
5. A lease file in an unknown state (`../BOGUS`) is refused with that reason.
6. A lease file whose state is a JSON list is refused as unreadable.
7. Activation over a `SEALED` lease succeeds and creates exactly one `PRIOR-...` archive.

Not tested: renames and the `--no-renames` seal change, expired `ACTIVE` leases, malformed JSON, naive dates, controlled-path and protected-file rejection (an optional extra test: a dirty task contract with `--inherit-dirty` must be refused). Symlinks, junctions, and Windows short names were not examined. These are follow-ups.

## How to apply (owner, own terminal)

1. Commit this proposal directory first, so the reviewed bytes are pinned in Git, then confirm nothing changed since:
```powershell
git status --short -- docs/05-production/proposals/DEBT-FIX-001
```
The output must be empty immediately before you run the applier.
2. Check the applier's SHA-256 (`python scripts/artifact_digest.py docs/05-production/proposals/DEBT-FIX-001/apply_debt_fix_001.py`) against the value in the chat message that delivered this proposal and against the value the final independent reviewer reports. Revision 3 as authored: `3a45dbe13c1b4c5b66c2543a84bcab429a332c580ec14009a86fbe63cc48e72a`. If it differs, do not run it. The `ALLOWED_TARGETS` list and the terminal check only guard against accidents and agent runs of the reviewed file; a modified applier could remove them.
3. Dry run. Expect five `WOULD WRITE` lines; on `NOT APPLIED`, stop and report the message:
```powershell
python docs/05-production/proposals/DEBT-FIX-001/apply_debt_fix_001.py
```
4. Apply:
```powershell
python docs/05-production/proposals/DEBT-FIX-001/apply_debt_fix_001.py --apply
```
5. The decisive control: read `git diff` for the five files and confirm it contains only what this document describes. Then verify (owner-run; agents cannot run these flagged commands):
```powershell
python scripts/validate_os.py --working-repository
```
```powershell
python scripts/doctor.py --working-repository
```
Both must print `RESULT: PASS`. Also confirm the default check in a clean copy without `implementation-seals` (as done for `TASK-UNITY-RULES-001`).

## Rollback

`git restore .claude/hooks/common.py scripts/activate_lease.py scripts/seal_implementation.py scripts/validate_os.py scripts/doctor.py` before committing; `git revert` after.

## After applying

Commit the five patched files before the next activation: they are `CONTROLLED_PATHS`, and activation now refuses any dirty controlled file (it also refused any dirty file before). Then update `docs/05-production/TECH-DEBT.md`: `DEBT-002`, `DEBT-003`, `DEBT-006` become "fix applied, verification pending" with command outputs and the commit SHA. `git_worktree_clean` is left in place, unused by `activate_lease.py`. To re-lease an expired, unsealed task: `python scripts/activate_lease.py <task> --inherit-dirty`, then seal.

## Follow-ups (not part of this patch)

- An `ADR-002` addendum and a threat-model row for the changed activation semantics; the acceptance and READY records of `TASK-UNITY-RULES-001` describe the old "clean tree" precondition and remain historically correct.
- Tighten `allowed_paths` validation (`**/*`, `lstrip("./")` in `matches_any`).
- More adversarial tests (renames, expired leases, malformed JSON, naive dates, protected and controlled paths).
- Whether `PRIOR-*` archives belong in a separate ignored folder instead of `implementation-seals/`.
