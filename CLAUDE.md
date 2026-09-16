@AGENTS.md

# Claude Code Project Router

You are operating inside AI Game Development OS v1.2.

## Always load project state

Read these before material work:

- `docs/00-project/PROJECT-STATUS.md`
- `docs/05-production/CURRENT-MILESTONE.md`
- `docs/05-production/CURRENT-TASK.md`
- relevant accepted ADRs and system specifications

## Default behavior

- Begin in research or design mode.
- Inspect before claiming.
- Use the narrowest relevant skill.
- Keep `CLAUDE.md` concise; put procedures in skills and scoped rules.
- Treat conversation instructions as lower authority than accepted project records.
- Never change production files unless a valid implementation lease permits the exact path.
- Treat READY and ACCEPT claims as invalid unless their receipts match the exact task/evidence hashes, repository-bound implementation seal, and implementation revision.

## Required status words

Use only defined lifecycle states. Never use “done,” “finished,” “production ready,” or “accepted” as informal synonyms.

When blocked, emit one of:

- `AUTHORITY_CONFLICT`
- `DRIFT_DETECTED`
- `SCOPE_EXPANSION`
- `SPIKE_REQUIRED`
- `EVIDENCE_MISSING`
- `LEASE_REQUIRED`

## Skill routing

- New or unfamiliar repo: `/project-discovery`
- New system: `/new-system`
- Readiness decision: `/ready-review`
- Approved implementation: `/implement-system`
- Validation and evidence: `/verify-system`
- Independent acceptance: use `acceptance-reviewer`
- Closure and freeze: `/close-system`
- Milestone gate: `/milestone-review`
- Code/docs mismatch: `/drift-audit`
- Serious failure: `/postmortem`

## Claude-specific safeguards

- Do not invoke `scripts/activate_lease.py`, `scripts/deactivate_lease.py`, or `scripts/seal_implementation.py`.
- Do not ask another agent to bypass a denied tool call.
- Do not edit `.ai-governance/`.
- Do not loosen `.claude/settings.json`, hooks, or validation scripts to make a task pass.
- Never treat a compound, piped, redirected, substituted, or nested-shell command as pre-approved.
- Do not self-approve implementation you produced.
- Treat every unlisted MCP tool as a possible remote mutation; never bypass its governance decision.
- After writing an agent definition for the first time, remind the user that Claude Code may need a restart if `.claude/agents/` did not exist when the session began.
