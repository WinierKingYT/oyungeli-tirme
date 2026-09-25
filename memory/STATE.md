# Project State

Updated: 2026-09-25 · By: agent

## Now
- v3 is in place (F0 done); hardening on branch `v3-hardening` (not pushed).

## Last session
- guard.py now checks each command segment, so text that only mentions a blocked command passes; smoke tests 20/20 locally (`tests/hooks_smoke.py`).
- Root `.gitattributes` (LF), v3 README, `game/IDENTITY.md` filled from ship-game inputs.
- CI `.github/workflows/hooks.yml`: Windows + Ubuntu, Python 3.12/3.13, extra run from a non-ASCII path. Not yet run on GitHub.
- Honest naming: hooks are a seatbelt; review levels self → fresh context → other model → measurement → owner.

## Next
1. Owner: merge `v3-hardening` into `main` and push; check the `hooks` workflow is green on GitHub.
2. Owner: confirm (owner?) items in `game/IDENTITY.md`; answer `game/JUDGMENT-GAPS.md`.
3. F1: create Unity 6 LTS project at an ASCII path, install official Unity plugin + bridge, copy v3 folders, compile `docs/v3/unity-tools/`.
4. Baseline eval (plain Claude + bridge) on `evals/TASKS.md` before using v3 skills.

## Open questions for the owner
- Unity project path and version; which bridge (official first).
- References and twist in IDENTITY.

## Watch out
- `core.autocrlf false` is set locally; `.gitattributes` now pins LF.
- `logs/` belongs to another tool and is ignored.
