# How v3 skills are built and improved

## Rules for every skill
- Only write what Claude does not already know: project conventions, thresholds, procedures, gotchas.
- `description` is a routing rule in third person: what it does + when to use it + phrases the owner actually says (Turkish and English). ≤ 1024 characters.
- SKILL.md body short (target < 150 lines, hard limit 500). Details in `reference/*.md`, linked directly from SKILL.md (one level deep). Reference files > 100 lines start with a contents list.
- Freedom matches fragility: design and review → principles and heuristics; file formats, Unity YAML, batchmode → exact commands/scripts.
- Deterministic work (lint, capture, diff, layout validation) is a script or Editor tool, not generated code.
- Unity safety rules live once in `CLAUDE.md`; skills do not repeat them.
- One term per concept across all skills (e.g. always "card", "bridge", "review set").

## Evaluation first
1. Run the task without the skill (baseline); write down what went wrong.
2. Write 3 scenarios that hit those gaps (`evals/TASKS.md`) and trigger tests (`evals/triggers/<skill>.md`: 3 should-fire, 3 decoys, 1 action case proven by a tool call).
3. Write the minimum skill text that fixes the gaps.
4. Run the scenarios; compare with baseline using `eval-scorer`; keep only what improves the score.

## Claude A / Claude B
- Session A (with the owner) edits the skill.
- Session B (fresh, skill installed) does a real task.
- Watch B: which files it reads, what it skips, where it goes wrong. Bring observations back to A. A file never read is unnecessary or badly linked; a file always read belongs in SKILL.md.

## Models
Test critic and craft skills with the strongest model and with a faster one; the faster one must still follow the procedure. Critics run on the strongest model; scorers and summarizers on a faster one.

## Cost and cache
- Keep always-loaded text stable (CLAUDE.md, IDENTITY): frequent edits invalidate the prompt cache.
- Changing content (STATE) is injected by the session hook, not written into CLAUDE.md.
- Register MCP servers per project; only the bridge you use.
