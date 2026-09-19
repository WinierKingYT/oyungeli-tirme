# OWNER-POLICY-001 — Owner-signed standing policy (design)

Status: `PROPOSED` design, not implemented. Implements option B of `ADR-002`. Nothing here changes behavior. It needs an independent review, then patch proposals, then one owner session at a terminal.

## Goal

The owner should not need a terminal for routine lease activation, sealing, or commits. Authority must still come from the owner (ADR-001 PR1), never from an agent's own action.

## Owner decisions recorded (2026-09-19)

| Decision | Owner's choice | Note |
|---|---|---|
| Lanes agents may lease themselves | Prototype lane, production Unity code, rule and settings files | See "Lane risks"; the owner can drop any lane at signing time |
| Highest rigor approved without the owner | R2 | Conflicts with ADR-001 D4 until the sandbox spike is accepted; enforced as R1 until then |
| Signing key | Passphrase-protected SSH key | Never loaded into an agent, never stored in the repository |
| Policy lifetime | No expiry (indefinite) | Recommended alternative was 7 days. Accepted with mandatory revocation, per-lease expiry, and audit (below) |

## Trust chain

1. The owner signs a policy file once with `ssh-keygen -Y sign -n aigdo-owner-policy` using a dedicated, passphrase-protected key (not the everyday key, not in `ssh-agent`).
2. The policy and its signature live in `.ai-governance/` (`owner-policy.json`, `owner-policy.json.sig`) with the public key in `.ai-governance/owner-allowed-signers`. `.ai-governance/**` is a `CONTROLLED_PATH`: agents cannot write it, and shell access to it is forbidden. Files are local and gitignored.
3. Verification runs `ssh-keygen -Y verify -n aigdo-owner-policy` against the allowed-signers file on every use. The signature is defense in depth: even if a write guard failed, a forged policy still cannot verify without the passphrase.
4. Revocation is deletion of the policy file (or its signature). Everything below fails closed without a valid policy.

## What agents may do under a valid policy

Only these exact command forms are allowed; anything else keeps today's behavior (deny or ask).

| Action | Exact form | Conditions |
|---|---|---|
| Activate | `python scripts/activate_lease.py docs/05-production/tasks/<TASK>.md --owner-policy [--hours N]` | Task and READY receipt pass every existing check plus the policy checks below; no typed prompts; no `--inherit-dirty`; hours at most `max_lease_hours` |
| Seal | `python scripts/seal_implementation.py` | Only when the lease file shows `authority: owner-policy` and the policy still verifies |
| Stage | `git add -- <path>...` | Every path inside the lease's `allowed_paths` or `docs/**`; no wildcards, no `-A`, no `.` |
| Commit | `git commit -m "<message>"` (repeatable `-m`) | Only after a sealed or active owner-policy lease; no other flags (no `-a`, `--amend`, `--no-verify`, `--allow-empty`, `--author`); message must not contain `Co-Authored-By`, `Generated with`, or AI attribution (owner directive in `BRANCH-DISCIPLINE.md`) |

`git push`, `merge`, `tag`, `rebase`, `reset --hard`, `clean`, and history rewriting stay forbidden for agents. The owner pushes.

## Policy checks at activation

- The policy signature verifies, the policy is not expired (`expires_at: null` means indefinite, and must be written explicitly), and its `serial` is not lower than any recorded minimum.
- Every path in the task's `allowed_paths` is covered by exactly one lane and matches none of the lane's or the policy's `deny_paths`.
- The task's `rigor` is at most `min(lane.max_rigor, effective_cap)`. `effective_cap` is `R1` until the D4 sandbox mechanism is accepted and enforced; then it may be `R2`. R3 and R4 always need the owner.
- The task contract is unchanged since the independent READY receipt (existing hash check), the reviewer differs from the author (existing check), and the worktree has no dirty file outside `allowed_paths` (existing rule; dirty controlled files never accepted).

The lease records `authority: owner-policy`, the policy id, and the SHA-256 of the policy and signature, so every action can be traced to the exact signed authority.

## Proposed policy content

```json
{
  "schema": 1,
  "policy_id": "OWNER-POLICY-1",
  "serial": 1,
  "issued_at": "<ISO 8601>",
  "expires_at": null,
  "max_lease_hours": 8,
  "deny_paths": ["**/Editor/**", "Assets/Plugins/**", "Packages/**", "ProjectSettings/**", ".ai-governance/**", ".claude/hooks/**", ".claude/settings.json", "scripts/**", ".github/**"],
  "lanes": [
    {"name": "prototype", "allowed_paths": ["Assets/_Prototype/**", "Assets/_Prototype.meta"], "max_rigor": "R1", "commit": true},
    {"name": "game", "allowed_paths": ["Assets/Game/**", "Assets/Game.meta"], "max_rigor": "R2", "commit": true},
    {"name": "rules", "allowed_paths": [".claude/rules/**"], "max_rigor": "R1", "commit": true}
  ]
}
```

The owner edits this before signing; anything left out is not authorized.

## Files to change (patch proposal comes after review)

- `.claude/hooks/common.py`: policy verification helper; add the new script to `CONTROLLED_PATHS`.
- `.claude/hooks/govern_shell.py`: exact-form exceptions ahead of the existing denials; commit-message and path checks.
- `scripts/activate_lease.py`: `--owner-policy` mode.
- `scripts/seal_implementation.py`: refuse agent-style sealing unless the lease is owner-policy (the human path is unchanged).
- New `scripts/owner_policy.py` (human-run): create a template, sign, verify, revoke. Added to `CONTROLLED_PATHS`.
- `tests/governance_attack_corpus.json` and `scripts/validate_os.py`: adversarial cases (below). Depends on `DEBT-FIX-001` being applied first.

## Tests required

A forged or tampered policy signature; an expired policy; a missing policy; a policy replayed with a lower serial; a task path outside every lane or inside `deny_paths`; rigor above the cap; a `git commit` with a forbidden trailer, `--amend`, `-a`, or `--no-verify`; `git add .` or a path outside the lease; `git push`; compound and quoted variants of every allowed form; an agent-run command that names the scripts in any other form; revocation by deleting the file; an owner-policy seal on a human-authority lease.

## Lane risks (owner should read before signing)

- **Unity code that runs on your machine.** Unity executes editor scripts and `[InitializeOnLoad]` code when the project opens, and Play Mode runs game code. An injected or mistaken change in `Assets/Game/**` can run with your rights. `**/Editor/**`, `Assets/Plugins/**`, and `Packages/**` are denied, but runtime C# is not, so read the diff before opening Unity or pressing Play after unattended work.
- **The rules lane is the riskiest.** Files in `.claude/rules/**` become instructions for later agent sessions; a bad rule persists. Recommended: remove this lane from the policy, or keep it with `commit: false` so you see the diff before it is recorded. Your choice at signing.
- **Same-model independence.** The author, the reviewers, and the sealing agent share one model family; independence stays procedural, and unattended work is checked only by tests, the lane limits, and your later review.
- **Indefinite policy.** No expiry means the authority stays until you delete it. Mitigations: per-lease expiry (at most `max_lease_hours`, itself at most 24 h by the existing script), revocation by deletion, the audit log with the policy id, and a suggested habit of re-reading the policy monthly. This is not enforced.
- **R2.** ADR-001 D4 requires OS-level isolation for R2 and above once a mechanism is chosen; none is chosen yet (`SPIKE-SANDBOX-001`). The verifier therefore caps at R1 until that decision is accepted.

## One-time owner session (unavoidable)

1. Apply `DEBT-FIX-001`, then the `OWNER-POLICY-001` patch (after review), read `git diff`, run the validators.
2. Create the dedicated key, place the public key in `.ai-governance/owner-allowed-signers`, edit and sign the policy with `scripts/owner_policy.py`.
3. Commit the patched files. After that, routine work needs no terminal until you revoke or change the policy.

## Open questions

- Should the commit form also allow `git status`-only follow-ups (already read-only) and `git commit` of `docs/**` outside any lease? (Proposed: docs commits need a sealed or active owner-policy lease too, keeping one rule.)
- Where to keep the minimum-serial record (a controlled file under `.ai-governance/`).
- Whether the audit log needs tamper evidence beyond being agent-unwritable.
