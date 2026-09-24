# Prototype Lane

Status: `PROPOSED` — depends on `ADR-002` (option D) being accepted by the owner. Not in force.

## Purpose

Let the owner run fast, throwaway Unity experiments under the existing lease mechanism without a new task contract, spec, or acceptance receipt for every experiment. It keeps the fail-closed behavior: no lease, no writes.

## Scope

- One lane path, `Assets/_Prototype/**`, plus its folder meta file `Assets/_Prototype.meta`. Unity writes that meta file next to the folder, outside the pattern, so it must be listed in `allowed_paths` or the seal rejects it.
- Exists only after the Unity project is created (`UNITY-SETUP-001`).
- One standing task contract, `TASK-PROTO-LANE-001` (to be drafted, rigor R1, reviewed once by an independent reviewer). Its `allowed_paths` are exactly the two entries above. The owner activates a lease from it per work session; `activate_lease.py` allows up to 24 hours (`--hours`, lines 85-89).

## Rules inside the lane

1. No system specification, no per-experiment READY review, no acceptance receipt. Lane results are never `ACCEPTED`, and never count as evidence for an accepted system.
2. Lane code lives in its own assembly definition. Nothing outside the lane may reference it; dependencies point only from the lane outward.
3. Promotion to production is a new task through the normal process. The experiment is input to that task (like a spike report), not code to copy in.
4. Each session states one hypothesis and one stop condition in its commit message.
5. While a lease is active, nothing outside `allowed_paths` may change, including documents. `seal_implementation.py:43-45` rejects the seal otherwise (see `DEBT-003`). Notes go in the commit message; documents are updated after the seal.
6. Networking, persistence, and economy experiments are allowed as throwaway only. Findings are recorded as hypotheses; no data format from the lane becomes a save or wire format.

## Known risks (to verify in a real Unity project)

- Opening the Unity editor can rewrite files outside the lane (`Packages/packages-lock.json`, `ProjectSettings/**`, other `.meta` files). Any such change makes the seal fail. Verify how often this happens; if it is common, either restrict what the editor may write or list specific files, which needs its own review.
- The owner still runs activation, the seal, and the commit each session until `ADR-002` option B exists.
- For a pure idea test, a separate Unity project outside this repository stays the fastest route.

## Measurement

Record per session: start and end, number of owner terminal actions, whether the seal succeeded. This feeds the `ADR-002` validation baseline (`TASK-UNITY-RULES-001` is the comparison point).

## Open items

- Draft `TASK-PROTO-LANE-001` and review it.
- Choose the lane assembly-definition name.
- Decide whether `.claude/rules/unity.md` needs a lane-specific note.
