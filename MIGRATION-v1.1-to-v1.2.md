# Migration from v1.1 to v1.2

1. Deactivate and discard every schema-2 lease; v1.2 accepts schema 3 only.
2. Commit or stash all existing work before activating a new lease.
3. Merge `.claude/settings.json`, hooks, scripts, `.ai-governance/mcp-policy.json`, templates, and CI changes without overwriting project-specific policy blindly.
4. Add `approval_mode: hash` to R0–R3 task contracts and READY receipts.
5. Configure a reviewed public-key allowlist before using R4; R4 now requires `ssh-signature`.
6. Review every MCP server/tool and add only exact, demonstrably read-only names to `allow_without_lease`.
7. Run `python scripts/validate_os.py`, then `python scripts/doctor.py --require-claude` on the real development machine.

Do not copy an old lease or acceptance claim forward. Create fresh repository-bound authority and evidence.
