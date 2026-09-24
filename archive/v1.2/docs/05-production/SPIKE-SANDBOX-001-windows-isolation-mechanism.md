# SPIKE-SANDBOX-001 — Which Windows-native OS-level isolation mechanism should the V2.0 Worktree/Sandbox Manager use for local R2+ execution (D4)?

Status: `PROPOSED`

## Uncertainty to reduce

Which of the two remaining candidate mechanisms — Windows Sandbox, or Docker's Hyper-V isolated containers (Docker Desktop's default WSL2 backend was already excluded in [ADR-001](../04-decisions/ADR-001-v2-product-and-threat-specification.md) / V2-01 rev.2 §4, since it contradicts the WSL2 non-scope decision D1) — can the V2.0 controller realistically automate for per-task ephemeral isolation during **local** Windows-native execution, satisfying D4's mandatory OS-level isolation requirement for rigor tier R2 and above.

## Decision blocked by this uncertainty

Phase V2-04 (Worktree/Sandbox Manager) cannot begin implementation design until one mechanism, or a documented fallback pairing, is selected.

## Time/resource box

This spike: desk research only (Microsoft Learn documentation + existing community tooling), no code written, single research pass. A follow-up **hands-on** feasibility test (actually launching each mechanism on this machine, measuring startup/reset latency, scripting a full create→run→destroy cycle) is explicitly out of scope here and should be its own bounded follow-up spike before V2-04 commits.

## Method and environment

Web research against Microsoft Learn documentation and existing open-source automation tooling for both candidates. No live test was run against this machine's actual Windows edition or firmware virtualization settings — see Unknown below.

## Success, failure, and stop criteria

**Success:** identify a mechanism that is (a) scriptable/automatable by an external controller process without a human at the keyboard, (b) supports natural per-task ephemeral reset, (c) provides genuine OS-level isolation (not just process isolation), (d) works on the D1-assumed target (Windows 10/11 Pro or Enterprise, native).
**Failure/stop:** if neither candidate is confirmed automatable without unacceptable operational complexity, escalate back to D4 in ADR-001 for renegotiation rather than silently picking one.

## Disposable outputs

None — documentation-only spike, no throwaway code.

## Findings: facts vs inference

`[FACT]` Windows Sandbox is configured via `.wsb` XML files, launchable from the command line by invoking the file path; supports a `<LogonCommand>` to auto-run a script/app at startup; supports `<Networking>` (can be disabled entirely) and `<MappedFolders>` (explicit, host-controlled read/write folder sharing). ([Microsoft Learn](https://learn.microsoft.com/en-us/windows/security/application-security/application-isolation/windows-sandbox/windows-sandbox-configure-using-wsb-file))

`[FACT]` Windows Sandbox requires Windows 10 build 18342+ or Windows 11, **Pro or Enterprise edition** (not available on Home), with virtualization support enabled in firmware. Each launch is a fresh, fully disposable environment — closing it discards all state, giving natural per-task ephemerality with no manual cleanup step.

`[FACT]` Existing open-source PowerShell tooling (`jdhitsolutions/WindowsSandboxTools`, `flexxxxer/WindowsSandbox-ConfigsAndScripts`) already wraps Windows Sandbox launch/configuration/teardown — a controller adapter would be adapting an existing automation pattern, not building one from zero.

`[FACT]` Docker's Hyper-V isolation mode (`docker run --isolation=hyperv`) runs each container inside its own lightweight VM with its own kernel — genuine hardware-level isolation, stronger than plain process isolation. This is the **default** isolation mode for Windows containers on Windows 10/11 Pro/Enterprise specifically (Windows Server instead defaults to process isolation, which would **not** satisfy D4's OS-level bar unless `--isolation=hyperv` is explicitly forced). ([Microsoft Learn](https://learn.microsoft.com/en-us/virtualization/windowscontainers/manage-containers/hyperv-container))

`[FACT]` Hyper-V isolated containers additionally require the outer hypervisor to expose virtualization extensions to the guest whenever the host itself is a VM (nested virtualization) — commonly disabled or unavailable on shared cloud VM hosts. This independently reinforces (rather than merely assumes) the D3/D4 CI-incompatibility finding already recorded in ADR-001 (GitHub Actions' own Windows runners cannot support this class of mechanism).

`[INFERENCE]` Windows Sandbox appears to have a meaningfully simpler automation surface for an external controller — a single XML config plus a logon command, no separate container runtime/daemon dependency — versus Hyper-V isolated Docker containers, which require Docker Engine or Docker Desktop installed and running as a prerequisite, plus Windows base container images version-matched to the host build (a separately documented compatibility constraint). This is drawn from the shape of the tooling found during research, not a measured benchmark.

`[INFERENCE]` Startup/reset latency was not directly measured for either mechanism on this machine. Community sources describe Windows Sandbox startup as typically a few seconds; Hyper-V container startup is generally described as slower than process-isolated containers but faster than a full VM boot. Neither figure is independently verified here and neither should be treated as a committed performance budget.

`[UNKNOWN]` Whether this specific machine's Windows edition (Home vs. Pro/Enterprise) and firmware virtualization settings actually support either mechanism was **not checked** in this desk-research pass — this is a concrete, cheap next check before committing further.

## Decision recommendation and remaining uncertainty

Recommend **Windows Sandbox** as the primary candidate for D4's local R2+ isolation mechanism: simpler automation surface, no extra daemon/runtime dependency, natural ephemerality by design, and existing open-source tooling to adapt rather than build from scratch. Recommend **Hyper-V isolated Docker containers** be kept as a documented fallback — useful specifically if the controller later needs container-image-level reproducibility (e.g. pinning an exact toolchain/OS build per task) that Windows Sandbox's simpler model does not offer.

This recommendation does **not** close D4. It narrows the required follow-up from "three candidates" (per V2-01 rev.2 §4) to one concrete next check: confirm this machine's Windows edition and virtualization support, then hand-test one real `.wsb`-launched, scripted, torn-down cycle — before V2-04 commits to this mechanism.

Spike code is not production code unless separately reviewed and implemented under a task contract.
