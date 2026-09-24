# AI Game Development OS v1.2 — Package Report

Date: 2026-09-16

Disposition: `BOOTSTRAP PACKAGE VALIDATED / NOT PROJECT-RATIFIED`

## Verified

- Python sources compile in-memory.
- Shared settings parse and enforce Plan Mode with auto/bypass modes disabled.
- All expected agents and skills have valid required frontmatter.
- Production writes fail without a lease.
- Documentation writes require confirmation outside a lease.
- Governance paths remain denied during active leases.
- Scope-limited writes work only with a schema-3 lease bound to the exact Git root, base HEAD, and branch.
- Task-contract and READY-receipt drift both invalidate the lease.
- Internal hook exceptions exit with blocking code 2.
- Pipe, redirection, compound commands, substitutions, nested shells, destructive suffixes, Git invocation variants, Git output/external execution, sensitive reads, and outside-root reads have adversarial checks.
- A full interactive lease activation was exercised against a task-hash-bound independent review receipt and clean committed base.
- Dirty-worktree activation and branch-drift reuse are rejected.
- MCP calls are deny-by-default without a lease and exact-name policy is validated.
- Live project/user/local settings and skill changes are blocked through `ConfigChange`.
- Human-only sealing rejects out-of-scope changed paths, hashes tracked/untracked changes, closes authority, and blocks post-seal writes.
- Valid R4 SSH approvals activate; tampered receipts are rejected.
- The adversarial suite passes 169 checks.
- Audit output is valid JSON Lines.
- ZIP integrity is tested after packaging.

## Environment-dependent verification

`python scripts/doctor.py --require-claude` must run after installation at the actual Git repository root. The packaging environment is neither the target Git root nor equipped with the Claude Code executable, so strict runtime integration cannot be certified here. Non-strict doctor and the full mechanical/adversarial validator pass.

## Explicit limitations

- Claude Code documents hook startup failure and timeout as normally non-blocking; OS sandboxing and permission discipline remain required.
- Hooks do not govern edits made outside Claude Code.
- A human can still approve a dangerous one-time command; R0–R3 reviewer names are not cryptographic identities.
- An SSH signature proves control of an allowed key, not reviewer competence or evidence truth.
- External programs can modify the worktree after sealing; acceptance must recheck repository state and hashes.
- Command classification is conservative, not a formal shell interpreter.
- Game-specific correctness, architecture, engine version, plugins, build, runtime, platforms, and performance remain unknown until repository discovery.

This package must not be described as a completed or accepted game architecture.
