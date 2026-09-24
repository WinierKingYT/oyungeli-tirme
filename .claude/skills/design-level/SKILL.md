---
name: design-level
description: Runs the workflow for designing and blocking out a level with the Unity bridge — three structurally different concepts, independent scoring, planned and validated blockout, measurement, screenshot review, critique, revise. Use when the user asks for a new level, area, port, island, or route, or to rework one — "yeni bölüm", "liman tasarla", "ada haritası", "level yap".
---

# /design-level

Load `craft-level-design`. Mode: **Quick** (adjust an existing area: steps 1, 4–7, 9) or **Full** (new level: all).

```
- [ ] 1 Clarify   - [ ] 2 Three concepts   - [ ] 3 Independent scoring
- [ ] 4 Blockout (plan → validate → apply)  - [ ] 5 Measure   - [ ] 6 Capture + look
- [ ] 7 Critique  - [ ] 8 Revise + diff    - [ ] 9 Record + hand-off
```
1. **Clarify** job, place in progression, mechanics taught/tested, target duration, player count (≤ 3 questions).
2. **Three concepts** that differ in structure (linear with vistas / hub and spokes / loop with shortcut …): node graph of areas and connections with a landmark each, intensity sequence, signature moment.
3. **Independent scoring** by `level-critic` (anonymized) with RUBRIC + navigation clarity + pacing; pick or merge with a reason.
4. **Blockout** via `craft-level-design` procedure (layout.json → METRICS validation → one batch).
5. **Measure:** lint, NavMesh critical path, gates in unlock order.
6. **Capture + look:** review set; one focused question per image with the card.
7. **Critique:** `level-critic` with images, lint.json, path.json.
8. **Revise** once; recapture; before/after with the image diff tool.
9. **Record + hand-off** (Turkish): images, intensity sequence, what to try when playing, open questions; 👍/👎 → `/feedback`.

No art, lighting polish, or props before the owner has played the blockout. Status line at the end.
