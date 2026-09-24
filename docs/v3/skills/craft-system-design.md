---
name: craft-system-design
description: Provides game system design craft — loops, resources and sinks, meaningful choice, feedback loops, exploits, balance, scope — and the analyses a system card needs. Use when designing, reviewing, or changing any gameplay system such as economy, trade, cargo, repair, heat, crafting, progression, or combat rules — "sistem tasarla", "ekonomi", "denge", "bu mekanik nasıl çalışmalı".
---

# System design craft

Read `game/IDENTITY.md`, related `game/systems/*.md`, and `game/JUDGMENT-GAPS.md` first.

## Principles
- Serve a named pillar; a system that serves none is a cut candidate.
- Describe one concrete moment of play before any number.
- Meaningful choice = trade-off + visible information + felt consequence. Remove strictly dominant or dominated options.
- Loops at three scales (seconds, session, hours); touch at least two.
- Every resource has sources and sinks with rates; name caps and what happens at 0 and at cap.
- Name each feedback loop (snowball or catch-up) and why it is wanted.
- One rule that interacts with three systems beats three isolated rules.
- Failure is legible and recoverable unless IDENTITY says otherwise.
- Fun first: loop fun → clarity → performance → polish → economy detail. Smallest playable version first.
- One source per value: numbers live in their config asset; cards reference it. Conflicting values are flagged before designing further.

## Required analyses
Interaction matrix · resource flow · decision inventory (dominant option?) · exploit hunt (min-maxer, griefer, lazy player; ≥ 3) · boredom check · balance check (real data only, otherwise `NOT ASSESSED — NO DATA`) · ADD/KEEP/DEFER/CUT · twist. Formats and anti-patterns: [reference/analyses.md](reference/analyses.md).

## Output
Update `game/systems/SYS-<ID>.md` (template includes formulas with variable tables, edge cases with exact resolutions, acceptance criteria with witnesses). Append the analyses. End with minimum playable version, ranked expansions, top 3 risks written as `/playtest` hypotheses, and the status line.

Implementation follows `craft-gameplay-code` (pure C# rules + ScriptableObject config + debug view + simulation test).
