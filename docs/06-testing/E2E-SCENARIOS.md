# Whole-Game E2E Scenarios

## VOYAGE-E2E-001 — Baseline cooperative voyage

Host session -> join required clients -> select cargo -> load and secure -> depart -> navigate -> engine failure -> communicate -> repair -> weather event -> cargo damage -> arrive -> unload/sell -> save -> exit -> reload -> verify economy and cargo state.

Status: `PROPOSED / NOT IMPLEMENTED`

## Required variants

- client disconnects while carrying cargo;
- host migration or explicit unsupported behavior;
- failure during save;
- island/service unavailable;
- all repair resources exhausted;
- high latency and packet loss;
- repeated voyage loop in soak test;
- no profitable mission fallback to market trade.

