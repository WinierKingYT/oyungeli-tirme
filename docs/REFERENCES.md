# Tooling References

These references support the Claude Code integration. Project engineering standards remain owned by this repository.

- Claude Code memory and `CLAUDE.md`: https://code.claude.com/docs/en/memory
- Claude Code subagents: https://code.claude.com/docs/en/sub-agents
- Claude Code skills: https://code.claude.com/docs/en/skills
- Claude Code hooks: https://code.claude.com/docs/en/hooks
- Claude Code permissions: https://code.claude.com/docs/en/permissions
- Claude Code settings: https://code.claude.com/docs/en/settings

Validated against the official pages on 2026-09-16. The v1.2 threat model incorporates the documented behavior that most hook startup failures, timeouts, invalid JSON, and ordinary nonzero exits are non-blocking, while `PreToolUse` exit code 2 blocks. It also uses the documented `mcp__<server>__<tool>` matcher model and `ConfigChange` blocking semantics; enterprise `policy_settings` changes remain non-blockable by project hooks. Revalidate integration syntax and failure semantics when upgrading Claude Code.
