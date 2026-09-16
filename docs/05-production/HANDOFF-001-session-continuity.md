# HANDOFF-001 — Session continuity (v1.2 audit → V2.0 direction → first leasable task, blocked on DEBT-001)

## Authority and current lifecycle state

- This repository is **AI Game Development OS v1.2** — a governance/control-plane package for AI-assisted game development (hooks, lease/seal scripts, agent/skill definitions, heavy `docs/`), **not** a game codebase. No game discovery has started (`docs/00-project/PROJECT-STATUS.md`: discovery `NOT_STARTED`).
- [ADR-001](../04-decisions/ADR-001-v2-product-and-threat-specification.md) — `ACCEPTED`. Adopts a V2.0 controller-based architecture direction. Resolves D1 (Windows native host), D2 (no engine adapter yet — controller MVP first), D3 (local+CI), D4 (R2+ requires OS-level isolation), D6 (GitHub-coupled MVP, provider-neutral interface only), D7 (remote MCP off), D9 (evidence retention follows existing local/git-ignored precedent). Leaves D5 (Claude Code/Sonnet version policy), D8 (key custody/reviewer identity), D10 (usability budget) explicitly open.
- [SYS-V2-SCHEMAS-001](../03-systems/SYS-V2-SCHEMAS-001.md) — `SPECIFIED`, independently reviewed `READY_FOR_IMPLEMENTATION` (fresh-context `code-reviewer` agent, 2026-09-16).
- [TASK-SCHEMA-001](tasks/TASK-SCHEMA-001.md) — `READY_FOR_IMPLEMENTATION` as a contract (4 independent review rounds, 7 findings, all resolved; receipt: [READY-TASK-SCHEMA-001](tasks/READY-TASK-SCHEMA-001.md)). **Contract-complete but its lease cannot currently be activated on this machine** — see Known limitations below. This is the smallest next real (non-doc) artifact: one JSON Schema file + fixtures under `schemas/v2/`.

## What changed and why

Starting point: user asked to verify the v1.2 baseline, extract its architecture, hard-review its vulnerabilities, and produce a V2 plan — no code, no baseline changes, stop for human decisions. Sequence actually executed, in order:

1. Verified v1.2 baseline (`python scripts/validate_os.py` → 169 checks/114 md files/8 agents/9 skills, matches packaged claims).
2. Three parallel Explore agents extracted the full architecture (control-plane hooks, doc/lifecycle authority model, agent/skill/rule/CI layer).
3. Hard security review found 13 findings (critical: this repo was not a Git repository at all, so no v1.2 lease could ever activate).
4. User shared an external "AI Game Development OS 2.0" development brief; it was reconciled against the earlier plan (its own V2-00/V2-01 phase definitions were adopted as authoritative).
5. Wrote a V2-01 product/threat spec, independently reviewed by 3 fresh-context agents (unanimous `FIX_FIRST`), revised to rev.2 addressing all 9 findings.
6. User approved the direction → recorded as **ADR-001**.
7. Ran the Git bring-up (user did `git init`/commit/push to `github.com/WinierKingYT/oyungeli-tirme`, `main` branch, **public** repo).
8. Recorded `DEBT-001`/`RISK-006` (a real bug found live: `scripts/doctor.py --require-claude` false-fails on this repo's non-ASCII path).
9. Researched a sandbox-mechanism spike ([SPIKE-SANDBOX-001](SPIKE-SANDBOX-001-windows-isolation-mechanism.md)) recommending Windows Sandbox over Hyper-V isolated containers, pending a hands-on test not yet done.
10. Drafted and pushed `SYS-V2-SCHEMAS-001` + `TASK-SCHEMA-001` through a real independent-review cycle (4 rounds, using fresh Agent-tool dispatches as genuine independent reviewers) to `READY_FOR_IMPLEMENTATION`.
11. **Discovered DEBT-001 is far worse than first scoped**: a real `python scripts/activate_lease.py docs/05-production/tasks/TASK-SCHEMA-001.md` attempt failed with `ERROR: AI Game Development OS must be installed at the Git repository root` — the same non-ASCII-path encoding bug also lives in `.claude/hooks/common.py:git_state()`, which `activate_lease.py` and every governed hook's `load_lease()` depend on. **This is a hard block on activating any lease at all on this machine**, not a cosmetic warning. Escalated to P0 in `TECH-DEBT.md`/`RISK-REGISTER.md`.
12. Confirmed structurally, by direct attempt (not just inspection), that no Claude Code agent — this session or any future one — can ever fix this: `.claude/hooks/common.py` and `scripts/doctor.py` are both in `CONTROLLED_PATHS` (`.claude/hooks/common.py:16-30`), and `git commit`/`git push` are hard-denied to any agent (`govern_shell.py`'s `forbidden()`), regardless of lease state or Claude Code's own permission mode (plan/auto/bypass — confirmed via Claude Code's own `/auto-mode-setup` wizard independently flagging the same paths as `soft_deny` after reading this repo).

## Canonical revision and environment

- Repo: `github.com/WinierKingYT/oyungeli-tirme`, branch `main`. Last known local commit before this handoff: `8050ead` (`docs: escalate DEBT-001/RISK-006 to P0`), with further uncommitted doc edits made after it (DEBT-001 waiver-note correction, HANDOFF file itself) — **check `git log -1` and `git status` first thing in the new session, do not assume this list is still current.**
- Host: Windows 11 Pro, build 10.0.26200, native (not WSL). Python 3.13.7. Repo path contains non-ASCII characters (`oyungeliştirme`) — this is the direct cause of DEBT-001.
- Model/tooling: Claude Sonnet 5 (`claude-sonnet-5`) via Claude Code desktop app. Exact Claude Code CLI version was not captured (`claude --version` is not in `govern_shell.py`'s safe-command allowlist).

## How to build, test, and reproduce

- `python scripts/validate_os.py` — safe to run anytime, no lease needed, currently `PASS` (169 checks).
- `python scripts/doctor.py --require-claude` — safe to run, currently `FAIL` (`"package must be installed at the Git repository root"` — this is DEBT-001, a known false positive, not a real misconfiguration).
- `python scripts/task_digest.py <path>` — safe, used to bind READY receipts to exact task-contract bytes. **Any edit to a task contract after computing its digest invalidates the receipt — recompute and update the receipt every time**, this bit the author twice in this session.
- `python scripts/activate_lease.py docs/05-production/tasks/TASK-SCHEMA-001.md` — **currently fails** with the DEBT-001 error. Human-only; no agent can run this (name-matched hard block in `govern_shell.py`).

## Evidence and acceptance disposition

- Independent reviews used genuine fresh-context `Agent` tool dispatches (`code-reviewer`, `qa-reviewer`, `documentation-auditor` subagent types already registered in this repo's `.claude/agents/`), not self-review. This is disclosed as same-underlying-model independence (matching this project's own admitted limit: `PACKAGE-REPORT.md`, "R0–R3 reviewer names are not cryptographic identities"), not cryptographic/human independence.
- All disposition history (FIX_FIRST rounds and final READY_FOR_IMPLEMENTATION) is preserved in [READY-TASK-SCHEMA-001.md](tasks/READY-TASK-SCHEMA-001.md)'s Findings table — read it before assuming the task is trivially clean; it went through real, substantive corrections including the author (this agent) twice getting the DEBT-001 severity wrong before a reviewer caught it.

## Known limitations, open risks, and forbidden assumptions

- **DEBT-001/RISK-006 (P0, blocking)**: `scripts/doctor.py:57-61` and `.claude/hooks/common.py:git_state()`/`git_worktree_clean()` (~lines 137-177) all call `subprocess.run(..., text=True, ...)` without `encoding="utf-8"`, breaking git-root path comparison on this repo's non-ASCII Windows path. **No agent can ever fix this** (`CONTROLLED_PATHS`). Two untried remediation paths, neither verified working yet:
  1. Human runs with `PYTHONUTF8=1` set (e.g. `PYTHONUTF8=1 python scripts/activate_lease.py ...` in the user's own terminal — the governance hook only gates Claude's own Bash calls, not the user's terminal) — **not yet confirmed to work**, only theorized (Python UTF-8 mode changes `locale.getpreferredencoding()` to `utf-8`, which `subprocess.run(text=True)` uses by default).
  2. Human manually adds `encoding="utf-8"` to the ~4 `subprocess.run` calls across the two files, then commits.
  Whichever the user reports worked (or didn't), record the actual result and stop guessing further.
- **Never assume `git commit`, `git push`, or `scripts/activate_lease.py`/`deactivate_lease.py`/`seal_implementation.py` can be run by any Claude Code agent in this repo** — this was empirically re-confirmed multiple times this session (exact tool-call attempts, not just documentation reading), and holds regardless of plan/auto/bypass permission mode.
- **Never assume `.claude/hooks/**`, `.claude/settings.json`, or any file listed in `CONTROLLED_PATHS` (`.claude/hooks/common.py:16-30`) can be edited by an agent** — `govern_write.py` denies this outright, unconditionally.
- The user could not exit plan mode / switch permission modes via the app UI this session ("Permission mode couldn't be changed, try again") — unresolved app-level issue, not something either side could fix from inside the conversation. Does not appear to block ordinary doc edits in practice (they kept succeeding regardless of the mode reminder).
- Do not repeat the mistake made twice this session: don't let a task contract self-declare a waiver on a documented tech-debt trigger it is itself the exact match for — surface it as `ASSUMPTION_REQUIRES_APPROVAL` for the human, don't resolve it unilaterally (an independent reviewer caught this both times; see `READY-TASK-SCHEMA-001.md` F1/F2).
- `SPIKE-SANDBOX-001`'s recommendation (Windows Sandbox over Hyper-V containers) is desk-research only — no hands-on test of this machine's actual edition/virtualization support has been done.

## Next permitted action and required gate

1. **Immediate, blocking**: get DEBT-001 resolved by one of the two paths above, confirmed by an actual `python scripts/doctor.py --require-claude` → `RESULT: PASS` and a successful `python scripts/activate_lease.py docs/05-production/tasks/TASK-SCHEMA-001.md` run (human-only, both).
2. **Once leased**: an agent may write exactly `schemas/v2/task-contract.schema.json` and the four fixture files under `schemas/v2/fixtures/`, per `TASK-SCHEMA-001.md`'s `allowed_paths` — nothing else, per its `allowed_paths`/non-scope sections.
3. **After that task seals and is accepted**: the next backlog items are `D5`/`D8`/`D10` (still open per ADR-001), `SPIKE-SANDBOX-001`'s hands-on test, and the remaining V2-02 schemas (capability, state-transition, evidence-manifest, seal/attestation, review/acceptance receipt) — each needs its own task contract and independent review, following the exact pattern in `TASK-SCHEMA-001.md`/`READY-TASK-SCHEMA-001.md`.
4. A new session should start by reading this file, then `docs/00-project/PROJECT-STATUS.md`, `git log -1`, and `git status` — in that order — per this project's own `docs/00-project/CONTEXT-FRESHNESS.md` rule (conversation summaries are navigation aids, not current authority).
