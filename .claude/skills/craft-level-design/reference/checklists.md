# Level design — checklists and limits

## Contents
- Guidance · Flow · Spaces · Anti-patterns · Using screenshots well · Self-review table

## Guidance
- [ ] Goal or next landmark visible from every decision point
- [ ] Brightest / highest-contrast element is on or points to the intended path
- [ ] Optional paths visually secondary but discoverable
- [ ] No two exits look equally important unless the choice is intended

## Flow
- [ ] Intensity table realized; no two peaks without rest; never flat-high
- [ ] No stretch longer than METRICS "max time without a decision"
- [ ] Backtracking < 20% of the critical path, or a shortcut exists
- [ ] Gated progression checked in unlock order; no softlock
- [ ] Failure respawn close to the challenge

## Spaces
- [ ] Widths fit player count (co-op widths if co-op)
- [ ] Required traversal ≤ ~70% of max ability; challenge ≤ ~95%; barriers ≥ ~110%
- [ ] No unintended unreachable NavMesh islands
- [ ] No floating/intersecting geometry; every walkable surface has a collider

## Anti-patterns
- Corridor → room → corridor with no choice or landmark
- Guidance by UI arrows only
- Mechanic introduced under pressure
- Decor hiding walkable edges; identical-looking branches
- Geometry by eye instead of metrics; detailing before the layout has been played

## Using screenshots well
Vision models are good at obvious glitches and describing salience; weak at fine placement, subtle clipping, and before/after comparison, and they raise false alarms.
- Ask one concrete question per image, always with the card's intended read.
- Measure placement, overlap, reachability, and size in code (lint, NavMesh, raycast), not from images.
- Compare before/after with the pixel-diff tool; use vision only to describe the changed regions.
- Treat visual findings as *inferred-visual* until the owner or a measurement confirms them.

## Self-review table
| Moment | Intended read (card) | Observed read | Measured facts | Fix |
|---|---|---|---|---|
