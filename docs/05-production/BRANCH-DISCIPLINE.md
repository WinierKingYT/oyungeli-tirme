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

