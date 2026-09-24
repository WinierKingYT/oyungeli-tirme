---
name: craft-game-feel
description: Diagnoses and improves how actions feel (responsiveness, impact, rhythm, clarity, payoff) with a /14 rubric, then applies feedback techniques and verifies them in the running game. Use when an action feels flat, floaty, weak, sluggish, unresponsive, or the user asks for juice — "his kötü", "tepkisiz", "cansız", "vuruş hissi", "daha tatmin edici olsun".
---

# Game feel craft

Needs the game running (Play Mode via the bridge, a recording, or timed notes). Code alone is *inferred*.

## Diagnose (before changing anything)
0. Target feel in one sentence with the shared vocabulary (snappy, weighty, crunchy, hollow, mushy, flowing, telegraphed, readable, charged, lurching, floaty…).
1. Responsiveness: input → first visible change; > 100 ms reads sluggish.
2. Feedback chain per beat — anticipation, action, impact, resolution — and which channels fire (visual, audio, camera, UI/haptic). Missing audio at impact reads *hollow*; missing anticipation reads *lurching*.
3. Rhythm: dead time > 0.5 s; tension/release over 30–60 s.
4. Clarity, 5. payoff proportional to importance, 6. overload.
Score 0/1/2 each: Responsiveness · Clarity · Impact · Rhythm · Payoff · Dead time · Overload → **ALIVE** 12–14 · **BREATHING** 10–11 · **FLAT** 8–9 · **MUDDY** 5–7 · **DEAD** < 5. Findings = problem + channel + timing, no solutions yet.

## Improve
Tier events (small/medium/large) with fixed channel sets; layer several brief responses within ~100 ms; everything decays back; visuals separate from simulation; eased motion. Techniques and starting numbers: [reference/techniques.md](reference/techniques.md). Put all values in a feedback ScriptableObject.

## Verify
Trigger repeatedly via the bridge; confirm each channel fires, decays, and never blocks input; capture the impact frame; re-score and report the delta; ask the owner (`/feedback`).

## Output
`Feel: <mechanic> · Target: … · Score: x/14 → y/14 · Blockers: … · Changes: … · Evidence: <paths>` + status line.
