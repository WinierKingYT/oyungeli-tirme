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
- Standing authorization: an agent may create local commits of its own work without asking the owner first, where the governance hooks permit. Push, merge, tag, and history rewrite still need explicit authorization.
- Source: the project owner's instruction in conversation (authority level 8 in `AGENTS.md`). It is recorded here so it survives a folder rename and new sessions; it does not change hook or lease rules.

