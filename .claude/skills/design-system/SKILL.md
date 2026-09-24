---
name: design-system
description: Runs the workflow for designing a new gameplay system or changing one — clarify, three different approaches, independent scoring, detailed card, critique, revise, record, hand-off with playtest hypotheses. Use when the user asks to design a system or mechanic or asks how something should work — "sistem tasarla", "şu mekanik nasıl olmalı", "yeni özellik fikri", "design a system".
---

# /design-system

Load `craft-system-design`. Mode: **Quick** by default (steps 1, 4, 5-self, 7, 8); **Full** for new systems, cross-system changes, systems listed under IDENTITY "Critical systems", or when the owner asks.

Checklist to copy and tick:
```
- [ ] 1 Clarify
- [ ] 2 Three approaches
- [ ] 3 Independent scoring
- [ ] 4 Card + analyses
- [ ] 5 Critique
- [ ] 6 Revise
- [ ] 7 Record
- [ ] 8 Hand-off
```
1. **Clarify** goal, pillar, constraints, touched systems. Missing critical fact → ≤ 3 short questions, then proceed on stated assumptions.
2. **Three approaches** that differ in core verb or resource model, each: a play moment + loop in 3–5 steps.
3. **Independent scoring:** send the three (anonymized A/B/C) with IDENTITY and `evals/RUBRIC.md` to `design-critic`; it scores and recommends. You pick or merge with a stated reason.
4. **Card + analyses** per `craft-system-design`.
5. **Critique:** Full → `design-critic` on the card; Quick → run its checklist yourself. Decide accept / reject-with-reason per finding.
6. **Revise**; if the core changes, back to 3 once at most.
7. **Record** decision and rejected alternatives in `memory/DECISIONS.md`; update `memory/STATE.md`.
8. **Hand-off** (Turkish): design in 5 lines, rejected alternatives, top 3 risks as playtest hypotheses, open questions; ask 👍/👎 + reason → `/feedback`.

No implementation code here unless asked. Status line at the end.
