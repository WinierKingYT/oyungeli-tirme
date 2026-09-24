---
name: craft-level-design
description: Designs, blocks out, and reviews game levels in Unity with metric-driven layout, pacing as data, guidance, and screenshot-based self-review. Use when the user asks to design, build, block out, fix, or review a level, map, area, port, island, room, or route — "level tasarla", "bölüm yap", "haritayı düzelt", "blockout", "oyuncu nereye gideceğini bilmiyor".
---

# Level design craft

Read first: `game/IDENTITY.md`, `game/METRICS.md`, the level card, system cards of the mechanics used.

## Principles
- A level has one job (what the player learns, proves, or feels). No job, no level.
- Teach → test → combine → master; never test before teaching.
- Pacing is data: intensity 0–1 per beat, rising overall, a dip after every peak, never flat-high.
- The player always knows the next goal. Guidance strength: light > motion > contrast/color > lines > landmarks > sound > UI.
- Reveal the goal before the path; loops and shortcuts beat backtracking.
- Metrics are law: required traversal ≤ ~70% of max ability, challenge ≤ ~95%.
- Blockout until it plays well; art never fixes layout.

## Procedure
1. **Plan on paper:** fill the level card (job, teach/test, intensity table, gates, key moments, scene contract).
2. **Scout** the scene and prefabs read-only; reuse before creating.
3. **Plan → validate → apply:** write `reviews/<date>/<level>/layout.json` (objects, positions, sizes, purpose) → check every size/gap against METRICS → apply through the bridge in one batch under `_Env/Blockout`.
4. **Verify by measurement (code, not eyes):** `Tools/Review/Lint Scene`, bake NavMesh, `Tools/Review/Measure Critical Path`; check gated areas in unlock order.
5. **Guidance pass:** blockout lights and landmark silhouettes.
6. **Look:** `Tools/Review/Capture Review Set`. For each image ask one focused question with the card beside it ("What is the most salient element? Is the dock exit visible?"). Label answers *inferred-visual*.
7. **Critique:** `level-critic` (fresh context) with card, images, lint/path reports.
8. **Revise** once, recapture, compare before/after with the image diff tool — not by eye.
9. **Record:** card status, `memory/DECISIONS.md`, `memory/STATE.md`, owner summary with images.

Details: [reference/checklists.md](reference/checklists.md) (guidance, flow, spaces, anti-patterns, vision limits).

Output ends with the status line from `_quality-preamble`.
