# Game feel — techniques and starting numbers

All numbers are starting points; tune in the feedback config.

| Technique | How | Starting values | Pitfall |
|---|---|---|---|
| Layering | Several small responses fire together at impact: sound, particles, flash, shake, hit-stop, knockback, tween | ~5–8 responses within ~100 ms for large events; 2–3 for small | Adding everything everywhere → noise |
| Tiers | small / medium / large events each get a fixed channel set | Shake and hit-stop only for large | Inconsistent feedback across the game |
| Screen shake (trauma) | trauma 0–1 added per event; offset/rotation ∝ trauma²; smooth noise (Perlin); decay each frame | decay ~1.0–1.5 per second; max offset small (a few cm world / a few px) | Random per-frame jitter reads as static; shaking the body breaks physics |
| Hit-stop | Briefly lower `Time.timeScale`, restore with unscaled/real-time timer | ~0.05–0.1 s at scale ~0.05 | Scaled timers never resume |
| Squash & stretch / pop | Instant deformation, then overshoot ease back | 1.2–1.3× on one axis, inverse on the other; back to 1 in ~0.15–0.2 s | Linear tween looks robotic |
| Easing | Ease-out to settle, back/overshoot to pop | — | Linear everywhere |
| Weight (heavy objects, ships, cargo) | Longer anticipation, slower settle, low-frequency sound, small camera dip instead of sharp shake | settle 0.3–0.6 s | Snappy feedback on heavy things feels cheap |
| Accessibility | Setting to reduce shake/flash; no juice on routine repeated actions | — | Fatigue, motion sickness |

## Unity notes
- Camera shake on a camera child or Cinemachine impulse, never on the Rigidbody.
- Hit-stop restore with `WaitForSecondsRealtime` or `Time.unscaledDeltaTime`.
- Keep feedback in presenter/visual components; the rule layer only raises events (`OnCargoDropped`, `OnHullHit`).
