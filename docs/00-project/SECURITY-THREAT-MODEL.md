# Security and Control-Plane Threat Model

Status: `BOOTSTRAP — RATIFY IN REAL REPOSITORY`

## Protected assets

- production source/assets/configuration;
- project authority and lifecycle state;
- task scope and approval records;
- secrets and credentials;
- Git history, branches, releases, and deployments;
- evidence provenance.

## Threats and controls

| Threat | Primary controls | Residual limitation |
|---|---|---|
| Agent writes before approval | Plan Mode + write hook + Git-bound lease | Programs outside Claude Code do not pass through hooks |
| Agent widens its own authority | Protected governance paths + human-only activation | User can still manually alter files |
| Hook code throws | top-level fail-closed `exit 2` + adversarial probe | Interpreter failing to start is non-blocking in Claude Code |
| Shell read command writes via `>`, pipe, `&&`, `$()` | compound/operator detection; never auto-approved | One-time human approval can still authorize risk |
| Git deny-rule spelling bypass | full-command hook parses absolute Git, `-C`, `-c`, and quoted subcommands | Arbitrary custom executables remain impossible to classify perfectly |
| Fake READY claim | separate reviewer + task-hash-bound receipt + human activation | A careless human can accept fabricated review content |
| Floating acceptance | evidence digest + implementation revision receipt | External evidence links can disappear unless archived |
| Lease reused after repository drift | base HEAD + branch binding on every governed call | Human edits can still dirty the tree during a lease |
| MCP bypasses file/shell hooks | all `mcp__*` tools gated, deny-by-default exact allowlist | Human one-time approval can still authorize remote mutation |
| Settings weakened during session | `ConfigChange` blocks user/project/local/skill changes | Enterprise policy changes cannot be blocked by project hooks |
| Diff changes after implementation | human seal closes lease and hashes tracked/untracked diff | Tools outside Claude can still modify files after sealing; reviewer must recheck |
| Reviewer name is spoofed for R4 | SSH-signed ready receipt + public-key allowlist | Private-key custody and allowlist quality remain human responsibilities |
| Context loss/compaction | short root instructions + current-state reread + authority docs | Model can still misunderstand; evidence gates remain required |
| Malicious repository instructions | authority order + scoped rules + workspace trust | Opening untrusted repos without review remains dangerous |

## Critical platform limitation

Claude Code documents that a command hook which cannot start, times out, returns ordinary `exit 1`, or produces invalid output normally does not block `PreToolUse`. Therefore this package does not claim that a Python hook alone is a security sandbox.

Mitigations are layered:

1. start in Plan Mode;
2. disable auto and bypass permission modes;
3. run `python scripts/doctor.py` before work;
4. require CI validation and protected branches;
5. retain manual permission prompts for unapproved commands;
6. use OS/container sandboxing and secret isolation for high-risk work;
7. inspect `.claude/` before trusting an unfamiliar repository;
8. protect the branch and require CI to recompute validation and evidence checks.

## Human responsibility

Do not approve a command because the agent says it is safe. Review the exact command, paths, redirections, expansions, network effects, and active task scope. Hooks reduce accidental and model-driven violations; they do not replace human or operating-system security.
