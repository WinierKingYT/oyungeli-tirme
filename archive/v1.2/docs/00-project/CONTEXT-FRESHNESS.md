# Context Freshness Standard

At session start, after context compaction, after branch/worktree change, and before any lifecycle transition, reread:

1. `PROJECT-STATUS.md`;
2. `CURRENT-MILESTONE.md`;
3. `CURRENT-TASK.md`;
4. active lease, exact task/review hashes, base Git HEAD, and branch when implementation is intended;
5. relevant accepted ADRs and system specs;
6. repository status and revision.

Conversation summaries, auto memory, old review reports, and prior agent messages are navigation aids, not current authority.

If the current revision, task hash, evidence digest, or branch differs from the accepted record, report `DRIFT_DETECTED` and stop the affected claim.
