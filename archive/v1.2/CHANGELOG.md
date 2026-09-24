# Changelog

## 1.2.0 — Repository-bound attestation

- Upgraded implementation authority to schema 3 and bound it to a clean Git root, exact base HEAD, and branch.
- Added a human-only implementation seal that rejects out-of-scope changed paths, hashes tracked/untracked changes, and closes agent write authority.
- Added deny-by-default governance for all MCP tool calls with exact-name allowlists.
- Added live `ConfigChange` blocking for user/project/local settings and skills.
- Added mandatory SSH-signed READY receipts for R4 tasks and tamper tests.
- Added a versioned adversarial attack corpus and end-to-end activation/sealing tests.
- Added v1.1 migration and repository-attestation documentation.

## 1.1.0 — Control-plane hardening

- Changed policy-hook unexpected failures from non-blocking process errors to explicit `exit 2` fail-closed behavior.
- Added adversarial shell parsing for redirection, pipes, compound commands, substitutions, nested shells, absolute-path Git, Git global options, destructive operations, and publish/deploy commands.
- Added task-author separation and SHA-256-bound independent READY review receipts.
- Added evidence-digest-bound acceptance receipts.
- Added JSONL governance audit trail.
- Disabled Claude Code auto and bypass permission modes at project scope.
- Added `doctor.py`, artifact/task digest utilities, and GitHub Actions validation.
- Added security threat model, context freshness, and migration documentation.

## 1.0.0 — Initial bootstrap

- Added layered instructions, rules, agents, skills, documentation authority, templates, implementation leases, hooks, and ship-game discovery baseline.
