# Controlled Autorun Laws v2

**Schema:** `controlled-autorun-laws-v2`  
**Saved at (UTC):** 2026-07-02T11:45:00Z  
**Agent skill:** `.cursor/skills/controlled-autorun/SKILL.md` (+ `references/sourcea-wiring.md`, `references/receipt-schemas.md`)  
**Owner:** SourceA Loop Specialist (standing assignment)  
**Scope:** CF cron worker · Railway FBE motor · queue batches · cycle receipts · sink invariants · heartbeats · external verification · Kaizen improvement backlog

## L1 — One reconciler

Extend `scripts/phase_reconciler_v1.py` only. Never create parallel control authority. Desired state is founder/ASF-authored; observed state is probe-backed projection only.

## L2 — Scheduled loops only

Primary scheduler: Cloudflare cron (`*/10 * * * *`) → Railway `POST /api/cloud-forge-run/auto-tick/v1`. Mac is observe/dispatch proxy only — never the motor body.

## L3 — Sink invariant every cycle

Every cycle receipt must carry `sink_invariant`. Mismatch → `BLOCKED_WITH_REASON`. Law: `supabase_count == railway_count` (or `railway_count + mac_replay_count == supabase_count` when mac replay is wired).

## L4 — External verify only

Agent fetches and local curls are **never** PASS evidence. Only the GitHub Action `.github/workflows/external-verify.yml` receipt counts. Verify timestamp within 60s of deploy invalidates the agent's own report — re-run through the external Action.

## L5 — Verifier freeze

Do not edit `scripts/verify_*` pass criteria. Failing check = fix the system or `BLOCK`. Escalate; do not weaken gates.

## L6 — Commit before deploy

Scoped dirty-guard per lane. Receipts committed in repo under `receipts/cloud/`. No deploy from uncommitted motor changes.

## L7 — Queue batch law

100 rows mandatory quota per tick when work exists. `IDLE_NO_WORK` when registry exhausted. No skip law (INCIDENT-044).

## L8 — Heartbeat daily

`receipts/cloud/autonomous-forge-run-heartbeat/heartbeat-YYYY-MM-DD-v1.json` — written by cloud motor, mirrored at `~/.sina/autonomous-forge-run-daily-heartbeat-v1.json`.

## L9 — Founder-blocked queue

`founder_blocked` items are surfaced, never processed, never cancelled. Count + oldest + age reported each session.

## L10 — BLOCKED_WITH_REASON gate

If any `BLOCKED_WITH_REASON` exists in the active window: fix or escalate before accepting new work.

## L11 — Cost meter every cycle

Meter on every cycle: `provider`, `tokens`, `USD`, `value_class`. Respect budget caps and `THROTTLED_ROI` — throttle when ROI class is below floor.

## L12 — Drift check in daily heartbeat

Daily heartbeat includes live hash vs committed drift check. Drift without receipt = BLOCK.

## Standing duties (each session)

1. Read latest heartbeat + last 3 cycle receipts. Report: loops, states, sink invariant, drift, cost window (5 lines).
2. Surface `founder_blocked` items (count, oldest, age). Never process or cancel.
3. If `BLOCKED_WITH_REASON` exists: fix or escalate before new work.

## Work rules

- One improvement per cycle, highest expected ROI, `machine_safe` only.
- `founder_gated` changes → weekly digest, untouched by loop specialist.
- Reports: fixed fields only — SHAs, receipt paths, counts before/after, cost table, dirty state, gate receipts with `{decision, reason, evidence}`.
- No narrative claims without command + output.

## Wired artifacts

| Artifact | Path |
|----------|------|
| Cloud runtime SSOT | `data/cloud-auto-runtime-v1.json` |
| Phase reconciler | `scripts/phase_reconciler_v1.py` |
| Autorun verifier | `scripts/verify_autorun_zero_manual_v1.py` |
| External verify Action | `.github/workflows/external-verify.yml` |
| Cycle receipts (repo) | `receipts/cloud/autonomous-forge-run-cycles/` |
| Heartbeat (repo) | `receipts/cloud/autonomous-forge-run-heartbeat/` |
| Cycle mirror (Mac) | `~/.sina/autonomous-forge-run-cycle-receipts/` |
| Loop specialist tick | `scripts/loop_specialist_tick_v1.py` |
| Controlled autorun skill | `.cursor/skills/controlled-autorun/SKILL.md` |
| Skill validator | `scripts/validate-controlled-autorun-skill-v1.sh` |
| Observer API | `https://sourcea-fbe-runner-production.up.railway.app/api/cloud-forge-run/observer/v1` |

## Out of scope

Sales copy · LinkedIn · product pages · NOOS repo · founder decisions.
