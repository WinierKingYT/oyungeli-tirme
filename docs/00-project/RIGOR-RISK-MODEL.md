# Rigor and Risk Model

## Rigor levels

| Level | Use | Minimum controls |
|---|---|---|
| R0 | Documentation typo or cosmetic, easily reversed | Review + visual check |
| R1 | Local low-risk behavior | Bounded task + automated test |
| R2 | Integrated gameplay or shared asset | System spec + integration/runtime evidence |
| R3 | Multiplayer, save, economy, performance-critical, public contract | ADR where needed + adversarial tests + independent review |
| R4 | Irreversible/high-cost architecture, release, migration, security | Alternatives + spike + rollback + multiple evidence classes + human gate |

R4 ready approval additionally requires an SSH-signed receipt verified against a committed public-key allowlist. A hash-only reviewer name is insufficient for R4 identity assurance.

## Reversibility

- `EASY`: isolated change with no persistent or external impact.
- `MODERATE`: migration or coordinated changes required.
- `EXPENSIVE`: save schema, skeleton, multiplayer architecture, world partition, core physics, public contract, or platform commitment.

Risk equals impact × likelihood × detectability × reversibility cost. High uncertainty raises rigor even when estimated impact is low.
