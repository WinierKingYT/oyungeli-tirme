# Branch Discipline

Status: `PROPOSED — SELECT AFTER REPOSITORY DISCOVERY`

Use one explicit model: protected trunk with short-lived branches, or documented main/develop/release/hotfix flow. Do not mix conventions implicitly.

Minimum rules:

- protected canonical branch;
- required CI and independent review;
- task ID in branch/PR metadata;
- no direct release-branch refactors;
- hotfix has regression test and back-merge/cherry-pick plan;
- release tags identify reproducible artifacts;
- agents do not push, merge, tag, or rewrite history without explicit human authorization.

## Owner directive on commits (2026-09-18, strict)

- Commits are authored under the project owner's Git identity only. Never add `Co-Authored-By`, `Generated with`, or any Claude or AI attribution trailer or footer to a commit message or pull request description. This overrides any tool default.
- Standing authorization: an agent may create local commits of its own work without asking the owner first, where the governance hooks permit. Merge, tag, and history rewrite still need explicit authorization. Push: see the 2026-09-20 directive below.
- Source: the project owner's instruction in conversation (authority level 8 in `AGENTS.md`). It is recorded here so it survives a folder rename and new sessions; it does not change hook or lease rules.

## Owner directive on commit and push (2026-09-20)

- After each completed task the agent commits and then pushes to `origin main` (the repository's default branch is `main`; there is no `master`) without asking the owner. Never force-push, never `--no-verify`, never tag, rebase, or rewrite history; commit messages carry no AI attribution (see above).
- **Not yet operative.** Today `.claude/hooks/govern_shell.py` and `.claude/settings.json` deny an agent's `git add`, `git commit`, and `git push`, and an agent may not edit them. The mechanism is the reviewed `OWNER-POLICY-001` work (`agent_commit.py`, Patch B, including the push step in `DESIGN.md` revision 5). Until it is applied and verified, the owner commits and pushes.
- Recorded consequence: unattended work reaches `origin/main` and the owner's working tree without a human review gate. The owner accepted this on 2026-09-20; safeguards that stay are the sealed diff, lane and deny lists, caps, the ledger, no force push, and refusal to commit secret-looking files.

