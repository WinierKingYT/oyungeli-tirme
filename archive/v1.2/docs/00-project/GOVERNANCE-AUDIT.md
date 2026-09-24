# Governance Audit Trail

Every governed write, shell, and MCP `PreToolUse` decision is appended to `.ai-governance/audit.log` as JSON Lines with timestamp, tool, subject, decision, reason, and active task ID. The file is local and ignored by Git because commands, paths, and tool inputs may contain sensitive project details.

The audit trail helps reconstruct attempted writes and shell actions. It is not proof that implementation is correct, that a command completed, or that no external tool changed the repository. Acceptance still requires repository diff and evidence-pack review.
