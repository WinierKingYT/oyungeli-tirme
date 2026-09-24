---
name: unity-test
description: Compile-checks a Unity project and runs EditMode/PlayMode tests through the bridge or batchmode, judging results from logs and NUnit XML, and lists visual verification images to review. Use after changing C# code, before calling a task complete, or when the user asks to test — "testleri çalıştır", "derleniyor mu", "compile", "run tests".
---

# /unity-test

## 1. Fast compile (rung 2, ~3 s)
Before running tests, check compilation:
- Editor open + MCP connected → read compile status / console via MCP.
- Otherwise → `dotnet build` on the Unity-generated `Assembly-CSharp.csproj` (or the feature assembly's `.csproj`). Use the system .NET SDK or the one bundled with the Editor (`<Editor>/Data/DotNetSdk/dotnet`). Limitation: files created outside the Editor are missing until Unity regenerates project files.
Compile errors stop here: fix first.

## 2. Choose the test runner
- **Editor open and MCP connected** → the MCP test tool (platform + optional assembly/filter). Batchmode cannot open a project the Editor already holds.
- **Editor closed** → batchmode:
```
"<Editor>/Unity" -batchmode -nographics -projectPath "<Project>" -runTests -testPlatform EditMode -testResults "<Project>/Logs/editmode.xml" -logFile "<Project>/Logs/editmode.log"
```
`-testPlatform PlayMode` for play mode; narrow with `-testFilter "A;B;!Skip"` or `-assemblyNames "Game.Tests.EditMode"`. Editor path: `ProjectSettings/ProjectVersion.txt` + Unity Hub install folder.

Batchmode pitfalls:
- **Never combine `-quit` with `-runTests`** (Unity exits before tests run).
- `Temp/UnityLockfile` present → the Editor (or a crashed one) owns the project; do not delete it while a Unity process is running.
- The first batchmode run after closing the Editor may reimport the Library (minutes) — say so instead of assuming a hang.

## 3. Judge by evidence, not exit codes
- Tests: parse NUnit XML `<test-run total passed failed skipped>` and failed `test-case` elements (`message`, `stack-trace`).
- Log failure markers override any exit code: `error CS`, `Scripts have compiler errors`, `Aborting batchmode due to failure`, exception stacks. Success marker for batchmode: `Exiting batchmode successfully`.
- `VisualVerification` tests produce screenshots, not pass/fail: list their image paths and review each image against its `[Description]`.

## 4. Scope
- Default: compile + EditMode tests for assemblies touched in this task.
- Before calling a feature complete: all EditMode, the feature's PlayMode tests, and its visual verification tests reviewed.

## 5. Report
First two lines always: the command/tool used, then the verdict with numbers.
```
Ran: MCP run_tests EditMode (Game.Tests.EditMode)
Result: 41 passed, 1 failed, 0 skipped (3.1 s) · compile clean
FAIL Game.Tests.CargoBalanceTests.Tilt_HeavyOnLeft_TiltsLeft
  Expected: 5.0 ± 0.1  But was: -5.0   at CargoBalance.cs:37
Visual: 2 images to review → Logs/Screenshots/Deck_Tilt_*.png
```
Show at most 5 failures in full; count the rest.

## 6. Then
- Fix failures caused by this change. A failing test is never "pre-existing" by assumption: check `git stash`/previous run evidence, otherwise fix or report with output.
- Never weaken an assertion to get green.
- A test that passes on rerun is flaky: report it as a defect with both outputs.

Sources of ideas: m4bwav/unity-agent (offline compile, log markers, batchmode pitfalls), nowsprinting/unity-coding-skills (visual verification category).
