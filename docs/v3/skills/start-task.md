---
name: start-task
description: Starts a game-development task with the smallest useful context — classifies the task, loads only the relevant cards, craft skill, decisions and examples, scouts the Unity project read-only, and writes what "done" will be observed as. Use at the start of any non-trivial request — new feature, level, system, fix, tuning — "başlayalım", "şunu yap", "yeni görev".
---

# /start-task

Goal: best context with the least tokens. Load at most one craft skill and 3–4 cards.

1. **Classify** the request: `system-design | level-design | gameplay-code | game-feel | tuning | bugfix | playtest | ui | other`, plus the project stage from IDENTITY (idea / blockout / prototype / alpha / polish).
2. **Load context pack:**
   | Type | Always | Plus |
   |---|---|---|
   | system-design | `game/IDENTITY.md`, `memory/STATE.md` | related `game/systems/*`, `craft-system-design`, decisions mentioning them |
   | level-design | same | level card, `game/METRICS.md`, `craft-level-design`, system cards for mechanics used |
   | gameplay-code | `memory/STATE.md` | system card being implemented, `craft-gameplay-code` |
   | tuning | same | system card + its ScriptableObject configs |
   | bugfix | same | `craft-gameplay-code`, repro steps, console log |
   | game-feel | same | `craft-game-feel`, system card of the mechanic, feedback config |
   | playtest | same | `/playtest`, the card whose risks are being tested, previous PT for the scene |
   Every type also loads `_quality-preamble` and checks `game/JUDGMENT-GAPS.md` for open questions touching the task.
   Load `memory/EXAMPLES/` entries tagged with the same type (max 2).
3. **Scout** (read-only bridge calls, cheapest first): editor status and console, scene summary/health check, relevant hierarchy, existing scripts/prefabs/ScriptableObjects for this feature. Report what already exists; reuse before creating.
4. **Define done as observations**, e.g. "console clean; EditMode tests X pass; screenshot shows cargo tilting the deck; card updated". Write them as a checklist.
5. **Pick the workflow:** design → `/design-system` or `/design-level`; code → implement with `craft-gameplay-code` feedback loop; small tweak → quick mode.
6. At the end: update the card, `memory/STATE.md`, and give the owner a short summary in their language.
