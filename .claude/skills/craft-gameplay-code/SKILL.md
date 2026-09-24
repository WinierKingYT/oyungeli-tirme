---
name: craft-gameplay-code
description: Structures and verifies Unity C# gameplay code — script roles, pure C# rules with thin MonoBehaviours, ScriptableObject config, events, debug views, test design, and the verification ladder. Use when writing, changing, or fixing gameplay scripts, systems, or mechanics in Unity — "kodla", "implement et", "mekaniği yaz", "bug düzelt", "script".
---

# Gameplay code craft (Unity)

Implement the system card's minimum playable version, not more. Unity API specifics come from the official Unity plugin skills; Unity safety gotchas are in `CLAUDE.md`.

## 1. Roles before code
Write a role table for the feature, one justification line per script:
| Role | For | Not for |
|---|---|---|
| Pure C# rules/service | rules, math, state transitions | lifecycle, scene access |
| ScriptableObject config | tunables, definitions | runtime state |
| MonoBehaviour bridge | lifecycle, input, physics callbacks, applying results | rules |
| Presenter/controller | UI/input → rule calls | owning state |
| State machine | mode switching | storage |
| Installer/bootstrap | wiring at scene start | gameplay |

## 2. Structure
- Rules take injected data and emit `event Action<…>` or return values; MonoBehaviours stay thin.
- Every tunable from the card lives in config with `[Range]`/`[Min]` and `[Tooltip("raising this makes…")]`.
- Cross-system talk via events or event channels; explicit scene wiring, no `Find*` chains.
- Content (items, routes, tables) as data brought in by importer/ScriptableObject.
- Feedback visuals are separate from the simulated body; time effects use unscaled time.
- Each system has a debug view (gizmo, overlay, or editor window).

## 3. Verification ladder
Choose the lowest rung that can catch the mistake; show evidence that lives outside the conversation.
| Rung | Catches | How |
|---|---|---|
| 1 | logic, math, state | EditMode tests on pure rules (seconds) |
| 2 | compile errors | bridge compile status or offline `dotnet build` of the generated `.csproj` (~3 s) |
| 3 | serialization, Editor APIs, Play Mode | `/unity-test` |
| 4 | runtime look and logs | bridge: console, screenshot, debug view |
| 5 | feel and UX | owner plays → `/playtest` |
Never "done" with console errors; a failing test is not "pre-existing" without evidence.

Test design rules and visual verification tests: [reference/testing.md](reference/testing.md).

## Anti-patterns
Everything a MonoBehaviour · runtime state in ScriptableObjects · magic numbers · hidden singletons · `Find` chains · shaking the physics body · "compiles/tests pass" reported as done for a visible change without rung 4 evidence.
