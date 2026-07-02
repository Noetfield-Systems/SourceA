# DEPRECATED — do not deploy dedicated cron

**Status:** deprecated (W-LBA-002 · 2026-07-02)  
**Law:** Signal Factory 24/7 trigger is **piggyback-only** via `sourcea-loop-specialist-tick-v1` `scheduled()` hook.

## Do not

- Deploy this worker with `[triggers] crons`
- Add a registry entry pointing at this wrangler cron

## Sole SF schedule trigger

- **Registry:** `SA-T-signal-factory-piggyback` in `data/trigger-registry-v1.json`
- **Live probe:** `cloud/workers/loop-specialist-tick-v1/src/index.js` → `runSignalFactoryTick`
- **Cron:** `*/15 * * * *` on loop-specialist worker only

Manual HTTP `/tick` on this worker may remain for founder debugging only — not a scheduled trigger.
