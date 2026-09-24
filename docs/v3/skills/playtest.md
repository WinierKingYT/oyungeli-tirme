---
name: playtest
description: Prepares and digests playtests — hypothesis, build check, session timeline, observations, playability score (6 dimensions /12), hypothesis verdict, regression against the previous session, and card updates. Use when the user is about to play, has played, or shares play notes — "oynadım", "test ettim", "playtest", "oyun nasıl olmuş", "şurada takıldım".
---

# /playtest

## Before (prepare)
1. **Hypothesis.** Take it from the risks in the relevant system/level card: one sentence that this session can confirm or reject ("Players notice cargo shifting before the ship tilts dangerously"). At most two.
2. **Build check:** console clean, `/unity-test` green, `Tools/Review/Lint Scene` without errors.
3. **Evidence plan.** Best to weakest: runnable build the owner plays + screen recording → screenshots + minute-by-minute notes → notes only. Anything inferred from code alone is labelled *inferred, not observed*.
4. Turn on the debug overlay/telemetry if available; otherwise list 3 things to watch (time to first loop, where they hesitated, what they said).
5. Create `memory/PLAYTESTS/PT-<NNN>.md` from the template. Brief the owner in 3 lines (their language): what to try, what to watch, how to report (free text or voice note is fine).

## After (digest)
1. **Session timeline** from the notes/recording:
   | Time | Action | Player state (curious/engaged/lost/frustrated/satisfied) | Flag OK/⚠️/🔴 |
   Flag dead time (> 5 s with nothing to do), unclear goals, hesitation.
2. **Observations** as facts with location and severity (1–3). Keep interpretations in a separate column.
3. **Playability score** — each 0/1/2 with cited evidence from the timeline:
   | Dimension | 2 | 1 | 0 |
   |---|---|---|---|
   | Loop closure | action → reward → use/spend completes and is visible | a gate missing or unclear (reward without use, cost without source) | no complete cycle |
   | Session viability | 5+ min without friction, session has a shape | 5+ min with 1–2 rough moments | stuck or quits within 5 min |
   | Onboarding | new player knows what and why within ~90 s | understands after > 2 min or by guessing | lost after 2 min |
   | Failure recovery | clear next step after failure, no softlock | recovery slow or unclear | no failure state or dead end/softlock |
   | Retention signal | one moment that makes them want to continue (unlock, new ability, story) | hook exists but thin or far | only repetition |
   | Peak moment | a memorable instant (tension, satisfying hit, discovery, laugh) | pleasant but forgettable | tedious or numb |
   Verdict: 10–12 play-ready · 7–9 almost · 4–6 not yet · 0–3 tech demo. Judge by stage: placeholder art is normal early; a broken loop is not.
4. **Forcing questions**, each answered with evidence:
   - *Stranger test:* could someone with zero context finish the first loop? What confuses them?
   - *Opposite action:* what breaks if they skip text, ignore the tutorial, or play "wrong"?
   - *Retention cliff:* at minute 5, do they want to continue or feel obliged?
5. **Hypothesis:** VALIDATED / INVALIDATED / INCONCLUSIVE + one line of evidence. A lower score that answers the hypothesis is worth more than a higher score that does not.
6. **Regression delta:** compare each dimension with the previous PT for the same scene; flag any drop.
7. **Actions** (max 5, ranked by player impact): one sentence each, pointing to a card ("Fix the softlock at the dock ramp, then replay"). Do not implement yet.
8. Update cards' risks/open questions; record owner decisions in `memory/DECISIONS.md`; turn explicit likes/dislikes into `/feedback` examples; rewrite `memory/STATE.md` "Next".

## Rules
- Never argue with an observation; the player's experience is data.
- One player is a signal, not a verdict — mark severity and look for repetition across sessions.
- Diagnose, do not prescribe, in the observation section; fixes go only in Actions.
- Do not change METRICS or IDENTITY without the owner's explicit decision.

Sources of ideas: gstack-game `/build-playability-review` and `/playtest`.
