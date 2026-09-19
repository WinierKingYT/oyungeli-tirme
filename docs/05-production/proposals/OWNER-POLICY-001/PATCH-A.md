# OWNER-POLICY-001 Patch A — how to apply

Status: `PROPOSED`, revision 3 (revisions 1 and 2 got `FIX_FIRST`; revision 3 got `READY` for the owner's dry run from a correctness and a security review, both static, nothing executed). Applier SHA-256 of revision 3: `e1458693e5ec60175ccfe8e7549075163a8e831b4ce2a969a2538971a13a7f11` (both reviewers computed it; recompute before running). Not applied. Design: `DESIGN.md` revision 4.

## What it does

Inert without `.ai-governance/owner-policy.json`; with one present ("policy mode") it adds:

- Strict policy validation: schema, explicit `expires_at`, `agent/` branch, an existing absolute `git` executable, a non-empty `deny_paths`, reviewer ids without placeholders, and lane paths that are literal or end in `/**`, use the same normalization as `matches_any` (leading `./` and dots stripped) when tested against controlled files, and never contain empty, `.`, or `..` segments, segments ending in a dot or space, wildcards, backslashes, `:`, or a leading `~`. Any segment whose dot-stripped form starts with `git` is rejected, which also means a directory such as `Assets/Game/GitTools` cannot be a lane path (rename it or list its files).
- Exact owner-policy command recognition on the raw command (ASCII and printable only, full-match). Only the activate, seal, commit, and task-documents-commit forms; seal and commit also need a lease whose `authority` is `owner-policy` in the right state (`ACTIVE` for seal, `SEALED` for commit). Patch B provides the scripts and the remaining checks (policy-hash equality, seal digest, commit deadline); Patch A alone activates nothing.
- Every hook `ask` becomes `deny` (no human is present); MCP tools included.
- Writes of NEW or untracked `docs/05-production/tasks/TASK-*.md` and `READY-TASK-*.md` are allowed without a prompt; overwriting an existing or tracked file, other documents, and acceptance receipts are denied.
- Controlled-path checks now also run on the project-root-relative path, case-insensitively (a shifted working directory can no longer hide a controlled path).
- `load_lease(allow_sealed=True)`, the policy hash in the audit log, `scripts/owner_policy.py` and `scripts/agent_commit.py` added to `CONTROLLED_PATHS`, and to the script names the shell hook forbids.

Side effects even without a policy (all are additions or corrections, never new permissions except the last): any shell command that merely mentions `agent_commit.py` or `owner_policy.py` (including `cat` or `rg`) is denied; every audit event gains a `policy_sha256` key (`null` without a policy); the write hook now judges every write from the project root, so a write whose target lies outside the project root is denied, a controlled path is denied even when the session's working directory is shifted (case-insensitively), and a lease's `allowed_paths` are matched against the root-relative path (a lease write from a shifted working directory that used to be denied can now be allowed, and one that used to slip through under a nested directory of the same name is denied).

Drafting rule in policy mode, stated exactly: an agent may write `docs/05-production/tasks/TASK-*.md` and `READY-TASK-*.md` when Git does not track the path. That includes an existing untracked draft (so the agent can iterate on its own drafts) and a path that Git ignores, and excludes anything tracked, including a tracked file deleted from the working tree. If Git cannot answer, only a brand-new path is allowed.

One more small relaxation without a policy: a documentation write whose working directory is shifted used to fall through to a denial; because the documentation check is now root-relative, it returns the normal `ask` (denied only in policy mode).

## Follow-ups from the reviews (not blockers)

- Add `.git/**` to `CONTROLLED_PATHS` and make `matches_any` strip only one leading `./` (it strips every leading dot, so `<root>/.Assets/_Prototype/x.cs` matches a lease for `Assets/_Prototype/**`; Unity ignores dot directories, so this only admits a stray hidden path).
- Reject a lane that starts at `docs`; make the audit test assert `"policy_sha256" in audit[0]`; add a junction test if the owner's account can create junctions.
- Patch B: `--task-docs` must fail explicitly, not skip silently, when `git add` refuses an ignored path.
- The two `ask` to `deny` gaps listed below.

## Not tested by the author or the reviewers

Nothing was executed. The new `validate_owner_policy_mode` tests (which run in a real temporary Git repository) and the two shifted-working-directory lease tests are the first real run. Known gaps: no MCP case that would return `ask` without a policy, and no test of `ask` to `deny` under an active lease (a compound shell command); the Windows behavior of path resolution for not-yet-existing files; symlinks and junctions inside `docs/05-production/tasks`.

## Apply (owner, own terminal)

1. Commit this directory, then confirm it is unchanged: `git status --short -- docs/05-production/proposals/OWNER-POLICY-001` must print nothing.
2. Compare the applier's SHA-256 (`python scripts/artifact_digest.py docs/05-production/proposals/OWNER-POLICY-001/apply_patch_a.py`) with the value in the message that delivered this patch and with the value the final independent reviewer reported. Do not run it if they differ.
3. Dry run: `python docs/05-production/proposals/OWNER-POLICY-001/apply_patch_a.py`. Expect five `WOULD WRITE` lines. On `NOT APPLIED` stop and report the message.
4. Apply with `--apply`.
5. Read `git diff` for the five files. It must contain only what this document describes. This is the decisive control.
6. Verify: `python scripts/validate_os.py --working-repository` and `python scripts/doctor.py --working-repository` must both print `RESULT: PASS`; then check the default mode in a clean copy without `implementation-seals` (as for `DEBT-FIX-001`).
7. Commit the five files. Dirty controlled files block every lease activation.

## Rollback

`git restore .claude/hooks/common.py .claude/hooks/govern_shell.py .claude/hooks/govern_write.py scripts/validate_os.py .gitignore` before committing; `git revert` after.
