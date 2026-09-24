# Migration from v1.0 to v1.1

v1.1 changes the lease schema from 1 to 2. A v1.0 active lease is intentionally invalid under v1.1.

## Safe migration

1. Finish or stop current agent work.
2. Run `python scripts/deactivate_lease.py` using the v1.0 control plane.
3. Preserve project-specific documents, task contracts, agents, rules, and settings customizations.
4. Replace the core control files: `.claude/hooks/`, `scripts/`, `.claude/settings.json`, root contracts, templates, CI workflow, and security/process standards.
5. Add `authored_by` and `ready_review_receipt` to every task contract.
6. Re-run independent readiness review and create a task-hash-bound receipt; old prose-only READY decisions cannot be migrated automatically.
7. Run `python scripts/doctor.py --require-claude` in the actual Claude Code environment.
8. Confirm `/context`, Plan Mode, disabled auto/bypass modes, and both PreToolUse hooks.
9. Activate a fresh v1.1 lease only after the doctor and CI are green.

Do not overwrite project-specific authority records blindly. Resolve conflicts according to the project authority model and record the migration as a change request when the OS is already ratified.
