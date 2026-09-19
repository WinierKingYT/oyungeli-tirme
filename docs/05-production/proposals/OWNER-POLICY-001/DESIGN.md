# OWNER-POLICY-001 — Owner-written standing policy with a separate agent worktree (design)

Status: `PROPOSED` design, revision 4. Revisions 1 to 3 each returned `FIX_FIRST` from an independent security review; revision 4 adopts the reviewer's simpler variant (unsigned policy, mandatory worktree) chosen by the owner on 2026-09-19. Not implemented. Implements option B of `ADR-002`. Next: one delta re-check, then two patch proposals, then one owner session at a terminal.

## Goal

The owner should not need a terminal for routine lease activation, sealing, or commits. Authority must still come from the owner (ADR-001 PR1), never from an agent's own action.

## Owner decisions (2026-09-19)

| Decision | Choice | Notes |
|---|---|---|
| Lanes | Prototype, production Unity code, engine rule files | Against the reviewer's advice; see "Accepted risks" |
| Highest rigor without the owner | R2 | Enforced as R1 until the ADR-001 D4 sandbox is accepted |
| Policy authenticity | Unsigned policy file, no signing key | Replaces the earlier passphrase-key choice after the review showed the signature added little in this architecture; ADR-001 D8 (key custody) is not needed for this feature |
| Policy lifetime | Indefinite (explicit `"expires_at": null`) | Against the reviewer's advice |
| Agent commits | Only to one standing `agent/work` branch in a separate worktree; the owner merges | Push is never automated |

## Mandatory separate worktree

The agent works in its own `git worktree` on the `agent/work` branch, never in the owner's main working tree. This does most of the risk reduction: the owner's Unity project and rule files are untouched until the owner merges, so Unity code that could run when the owner presses Play, and rule files that persist into later sessions, become a reviewed merge gate.

- `.ai-governance/` is gitignored and absent from a new worktree, so the policy, lease, seals, and audit log live only in the agent worktree, never in the owner's main tree.
- The patched controlled files (hooks, scripts, settings) must be merged into `agent/work` before the worktree is used.
- The empty hooks directory used to disable `.git/hooks` is created at runtime (git does not track empty directories).

## Policy file and its trust basis

`.ai-governance/owner-policy.json` in the agent worktree, written by the owner (with `scripts/owner_policy.py`, human-run), revoked by deleting it. `.ai-governance/**` is a `CONTROLLED_PATH`: agents cannot write it, and shell access to it is forbidden. Authenticity therefore rests on that write guard, exactly like the lease file today; there is no signature. This is a stated limit: anything that can write `.ai-governance/` can already forge a lease, and code running with the owner's rights could remove any verifier.

## When policy mode applies

Policy mode means: a valid policy file is present. In policy mode every decision that would need a human answer becomes `deny`, including MCP filesystem tools. Exact new-file writes of task contracts and READY receipts under `docs/05-production/tasks` are allowed without a prompt; other documentation writes keep today's decision, which may still be a prompt.

Consequences stated plainly: with `allowed_commands` empty and every `ask` denied, agents cannot run tests or compile under an unattended lease, so unattended lane commits carry no test or runtime evidence; that evidence comes from the owner at review. The owner may put exact command patterns in `policy.allowed_commands` (for example a Unity batch-mode test invocation) to change this. Process rule: no documentation writes while a lease is active (they make the seal fail, see `DEBT-003`).

## Command recognition

The hook first requires the raw command (not the stripped one) to satisfy `command.isascii() and command.isprintable()`, then `re.fullmatch` against exactly these forms. No tokenizing, no env or path prefixes, no extra arguments:

| Action | Pattern |
|---|---|
| Activate | `python scripts/activate_lease\.py docs/05-production/tasks/(?!.*\.\.)[A-Z0-9][A-Z0-9._-]{2,80}\.md --owner-policy( --hours [0-9]{1,2}(\.[0-9])?)?` |
| Seal | `python scripts/seal_implementation\.py` |
| Commit lane work | `python scripts/agent_commit\.py` |
| Commit task documents | `python scripts/agent_commit\.py --task-docs` |

`owner_policy.py` and `agent_commit.py` join the script names that `forbidden()` blocks in any other form. `git add`, `commit`, `push`, `merge`, `tag`, `rebase`, `reset --hard`, `clean`, and history rewriting stay forbidden for agents; only these scripts commit. The commit subject is not on the command line: it comes from a `commit_subject` field in the task contract's front matter, checked at activation (charset `[A-Za-z0-9 .,:/()_-]`, up to 72 characters, no `Co-Authored-By`, `Generated with`, or trailer-looking text, case-insensitive) and so bound by the READY hash.

## `scripts/agent_commit.py` (new, controlled)

Common rules: absolute path to `git`; environment scrubbed (`GIT_DIR`, `GIT_INDEX_FILE`, `GIT_AUTHOR_*`, `GIT_COMMITTER_*`, `PYTHON*` removed); the current branch must be exactly `agent/work`, which the owner creates once (the script never creates a branch); HEAD must equal the lease base commit; the index must start empty; staging uses `git --literal-pathspecs add --pathspec-from-file=- --pathspec-file-nul`; every staged mode must be `100644` (no symlinks or gitlinks); commit with `--no-verify -c core.hooksPath=<empty controlled directory> -c core.fsmonitor=false --message=<subject>`, the owner's configured identity, and no `--amend`, `-a`, `--allow-empty`, or `--author`; the lease is then marked `COMMITTED` so a second run refuses.

- **Lane commit** (no argument): requires a `SEALED` owner-policy lease and recomputes the seal digest with a sealed-lease verifier (below). It stages exactly the sealed `changed_paths`, each inside a lane and outside every deny entry, plus one new ledger file. It rejects any modified or deleted tracked file under `docs/`.
- **Task-document commit** (`--task-docs`): no lease. It stages only new, untracked files matching the anchored regexes `docs/05-production/tasks/TASK-[A-Z0-9._-]+\.md` and `docs/05-production/tasks/READY-TASK-[A-Z0-9._-]+\.md` (no `ACCEPT-*`, no evidence packs, no other path, no `:`), after validating the contract's front matter: valid `rigor`, empty `allowed_commands`, `commit_subject`, `approval_mode: hash`, receipt present with a matching hash, `approved_by` drawn from `policy.reviewer_ids` (never the owner's name), reviewer different from author, paths inside a lane. If any other untracked file exists the whole run refuses. It runs on the same branch and counts against the daily cap. This is where an agent effectively approves its own contract; it is procedural, and the owner sees it at merge.
- **No unattended `ACCEPTED`.** Agents never commit `ACCEPT-*` receipts or evidence packs. Lane work stays `IMPLEMENTED`; the owner's merge review is the acceptance gate, and the owner commits any acceptance receipt.
- **Lease states.** `activate_lease.py` must accept `COMMITTED` next to `SEALED` as an archivable prior state, or every second lease would need the owner's terminal. Patch B adds a test that reactivates after a commit.
- **Sealed-lease verifier.** `load_lease` gets an `allow_sealed` parameter (not a copy). It requires the lease's recorded policy hash to equal the current policy file's hash, verifies `implementation_seal_sha256`, and requires the commit within `max_lease_hours` of the seal.
- **Ledger:** one new file per commit, `docs/07-evidence/agent-ledger/<seal-sha>.json`, with lease id, policy hash, seal hash, changed paths, and the hash of the previous ledger file (a chain).
- **Volume caps:** `max_unmerged_commits` and `max_unmerged_paths` counted against `main`; the script refuses beyond them so the merge review stays possible.

## Checks at activation (policy mode)

- The policy file exists in the agent worktree, parses against the schema, and `expires_at` is explicitly `null` or in the future.
- `allowed_commands` in the task contract must be empty, or a subset of `policy.allowed_commands` (default none).
- `rigor` is exactly one of `R0`..`R4` (missing is refused) and at most `min(lane.max_rigor, effective_cap)`; `effective_cap` is `R1` until the D4 sandbox is accepted and enforced.
- Path grammar: each `allowed_paths` entry is a literal path or a literal prefix with a trailing `/**`. Activation checks the literal prefix per path segment, casefolded, against the lane. Deny lists are enforced on concrete paths at write, seal, and commit (a glob comparison at activation is undecidable and is not attempted). No `:` in any path (NTFS alternate data streams).
- Hours at most `max_lease_hours`; `max_changed_paths`, `max_total_bytes`, and `max_leases_per_day` (a counter written by the controlled script).
- Task contract, receipt, and every controlled file are committed and unmodified; the branch is `agent/work`; the rest as today.

The lease records `authority: owner-policy`, the policy id, and the SHA-256 of the policy file.

## Lane policy (proposed)

```json
{
  "schema": 1,
  "policy_id": "OWNER-POLICY-1",
  "issued_at": "<ISO 8601>",
  "expires_at": null,
  "max_lease_hours": 8,
  "required_branch": "agent/work",
  "max_changed_paths": 40,
  "max_total_bytes": 2000000,
  "max_leases_per_day": 12,
  "max_unmerged_commits": 20,
  "max_unmerged_paths": 200,
  "allowed_commands": [],
  "reviewer_ids": ["<independent reviewer id>"],
  "deny_paths": ["**/Editor/**", "Assets/Plugins/**", "Packages/**", "ProjectSettings/**", "**/*.asmdef", "**/*.asmref", "**/*.dll", "**/*.rsp", "**/.git*", ".ai-governance/**", ".claude/hooks/**", ".claude/settings.json", ".claude/rules/security.md", ".claude/rules/architecture.md", ".claude/rules/testing.md", ".claude/rules/documentation.md", "scripts/**", ".github/**"],
  "lanes": [
    {"name": "prototype", "allowed_paths": ["Assets/_Prototype/**", "Assets/_Prototype.meta"], "max_rigor": "R1", "extensions": [".cs", ".meta", ".prefab", ".unity", ".asset", ".mat", ".shader", ".png", ".json", ".txt"]},
    {"name": "game", "allowed_paths": ["Assets/Game/**", "Assets/Game.meta"], "max_rigor": "R2", "extensions": [".cs", ".meta", ".prefab", ".unity", ".asset", ".mat", ".shader", ".png", ".json", ".txt"]},
    {"name": "engine-rules", "allowed_paths": [".claude/rules/unity.md", ".claude/rules/assets.md", ".claude/rules/multiplayer.md", ".claude/rules/unreal.md"], "max_rigor": "R1", "extensions": [".md"]}
  ]
}
```

`**/*.asmdef` is denied, so the owner pre-creates each lane's assembly definition once (as part of `UNITY-SETUP-001`) and it stays immutable. The owner edits this policy before use; anything left out is not authorized.

## Seal-time checks on lane files

Every changed file's extension is in its lane's list; no nested `.gitignore` or `.gitattributes`; no ignored file exists inside a lane (`git status --ignored`); every `.meta` GUID is unique across the project; and `.cs` files pass an allowlist scan: only `using` of `System`, `System.Collections`, `System.Collections.Generic`, `System.Linq`, and `UnityEngine*` namespaces; rejected tokens include `\u` escapes, `extern`, `unsafe`, `#if`, `Type.GetType`, `Activator`, `Marshal`, `System.IO`, `System.Net`, `Environment`, `Process.`, `Reflection`, `GetMethod`, `GetType`, `Expressions`, `PlayerPrefs`, `Application.`, `UnityEngine.Networking`, `UnityEngine.Windows`, `UnityEditor`, `InitializeOnLoad`, and `DllImport`. The scan is a speed bump, not a sandbox: it can be evaded, for example by reflection that needs no `using`. Persistence code that needs `System.IO` needs the owner, which matches the rigor model (R3).

## Accepted risks

- **Code that runs on the owner's machine.** Reduced by the separate worktree (nothing runs until the owner merges and opens it), the extension and deny lists, and the scan; not removed. Read the diff on `agent/work` before merging, and before opening Unity on it. The rigor cap does not reduce this risk (rigor is agent-declared).
- **Self-approval of task contracts.** `--task-docs` lets an agent commit its own contract and receipt. Safeguards: a different reviewer agent, caps, and the owner's merge review. ADR-001 PR4 asks for technical separation; same-model independence stays a known gap.
- **Engine rule files persist.** Only engine-specific rule files are in the lane, the four safety and process rule files are denied, and the worktree keeps changes out of the owner's tree until merge.
- **Indefinite and unsigned policy.** Authority lasts until the owner deletes the policy file; nothing binds it to a repository or time. Restoring the file from a backup would restore the authority; keep the agent worktree out of synced or shared folders. Suggested, not enforced: re-read the policy monthly.
- **Policy authenticity rests on the write guard,** like the lease today; see above.
- **R2** is capped at R1 until `SPIKE-SANDBOX-001` selects and enforces isolation (ADR-001 D4).

## Files to change

Two patches, each with the applier integrity controls from `DEBT-FIX-001` (committed directory, hash pinned out of band, `git diff` read after applying) and tests run in a scratch copy.

- **Patch A, inert without a policy:** `common.py` (policy loading, sealed-lease verifier via `load_lease(allow_sealed=...)`, casefolded project-root path matching, controlled-path additions, forbidden script names), `govern_shell.py`, `govern_write.py`, `govern_mcp.py` (recognition and `ask` to `deny`), `.gitignore`.
- **Patch B:** `activate_lease.py` (policy mode, `COMMITTED` prior state) and `seal_implementation.py` (policy mode, seal-time checks), new `scripts/agent_commit.py`, new human-run `scripts/owner_policy.py` (template, verify, revoke), `tests/governance_attack_corpus.json`, `scripts/validate_os.py`.

## Tests required

Missing, malformed, and expired policy; every command form with quote, smart-quote, env-prefix, path-prefix, trailing-newline, and non-ASCII variants; a path outside every lane, matching a concrete deny (`Assets/Game/Editor/x.cs`, `.asmdef`, `.dll`, nested `.gitignore`, `file:stream`); rigor missing, wrong, or above the cap; non-empty `allowed_commands`; commit subject violations; a dirty or non-empty index; a branch other than `agent/work`; HEAD not equal to the lease base; staged symlinks and gitlinks; ignored files in a lane; each forbidden `.cs` token and escape; duplicate `.meta` GUIDs; modified tracked docs during a lane commit; caps; a second commit run on the same lease; reactivation after a commit; the untracked-draft sweep (`--task-docs` with another untracked file); a docs edit during a lease making the seal fail; an owner-policy seal on a human-authority lease; policy deletion as revocation; `--task-docs` with tampered front matter or an `approved_by` naming the owner.

## Bootstrap order

1. Commit `DEBT-FIX-001` (its five files are dirty controlled files and block activation until committed).
2. Draft Patch A and Patch B; independent review for each (a signed R4 READY is optional now that no key is otherwise needed; the decisive control is the owner reading `git diff` after applying, plus the hash pin).
3. One owner session: apply, read `git diff`, run validators, commit; create the `agent/work` branch and the worktree; merge the patched files into it; write the policy with `scripts/owner_policy.py` in the agent worktree.
4. After that, routine work on the listed lanes needs no terminal until the policy file is deleted.
